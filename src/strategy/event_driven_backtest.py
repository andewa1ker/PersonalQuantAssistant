"""
事件驱动回测引擎 - 支持停牌、涨跌停等真实市场情况
Event-Driven Backtest Engine with Market Constraints
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from loguru import logger

from .backtest_engine import (
    BacktestEngine, BacktestConfig, BacktestResult,
    Order, Trade, Position, OrderType, OrderSide, OrderStatus
)


class MarketStatus(Enum):
    """市场状态"""
    NORMAL = "normal"           # 正常交易
    HALTED = "halted"          # 停牌
    LIMIT_UP = "limit_up"      # 涨停
    LIMIT_DOWN = "limit_down"  # 跌停
    PRE_OPEN = "pre_open"      # 集合竞价
    CLOSED = "closed"          # 休市


@dataclass
class MarketEvent:
    """市场事件"""
    timestamp: datetime
    event_type: str             # 事件类型: price_update, order_fill, dividend, split等
    symbol: str
    data: Dict[str, Any]


@dataclass
class MarketConstraints:
    """市场约束"""
    # 涨跌停限制
    enable_price_limit: bool = True
    price_limit_pct: float = 0.10        # 涨跌停幅度 (A股10%)
    st_price_limit_pct: float = 0.05     # ST股涨跌停幅度 (A股5%)
    
    # 停牌
    enable_halt_check: bool = True
    halt_symbols: Dict[str, List[Tuple[datetime, datetime]]] = field(default_factory=dict)
    
    # 流动性限制
    enable_liquidity_check: bool = True
    max_volume_pct: float = 0.10         # 单笔最大成交量占比 (不超过当日成交量10%)
    min_volume: float = 100              # 最小成交量
    
    # 交易时间
    trading_hours: List[Tuple[str, str]] = field(
        default_factory=lambda: [("09:30", "11:30"), ("13:00", "15:00")]
    )
    
    # 其他
    enable_auction: bool = False         # 集合竞价 (简化实现)
    tick_size: float = 0.01              # 最小价格变动单位


class EventDrivenBacktestEngine(BacktestEngine):
    """事件驱动回测引擎"""
    
    def __init__(self,
                 config: Optional[BacktestConfig] = None,
                 constraints: Optional[MarketConstraints] = None):
        """
        初始化事件驱动回测引擎
        
        Args:
            config: 回测配置
            constraints: 市场约束
        """
        super().__init__(config)
        self.constraints = constraints or MarketConstraints()
        
        # 事件队列
        self.events: List[MarketEvent] = []
        
        # 市场状态
        self.market_status: Dict[str, MarketStatus] = {}
        
        # 价格限制
        self.price_limits: Dict[str, Tuple[float, float]] = {}  # {symbol: (lower, upper)}
        
        # 待执行订单队列 (停牌、涨跌停时订单排队)
        self.pending_orders: List[Order] = []
        
        logger.info("事件驱动回测引擎初始化完成")
    
    def run_backtest(self,
                    data: pd.DataFrame,
                    strategy_func: Callable,
                    **kwargs) -> BacktestResult:
        """
        运行事件驱动回测
        
        Args:
            data: 价格数据
            strategy_func: 策略函数
            **kwargs: 策略参数
            
        Returns:
            BacktestResult
        """
        logger.info("=" * 80)
        logger.info("开始事件驱动回测 (支持停牌、涨跌停等市场约束)")
        logger.info("=" * 80)
        
        try:
            # 数据验证
            if not self._validate_data(data):
                raise ValueError("数据验证失败")
            
            # 确保数据按时间排序
            data = data.sort_index()
            
            # 初始化
            self._reset()
            self._initialize_market_status(data)
            
            start_date = data.index[0]
            end_date = data.index[-1]
            
            logger.info(f"回测期间: {start_date} 至 {end_date}")
            logger.info(f"数据条数: {len(data)}")
            
            # 逐日回测
            prev_bar = None
            for i in range(len(data)):
                current_date = data.index[i]
                current_bar = data.iloc[i]
                
                # 更新市场状态
                self._update_market_status(current_date, current_bar, prev_bar)
                
                # 更新市场数据
                self._update_market_data(current_date, current_bar)
                
                # 检查停牌状态
                symbol = kwargs.get('symbol', 'unknown')
                if self._is_halted(symbol, current_date):
                    logger.debug(f"{current_date.date()} {symbol} 停牌，跳过")
                    self._record_equity(current_date)
                    prev_bar = current_bar
                    continue
                
                # 尝试执行待处理订单 (停牌恢复、涨跌停打开等)
                self._try_execute_pending_orders(current_bar)
                
                # 执行策略
                current_data = data.iloc[:i+1]
                context = self._create_strategy_context(current_date)
                signals = strategy_func(current_data, context, **kwargs)
                
                # 处理交易信号 (考虑市场约束)
                self._process_signals_with_constraints(signals, current_bar, symbol)
                
                # 记录权益
                self._record_equity(current_date)
                
                # 进度日志
                if (i + 1) % 50 == 0:
                    logger.debug(f"进度: {i+1}/{len(data)} | "
                               f"资金: {self.portfolio_value:,.2f} | "
                               f"收益率: {(self.portfolio_value/self.config.initial_capital-1)*100:.2f}%")
                
                prev_bar = current_bar
            
            # 计算回测结果
            result = self._calculate_results(start_date, end_date)
            
            # 添加事件驱动特有统计
            result = self._add_event_driven_stats(result)
            
            logger.info("=" * 80)
            logger.info("事件驱动回测完成")
            logger.info(f"总收益率: {result.total_return_pct:.2%}")
            logger.info(f"年化收益率: {result.annualized_return:.2%}")
            logger.info(f"最大回撤: {result.max_drawdown:.2%}")
            logger.info(f"夏普比率: {result.sharpe_ratio:.2f}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"事件驱动回测失败: {e}")
            raise
    
    def _initialize_market_status(self, data: pd.DataFrame):
        """初始化市场状态"""
        # 假设所有标的初始状态为正常交易
        for symbol in data.columns:
            self.market_status[symbol] = MarketStatus.NORMAL
    
    def _update_market_status(self,
                             date: datetime,
                             current_bar: pd.Series,
                             prev_bar: Optional[pd.Series]):
        """
        更新市场状态 (检测涨跌停、停牌等)
        
        Args:
            date: 当前日期
            current_bar: 当前K线
            prev_bar: 前一K线
        """
        if prev_bar is None:
            return
        
        symbol = 'unknown'  # 简化处理，实际应该从数据中获取
        
        # 检查涨跌停
        if self.constraints.enable_price_limit:
            prev_close = prev_bar.get('close', 0)
            current_close = current_bar.get('close', 0)
            
            if prev_close > 0:
                change_pct = (current_close - prev_close) / prev_close
                
                # 计算价格限制
                limit_pct = self.constraints.price_limit_pct
                upper_limit = prev_close * (1 + limit_pct)
                lower_limit = prev_close * (1 - limit_pct)
                
                self.price_limits[symbol] = (lower_limit, upper_limit)
                
                # 判断是否涨跌停
                if abs(current_close - upper_limit) < 0.01:
                    self.market_status[symbol] = MarketStatus.LIMIT_UP
                    logger.debug(f"{date.date()} {symbol} 涨停 @ {current_close:.2f}")
                elif abs(current_close - lower_limit) < 0.01:
                    self.market_status[symbol] = MarketStatus.LIMIT_DOWN
                    logger.debug(f"{date.date()} {symbol} 跌停 @ {current_close:.2f}")
                else:
                    self.market_status[symbol] = MarketStatus.NORMAL
        
        # 检查停牌 (从配置中获取)
        if self.constraints.enable_halt_check:
            if symbol in self.constraints.halt_symbols:
                for halt_start, halt_end in self.constraints.halt_symbols[symbol]:
                    if halt_start <= date <= halt_end:
                        self.market_status[symbol] = MarketStatus.HALTED
                        return
        
        # 检查成交量 (异常低成交量视为流动性不足)
        if self.constraints.enable_liquidity_check:
            volume = current_bar.get('volume', 0)
            if volume < self.constraints.min_volume:
                logger.warning(f"{date.date()} {symbol} 成交量过低: {volume}")
    
    def _is_halted(self, symbol: str, date: datetime) -> bool:
        """检查是否停牌"""
        return self.market_status.get(symbol, MarketStatus.NORMAL) == MarketStatus.HALTED
    
    def _is_limit_up(self, symbol: str) -> bool:
        """检查是否涨停"""
        return self.market_status.get(symbol, MarketStatus.NORMAL) == MarketStatus.LIMIT_UP
    
    def _is_limit_down(self, symbol: str) -> bool:
        """检查是否跌停"""
        return self.market_status.get(symbol, MarketStatus.NORMAL) == MarketStatus.LIMIT_DOWN
    
    def _check_liquidity(self, symbol: str, quantity: float, bar: pd.Series) -> bool:
        """
        检查流动性是否充足
        
        Args:
            symbol: 标的代码
            quantity: 交易数量
            bar: 当前K线
            
        Returns:
            是否有足够流动性
        """
        if not self.constraints.enable_liquidity_check:
            return True
        
        volume = bar.get('volume', 0)
        if volume == 0:
            return False
        
        # 检查是否超过最大成交量占比
        volume_pct = quantity / volume
        if volume_pct > self.constraints.max_volume_pct:
            logger.warning(f"{symbol} 交易量过大: {quantity} ({volume_pct:.1%} of volume)")
            return False
        
        return True
    
    def _process_signals_with_constraints(self,
                                         signals: Any,
                                         bar: pd.Series,
                                         symbol: str):
        """
        处理交易信号 (考虑市场约束)
        
        Args:
            signals: 交易信号
            bar: 当前K线
            symbol: 标的代码
        """
        if signals is None:
            return
        
        if not isinstance(signals, list):
            signals = [signals]
        
        for signal in signals:
            if isinstance(signal, dict):
                self._process_signal_with_constraints(signal, bar, symbol)
    
    def _process_signal_with_constraints(self,
                                        signal: Dict,
                                        bar: pd.Series,
                                        symbol: str):
        """处理单个信号 (考虑约束)"""
        action = signal.get('action', 'hold').lower()
        quantity = signal.get('quantity', 0)
        signal_symbol = signal.get('symbol', symbol)
        
        if action == 'hold' or quantity <= 0:
            return
        
        # 创建订单
        if action == 'buy':
            order = self.place_order(signal_symbol, OrderSide.BUY, quantity)
        elif action == 'sell':
            order = self.place_order(signal_symbol, OrderSide.SELL, quantity)
        else:
            return
        
        if order is None:
            return
        
        # 尝试执行订单
        success = self._execute_order_with_constraints(order, bar, signal_symbol)
        
        if not success:
            # 订单无法立即执行，加入待处理队列
            self.pending_orders.append(order)
            logger.debug(f"订单加入待处理队列: {order.side.value} {order.symbol} x{order.quantity}")
    
    def _execute_order_with_constraints(self,
                                       order: Order,
                                       bar: pd.Series,
                                       symbol: str) -> bool:
        """
        执行订单 (考虑市场约束)
        
        Args:
            order: 订单
            bar: 当前K线
            symbol: 标的代码
            
        Returns:
            是否成功执行
        """
        market_price = bar['close']
        
        # 1. 检查停牌
        if self._is_halted(symbol, bar.name):
            order.notes = "停牌，无法交易"
            logger.debug(f"订单失败: {order.notes}")
            return False
        
        # 2. 检查涨跌停
        if order.side == OrderSide.BUY:
            if self._is_limit_up(symbol):
                order.notes = "涨停板，买入困难"
                logger.debug(f"订单延迟: {order.notes}")
                return False  # 涨停时买入困难，加入待处理队列
        
        elif order.side == OrderSide.SELL:
            if self._is_limit_down(symbol):
                order.notes = "跌停板，卖出困难"
                logger.debug(f"订单延迟: {order.notes}")
                return False  # 跌停时卖出困难，加入待处理队列
        
        # 3. 检查流动性
        if not self._check_liquidity(symbol, order.quantity, bar):
            order.notes = "流动性不足"
            logger.warning(f"订单失败: {order.notes}")
            order.status = OrderStatus.REJECTED
            return False
        
        # 4. 检查价格限制
        if self.constraints.enable_price_limit and symbol in self.price_limits:
            lower, upper = self.price_limits[symbol]
            
            if market_price < lower:
                market_price = lower
                logger.debug(f"价格触及下限: {market_price:.2f}")
            elif market_price > upper:
                market_price = upper
                logger.debug(f"价格触及上限: {market_price:.2f}")
        
        # 5. 执行订单
        trade = self._execute_order(order, market_price)
        
        return trade is not None
    
    def _try_execute_pending_orders(self, bar: pd.Series):
        """尝试执行待处理订单"""
        if not self.pending_orders:
            return
        
        executed_orders = []
        
        for order in self.pending_orders:
            if order.status != OrderStatus.PENDING:
                executed_orders.append(order)
                continue
            
            # 尝试执行
            success = self._execute_order_with_constraints(order, bar, order.symbol)
            
            if success:
                executed_orders.append(order)
        
        # 移除已执行或已取消的订单
        for order in executed_orders:
            self.pending_orders.remove(order)
        
        if executed_orders:
            logger.debug(f"待处理订单执行: {len(executed_orders)}个")
    
    def _add_event_driven_stats(self, result: BacktestResult) -> BacktestResult:
        """添加事件驱动特有统计"""
        # 统计因市场约束导致的订单延迟/拒绝
        rejected_orders = [o for o in self.orders if o.status == OrderStatus.REJECTED]
        pending_orders_final = len(self.pending_orders)
        
        logger.info(f"被拒绝订单: {len(rejected_orders)}")
        logger.info(f"未完成订单: {pending_orders_final}")
        
        # 可以扩展result添加这些统计信息
        # result.rejected_orders = len(rejected_orders)
        # result.pending_orders = pending_orders_final
        
        return result
    
    def set_halt_period(self, symbol: str, start: datetime, end: datetime):
        """
        设置停牌期间
        
        Args:
            symbol: 标的代码
            start: 停牌开始日期
            end: 停牌结束日期
        """
        if symbol not in self.constraints.halt_symbols:
            self.constraints.halt_symbols[symbol] = []
        
        self.constraints.halt_symbols[symbol].append((start, end))
        logger.info(f"设置停牌: {symbol} 从 {start.date()} 至 {end.date()}")
    
    def get_market_status_summary(self) -> Dict:
        """获取市场状态摘要"""
        summary = {
            'market_status': self.market_status.copy(),
            'pending_orders': len(self.pending_orders),
            'price_limits': self.price_limits.copy()
        }
        return summary


# 便捷函数
def event_driven_backtest(data: pd.DataFrame,
                         strategy_func: Callable,
                         initial_capital: float = 100000,
                         enable_price_limit: bool = True,
                         enable_halt_check: bool = True,
                         enable_liquidity_check: bool = True,
                         **kwargs) -> BacktestResult:
    """
    快速事件驱动回测
    
    Args:
        data: OHLCV数据
        strategy_func: 策略函数
        initial_capital: 初始资金
        enable_price_limit: 启用涨跌停限制
        enable_halt_check: 启用停牌检查
        enable_liquidity_check: 启用流动性检查
        **kwargs: 其他参数
        
    Returns:
        BacktestResult
    """
    config = BacktestConfig(
        initial_capital=initial_capital,
        commission_rate=0.0003,
        slippage_rate=0.0005
    )
    
    constraints = MarketConstraints(
        enable_price_limit=enable_price_limit,
        enable_halt_check=enable_halt_check,
        enable_liquidity_check=enable_liquidity_check
    )
    
    engine = EventDrivenBacktestEngine(config, constraints)
    return engine.run_backtest(data, strategy_func, **kwargs)

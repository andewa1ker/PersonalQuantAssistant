"""
高级回测引擎 - 支持滑点、交易成本、真实市场模拟
Enhanced Backtest Engine with Slippage, Transaction Costs, and Market Reality
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from enum import Enum


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"           # 市价单
    LIMIT = "limit"             # 限价单
    STOP_LOSS = "stop_loss"     # 止损单
    STOP_LIMIT = "stop_limit"   # 止损限价单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"         # 待执行
    FILLED = "filled"           # 已成交
    PARTIAL = "partial"         # 部分成交
    CANCELLED = "cancelled"     # 已取消
    REJECTED = "rejected"       # 已拒绝


@dataclass
class Order:
    """订单"""
    order_id: str
    timestamp: datetime
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None           # 限价单价格
    stop_price: Optional[float] = None      # 止损价格
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0
    notes: str = ""


@dataclass
class Trade:
    """成交记录"""
    trade_id: str
    order_id: str
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    commission: float
    slippage: float
    total_cost: float  # 包含所有成本的总成本


@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0


@dataclass
class BacktestConfig:
    """回测配置"""
    # 初始资金
    initial_capital: float = 100000.0
    
    # 交易成本
    commission_rate: float = 0.0003         # 佣金费率 (0.03%)
    min_commission: float = 5.0             # 最低佣金
    stamp_duty: float = 0.001               # 印花税 (仅卖出, A股)
    slippage_rate: float = 0.0005           # 滑点率 (0.05%)
    
    # 市场规则
    enable_slippage: bool = True            # 启用滑点
    enable_commission: bool = True          # 启用佣金
    enable_stamp_duty: bool = False         # 启用印花税 (A股)
    
    # 风控规则
    max_position_pct: float = 0.95          # 最大仓位比例
    min_cash_reserve: float = 1000.0        # 最低现金储备
    allow_short: bool = False               # 允许做空
    
    # 市场限制
    price_tick: float = 0.01                # 最小价格变动单位
    lot_size: int = 100                     # 交易单位 (A股100股)
    
    # 其他
    benchmark: Optional[str] = None         # 基准指数


@dataclass
class BacktestResult:
    """回测结果"""
    # 基本信息
    start_date: str
    end_date: str
    total_days: int
    trading_days: int
    
    # 资金信息
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # 收益指标
    annualized_return: float
    daily_returns: pd.Series
    cumulative_returns: pd.Series
    
    # 风险指标
    volatility: float                       # 波动率
    sharpe_ratio: float                     # 夏普比率
    sortino_ratio: float                    # 索提诺比率
    max_drawdown: float                     # 最大回撤
    max_drawdown_duration: int              # 最大回撤持续天数
    
    # 交易统计
    total_trades: int                       # 总交易次数
    winning_trades: int                     # 盈利交易次数
    losing_trades: int                      # 亏损交易次数
    win_rate: float                         # 胜率
    avg_win: float                          # 平均盈利
    avg_loss: float                         # 平均亏损
    profit_factor: float                    # 盈亏比
    
    # 成本统计
    total_commission: float                 # 总佣金
    total_slippage: float                   # 总滑点成本
    total_stamp_duty: float                 # 总印花税
    
    # 持仓分析
    equity_curve: pd.Series                 # 资金曲线
    positions_history: List[Dict]           # 持仓历史
    trades_history: List[Trade]             # 交易历史
    
    # 额外信息
    benchmark_return: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None


class BacktestEngine:
    """高级回测引擎"""
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        初始化回测引擎
        
        Args:
            config: 回测配置
        """
        self.config = config or BacktestConfig()
        
        # 账户状态
        self.cash = self.config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.portfolio_value = self.config.initial_capital
        
        # 交易记录
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        
        # 统计信息
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.total_stamp_duty = 0.0
        
        logger.info(f"回测引擎初始化完成 | 初始资金: {self.config.initial_capital:,.2f}")
    
    def run_backtest(self,
                    data: pd.DataFrame,
                    strategy_func: Callable,
                    **kwargs) -> BacktestResult:
        """
        运行回测
        
        Args:
            data: 价格数据 (OHLCV格式)
            strategy_func: 策略函数 (接收data和context, 返回交易信号)
            **kwargs: 传递给策略函数的额外参数
            
        Returns:
            BacktestResult
        """
        logger.info("=" * 80)
        logger.info("开始回测")
        logger.info("=" * 80)
        
        try:
            # 数据验证
            if not self._validate_data(data):
                raise ValueError("数据验证失败")
            
            # 确保数据按时间排序
            data = data.sort_index()
            
            # 初始化
            self._reset()
            start_date = data.index[0]
            end_date = data.index[-1]
            
            logger.info(f"回测期间: {start_date} 至 {end_date}")
            logger.info(f"数据条数: {len(data)}")
            
            # 逐日回测
            for i in range(len(data)):
                current_date = data.index[i]
                current_bar = data.iloc[:i+1]  # 截至当前的所有数据
                
                # 更新市场数据
                self._update_market_data(current_date, data.iloc[i])
                
                # 执行策略
                context = self._create_strategy_context(current_date)
                signals = strategy_func(current_bar, context, **kwargs)
                
                # 处理交易信号
                self._process_signals(signals, data.iloc[i])
                
                # 记录权益
                self._record_equity(current_date)
                
                # 进度日志
                if (i + 1) % 50 == 0:
                    logger.debug(f"进度: {i+1}/{len(data)} | "
                               f"资金: {self.portfolio_value:,.2f} | "
                               f"收益率: {(self.portfolio_value/self.config.initial_capital-1)*100:.2f}%")
            
            # 计算回测结果
            result = self._calculate_results(start_date, end_date)
            
            logger.info("=" * 80)
            logger.info("回测完成")
            logger.info(f"总收益率: {result.total_return_pct:.2%}")
            logger.info(f"年化收益率: {result.annualized_return:.2%}")
            logger.info(f"最大回撤: {result.max_drawdown:.2%}")
            logger.info(f"夏普比率: {result.sharpe_ratio:.2f}")
            logger.info(f"总交易次数: {result.total_trades}")
            logger.info(f"胜率: {result.win_rate:.2%}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"回测失败: {e}")
            raise
    
    def place_order(self,
                   symbol: str,
                   side: OrderSide,
                   quantity: float,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Order:
        """
        下单
        
        Args:
            symbol: 资产代码
            side: 买卖方向
            quantity: 数量
            order_type: 订单类型
            price: 限价单价格
            stop_price: 止损价格
            
        Returns:
            Order
        """
        # 调整数量到交易单位
        quantity = self._round_to_lot_size(quantity)
        
        if quantity <= 0:
            logger.warning(f"无效的数量: {quantity}")
            return None
        
        # 创建订单
        order = Order(
            order_id=self._generate_order_id(),
            timestamp=datetime.now(),
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        self.orders.append(order)
        logger.debug(f"下单: {side.value} {symbol} x{quantity} @ {order_type.value}")
        
        return order
    
    def _execute_order(self, order: Order, market_price: float) -> Optional[Trade]:
        """
        执行订单
        
        Args:
            order: 订单
            market_price: 市场价格
            
        Returns:
            Trade 或 None
        """
        # 检查是否可以执行
        if order.status != OrderStatus.PENDING:
            return None
        
        # 根据订单类型确定成交价格
        execution_price = self._calculate_execution_price(
            order,
            market_price
        )
        
        if execution_price is None:
            return None
        
        # 计算滑点
        slippage_cost = 0.0
        if self.config.enable_slippage:
            slippage_cost = self._calculate_slippage(
                order.side,
                market_price,
                order.quantity
            )
            execution_price += slippage_cost
        
        # 计算佣金
        commission = 0.0
        if self.config.enable_commission:
            commission = self._calculate_commission(
                execution_price,
                order.quantity
            )
        
        # 计算印花税 (仅卖出)
        stamp_duty = 0.0
        if self.config.enable_stamp_duty and order.side == OrderSide.SELL:
            stamp_duty = execution_price * order.quantity * self.config.stamp_duty
        
        # 计算总成本
        if order.side == OrderSide.BUY:
            total_cost = execution_price * order.quantity + commission + stamp_duty
        else:
            total_cost = execution_price * order.quantity - commission - stamp_duty
        
        # 检查资金是否充足
        if order.side == OrderSide.BUY:
            if self.cash < total_cost:
                order.status = OrderStatus.REJECTED
                order.notes = f"资金不足: 需要 {total_cost:.2f}, 可用 {self.cash:.2f}"
                logger.warning(order.notes)
                return None
        
        # 执行交易
        trade = Trade(
            trade_id=self._generate_trade_id(),
            order_id=order.order_id,
            timestamp=order.timestamp,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            commission=commission,
            slippage=slippage_cost * order.quantity,
            total_cost=total_cost
        )
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.filled_price = execution_price
        order.commission = commission
        order.slippage = slippage_cost * order.quantity
        
        # 更新账户
        self._update_account(trade)
        
        # 记录
        self.trades.append(trade)
        self.total_commission += commission
        self.total_slippage += slippage_cost * order.quantity
        self.total_stamp_duty += stamp_duty
        
        logger.info(
            f"成交: {trade.side.value.upper()} {trade.symbol} "
            f"x{trade.quantity} @ {trade.price:.2f} | "
            f"佣金: {commission:.2f} | 滑点: {trade.slippage:.2f}"
        )
        
        return trade
    
    def _calculate_execution_price(self,
                                   order: Order,
                                   market_price: float) -> Optional[float]:
        """计算成交价格"""
        if order.order_type == OrderType.MARKET:
            return market_price
        
        elif order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY:
                # 买入限价单: 市场价格低于限价才成交
                if market_price <= order.price:
                    return min(market_price, order.price)
            else:
                # 卖出限价单: 市场价格高于限价才成交
                if market_price >= order.price:
                    return max(market_price, order.price)
            return None
        
        elif order.order_type == OrderType.STOP_LOSS:
            if order.side == OrderSide.SELL:
                # 止损单: 价格跌破止损价时按市价卖出
                if market_price <= order.stop_price:
                    return market_price
            return None
        
        return None
    
    def _calculate_slippage(self,
                           side: OrderSide,
                           price: float,
                           quantity: float) -> float:
        """
        计算滑点
        
        市价单会产生滑点:
        - 买入: 实际成交价高于市场价
        - 卖出: 实际成交价低于市场价
        """
        if not self.config.enable_slippage:
            return 0.0
        
        base_slippage = price * self.config.slippage_rate
        
        # 根据数量调整滑点 (大单滑点更大)
        volume_factor = 1.0 + np.log1p(quantity / 100)
        
        slippage = base_slippage * volume_factor
        
        if side == OrderSide.BUY:
            return slippage  # 买入价格上升
        else:
            return -slippage  # 卖出价格下降
    
    def _calculate_commission(self, price: float, quantity: float) -> float:
        """计算佣金"""
        if not self.config.enable_commission:
            return 0.0
        
        commission = price * quantity * self.config.commission_rate
        return max(commission, self.config.min_commission)
    
    def _update_account(self, trade: Trade):
        """更新账户状态"""
        if trade.side == OrderSide.BUY:
            # 买入: 增加持仓, 减少现金
            self.cash -= trade.total_cost
            
            if trade.symbol in self.positions:
                pos = self.positions[trade.symbol]
                total_cost = pos.avg_cost * pos.quantity + trade.price * trade.quantity
                pos.quantity += trade.quantity
                pos.avg_cost = total_cost / pos.quantity
            else:
                self.positions[trade.symbol] = Position(
                    symbol=trade.symbol,
                    quantity=trade.quantity,
                    avg_cost=trade.price
                )
        
        else:  # SELL
            # 卖出: 减少持仓, 增加现金
            self.cash += trade.total_cost
            
            if trade.symbol in self.positions:
                self.positions[trade.symbol].quantity -= trade.quantity
                
                # 清空持仓
                if self.positions[trade.symbol].quantity <= 0:
                    del self.positions[trade.symbol]
    
    def _update_market_data(self, date: datetime, bar: pd.Series):
        """更新市场数据"""
        # 更新持仓市值
        for symbol, pos in self.positions.items():
            if 'close' in bar:
                pos.current_price = bar['close']
                pos.market_value = pos.quantity * pos.current_price
                pos.unrealized_pnl = (pos.current_price - pos.avg_cost) * pos.quantity
                pos.unrealized_pnl_pct = (pos.current_price / pos.avg_cost - 1)
        
        # 更新组合价值
        total_position_value = sum(pos.market_value for pos in self.positions.values())
        self.portfolio_value = self.cash + total_position_value
    
    def _record_equity(self, date: datetime):
        """记录资金曲线"""
        self.equity_curve.append((date, self.portfolio_value))
    
    def _create_strategy_context(self, date: datetime) -> Dict:
        """创建策略上下文"""
        return {
            'cash': self.cash,
            'positions': self.positions.copy(),
            'portfolio_value': self.portfolio_value,
            'date': date,
            'engine': self
        }
    
    def _process_signals(self, signals: Any, bar: pd.Series):
        """处理交易信号"""
        if signals is None:
            return
        
        # 支持单个信号或信号列表
        if not isinstance(signals, list):
            signals = [signals]
        
        for signal in signals:
            if isinstance(signal, dict):
                self._process_signal_dict(signal, bar)
    
    def _process_signal_dict(self, signal: Dict, bar: pd.Series):
        """处理信号字典"""
        action = signal.get('action', 'hold').lower()
        symbol = signal.get('symbol', 'unknown')
        quantity = signal.get('quantity', 0)
        
        if action == 'buy' and quantity > 0:
            order = self.place_order(symbol, OrderSide.BUY, quantity)
            if order:
                self._execute_order(order, bar['close'])
        
        elif action == 'sell' and quantity > 0:
            order = self.place_order(symbol, OrderSide.SELL, quantity)
            if order:
                self._execute_order(order, bar['close'])
    
    def _calculate_results(self,
                          start_date: datetime,
                          end_date: datetime) -> BacktestResult:
        """计算回测结果"""
        # 转换资金曲线为Series
        dates, values = zip(*self.equity_curve) if self.equity_curve else ([], [])
        equity_series = pd.Series(values, index=dates)
        
        # 计算日收益率
        daily_returns = equity_series.pct_change().fillna(0)
        cumulative_returns = (1 + daily_returns).cumprod() - 1
        
        # 总收益
        total_return = self.portfolio_value - self.config.initial_capital
        total_return_pct = total_return / self.config.initial_capital
        
        # 年化收益率
        total_days = (end_date - start_date).days
        trading_days = len(equity_series)
        years = trading_days / 252
        annualized_return = (1 + total_return_pct) ** (1 / years) - 1 if years > 0 else 0
        
        # 波动率
        volatility = daily_returns.std() * np.sqrt(252)
        
        # 夏普比率
        risk_free_rate = self.config.benchmark or 0.03
        excess_return = annualized_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # 索提诺比率 (仅考虑下行波动)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino_ratio = excess_return / downside_std if downside_std > 0 else 0
        
        # 最大回撤
        max_drawdown, max_dd_duration = self._calculate_max_drawdown(equity_series)
        
        # 交易统计
        trade_stats = self._calculate_trade_statistics()
        
        return BacktestResult(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            total_days=total_days,
            trading_days=trading_days,
            initial_capital=self.config.initial_capital,
            final_capital=self.portfolio_value,
            total_return=total_return,
            total_return_pct=total_return_pct,
            annualized_return=annualized_return,
            daily_returns=daily_returns,
            cumulative_returns=cumulative_returns,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            total_trades=trade_stats['total_trades'],
            winning_trades=trade_stats['winning_trades'],
            losing_trades=trade_stats['losing_trades'],
            win_rate=trade_stats['win_rate'],
            avg_win=trade_stats['avg_win'],
            avg_loss=trade_stats['avg_loss'],
            profit_factor=trade_stats['profit_factor'],
            total_commission=self.total_commission,
            total_slippage=self.total_slippage,
            total_stamp_duty=self.total_stamp_duty,
            equity_curve=equity_series,
            positions_history=[],
            trades_history=self.trades
        )
    
    def _calculate_max_drawdown(self, equity: pd.Series) -> Tuple[float, int]:
        """计算最大回撤和持续时间"""
        if len(equity) == 0:
            return 0.0, 0
        
        # 计算累计最高点
        cummax = equity.expanding().max()
        
        # 计算回撤
        drawdown = (equity - cummax) / cummax
        
        # 最大回撤
        max_dd = drawdown.min()
        
        # 最大回撤持续时间
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.astype(int).groupby(
            (is_drawdown != is_drawdown.shift()).cumsum()
        ).sum()
        max_dd_duration = drawdown_periods.max() if len(drawdown_periods) > 0 else 0
        
        return abs(max_dd), int(max_dd_duration)
    
    def _calculate_trade_statistics(self) -> Dict:
        """计算交易统计"""
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }
        
        # 配对买卖交易计算盈亏
        buy_trades = [t for t in self.trades if t.side == OrderSide.BUY]
        sell_trades = [t for t in self.trades if t.side == OrderSide.SELL]
        
        wins = []
        losses = []
        
        # 简单配对法 (按FIFO)
        for sell in sell_trades:
            for buy in buy_trades:
                if buy.symbol == sell.symbol:
                    pnl = (sell.price - buy.price) * min(buy.quantity, sell.quantity)
                    if pnl > 0:
                        wins.append(pnl)
                    elif pnl < 0:
                        losses.append(abs(pnl))
                    break
        
        total_trades = len(wins) + len(losses)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        
        total_win = sum(wins)
        total_loss = sum(losses)
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_columns if col not in data.columns]
        
        if missing:
            logger.error(f"数据缺少必需的列: {missing}")
            return False
        
        if len(data) == 0:
            logger.error("数据为空")
            return False
        
        return True
    
    def _reset(self):
        """重置引擎状态"""
        self.cash = self.config.initial_capital
        self.positions = {}
        self.portfolio_value = self.config.initial_capital
        self.orders = []
        self.trades = []
        self.equity_curve = []
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.total_stamp_duty = 0.0
    
    def _round_to_lot_size(self, quantity: float) -> float:
        """调整到交易单位"""
        return round(quantity / self.config.lot_size) * self.config.lot_size
    
    def _generate_order_id(self) -> str:
        """生成订单ID"""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.orders):04d}"
    
    def _generate_trade_id(self) -> str:
        """生成交易ID"""
        return f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.trades):04d}"
    
    def get_summary(self) -> str:
        """获取摘要"""
        summary = []
        summary.append("=" * 60)
        summary.append("回测引擎状态")
        summary.append("=" * 60)
        summary.append(f"现金: {self.cash:,.2f}")
        summary.append(f"持仓数量: {len(self.positions)}")
        summary.append(f"组合价值: {self.portfolio_value:,.2f}")
        summary.append(f"总收益: {self.portfolio_value - self.config.initial_capital:,.2f}")
        summary.append(f"收益率: {(self.portfolio_value/self.config.initial_capital-1)*100:.2f}%")
        summary.append(f"总交易次数: {len(self.trades)}")
        summary.append(f"总佣金: {self.total_commission:.2f}")
        summary.append(f"总滑点成本: {self.total_slippage:.2f}")
        summary.append("=" * 60)
        
        return "\n".join(summary)


# 便捷函数
def quick_backtest(data: pd.DataFrame,
                  strategy_func: Callable,
                  initial_capital: float = 100000,
                  commission_rate: float = 0.0003,
                  slippage_rate: float = 0.0005,
                  **kwargs) -> BacktestResult:
    """
    快速回测
    
    Args:
        data: OHLCV数据
        strategy_func: 策略函数
        initial_capital: 初始资金
        commission_rate: 佣金率
        slippage_rate: 滑点率
        **kwargs: 其他参数
        
    Returns:
        BacktestResult
    """
    config = BacktestConfig(
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        slippage_rate=slippage_rate
    )
    
    engine = BacktestEngine(config)
    return engine.run_backtest(data, strategy_func, **kwargs)

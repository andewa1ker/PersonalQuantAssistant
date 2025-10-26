"""
定投策略（DCA - Dollar Cost Averaging）
实现智能定投、估值定投和网格交易
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from .base_strategy import BaseStrategy, StrategyResult


class DCAStrategy(BaseStrategy):
    """定投策略"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化定投策略
        
        配置参数:
            base_amount: 基础定投金额 (默认: 1000)
            frequency: 定投频率，天数 (默认: 7, 即每周)
            dca_type: 定投类型
                - fixed: 固定金额定投
                - smart: 智能定投（基于估值调整）
                - grid: 网格定投
            valuation_factor: 估值调整因子 (默认: 0.5)
            grid_levels: 网格层数 (默认: 5)
            grid_spacing: 网格间距百分比 (默认: 0.05)
        """
        super().__init__(config)
        
        # 配置参数
        self.base_amount = self.get_config_value('base_amount', 1000)
        self.frequency = self.get_config_value('frequency', 7)
        self.dca_type = self.get_config_value('dca_type', 'smart')
        self.valuation_factor = self.get_config_value('valuation_factor', 0.5)
        self.grid_levels = self.get_config_value('grid_levels', 5)
        self.grid_spacing = self.get_config_value('grid_spacing', 0.05)
        
        # 定投记录
        self.dca_history: List[Dict] = []
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> StrategyResult:
        """
        分析并生成定投建议
        
        Args:
            data: 价格数据
            **kwargs: 其他参数
                asset_symbol: 资产标识
                last_dca_date: 上次定投日期
                valuation_percentile: 估值百分位（用于智能定投）
                
        Returns:
            StrategyResult
        """
        try:
            asset_symbol = kwargs.get('asset_symbol', 'Unknown')
            last_dca_date = kwargs.get('last_dca_date', None)
            valuation_percentile = kwargs.get('valuation_percentile', None)
            
            # 验证数据
            if not self.validate_data(data, ['close']):
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=0.0,
                    reason="数据不完整"
                )
            
            current_price = float(data['close'].iloc[-1])
            
            # 检查是否到了定投时间
            should_invest, days_since_last = self._check_investment_timing(last_dca_date)
            
            if not should_invest:
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=current_price,
                    reason=f"距离上次定投仅{days_since_last}天，未到定投时间"
                )
            
            # 根据类型生成定投计划
            if self.dca_type == 'fixed':
                dca_plan = self._fixed_dca(current_price)
            elif self.dca_type == 'smart':
                dca_plan = self._smart_dca(current_price, valuation_percentile)
            elif self.dca_type == 'grid':
                dca_plan = self._grid_dca(current_price, data)
            else:
                logger.warning(f"未知的定投类型: {self.dca_type}, 使用固定定投")
                dca_plan = self._fixed_dca(current_price)
            
            # 创建结果
            result = StrategyResult(
                strategy_name=self.name,
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                action='buy',
                quantity=dca_plan['quantity'],
                confidence=dca_plan['confidence'],
                current_price=current_price,
                target_price=None,
                stop_loss=None,
                take_profit=None,
                reason=dca_plan['reason'],
                indicators={
                    'dca_type': self.dca_type,
                    'invest_amount': dca_plan['amount'],
                    'base_amount': self.base_amount,
                    'adjustment_factor': dca_plan.get('adjustment_factor', 1.0),
                    'days_since_last': days_since_last
                },
                risk_level='low',  # 定投策略风险较低
                holding_period=365,  # 建议长期持有
                notes=dca_plan.get('notes', None)
            )
            
            # 记录定投
            self._record_dca(result)
            self.log_strategy_action(result)
            
            return result
            
        except Exception as e:
            logger.error(f"定投策略分析失败: {e}")
            return self.create_hold_result(
                asset_symbol=kwargs.get('asset_symbol', 'Unknown'),
                current_price=0.0,
                reason=f"分析出错: {str(e)}"
            )
    
    def _check_investment_timing(self, last_dca_date: Optional[str]) -> tuple:
        """
        检查是否到了定投时间
        
        Returns:
            (should_invest, days_since_last)
        """
        try:
            if last_dca_date is None:
                return True, 0
            
            last_date = datetime.strptime(last_dca_date, '%Y-%m-%d')
            current_date = datetime.now()
            days_since_last = (current_date - last_date).days
            
            should_invest = days_since_last >= self.frequency
            
            return should_invest, days_since_last
            
        except Exception as e:
            logger.error(f"检查定投时间失败: {e}")
            return True, 0
    
    def _fixed_dca(self, current_price: float) -> Dict:
        """固定金额定投"""
        try:
            amount = self.base_amount
            quantity = amount / current_price
            
            return {
                'amount': amount,
                'quantity': quantity,
                'confidence': 0.9,
                'reason': f"固定定投{amount}元",
                'adjustment_factor': 1.0
            }
            
        except Exception as e:
            logger.error(f"固定定投计算失败: {e}")
            return {
                'amount': 0,
                'quantity': 0,
                'confidence': 0,
                'reason': f"计算出错: {str(e)}"
            }
    
    def _smart_dca(self,
                   current_price: float,
                   valuation_percentile: Optional[float]) -> Dict:
        """
        智能定投（基于估值调整投入金额）
        
        估值越低，投入越多；估值越高，投入越少
        """
        try:
            if valuation_percentile is None:
                logger.warning("缺少估值数据，使用固定定投")
                return self._fixed_dca(current_price)
            
            # 计算调整因子
            # 估值在0-30分位：多投（1.5x-2x）
            # 估值在30-70分位：正常投（1x）
            # 估值在70-100分位：少投（0.5x-0x）
            
            if valuation_percentile < 20:
                adjustment_factor = 2.0
                reason_detail = "极度低估"
            elif valuation_percentile < 30:
                adjustment_factor = 1.5
                reason_detail = "低估"
            elif valuation_percentile < 70:
                adjustment_factor = 1.0
                reason_detail = "合理估值"
            elif valuation_percentile < 80:
                adjustment_factor = 0.5
                reason_detail = "高估"
            else:
                adjustment_factor = 0.2
                reason_detail = "极度高估"
            
            # 应用调整因子
            amount = self.base_amount * adjustment_factor
            quantity = amount / current_price
            
            confidence = 0.8 if adjustment_factor >= 1.0 else 0.5
            
            return {
                'amount': amount,
                'quantity': quantity,
                'confidence': confidence,
                'reason': f"智能定投{amount:.2f}元 ({reason_detail}, 估值{valuation_percentile:.1f}分位)",
                'adjustment_factor': adjustment_factor
            }
            
        except Exception as e:
            logger.error(f"智能定投计算失败: {e}")
            return self._fixed_dca(current_price)
    
    def _grid_dca(self, current_price: float, data: pd.DataFrame) -> Dict:
        """
        网格定投
        
        在价格下跌到特定网格时加大投入
        """
        try:
            # 计算价格网格
            recent_high = float(data['close'].tail(60).max())
            
            # 从最高价开始，每下跌grid_spacing%设置一个网格
            grids = []
            for i in range(self.grid_levels):
                grid_price = recent_high * (1 - self.grid_spacing * (i + 1))
                grids.append(grid_price)
            
            # 找到当前价格在哪个网格
            grid_level = 0
            for i, grid_price in enumerate(grids):
                if current_price <= grid_price:
                    grid_level = i + 1
            
            # 根据网格等级调整投入
            # 网格越低（价格越便宜），投入越多
            if grid_level == 0:
                adjustment_factor = 1.0
                reason_detail = "价格正常"
            else:
                adjustment_factor = 1.0 + grid_level * 0.5
                reason_detail = f"价格下跌至网格{grid_level}"
            
            amount = self.base_amount * adjustment_factor
            quantity = amount / current_price
            
            # 生成网格信息
            grid_info = "\n".join([
                f"网格{i+1}: {grid:.2f}元"
                for i, grid in enumerate(grids[:3])  # 只显示前3个网格
            ])
            
            return {
                'amount': amount,
                'quantity': quantity,
                'confidence': 0.85,
                'reason': f"网格定投{amount:.2f}元 ({reason_detail})",
                'adjustment_factor': adjustment_factor,
                'notes': f"价格网格：\n{grid_info}\n当前网格等级：{grid_level}"
            }
            
        except Exception as e:
            logger.error(f"网格定投计算失败: {e}")
            return self._fixed_dca(current_price)
    
    def _record_dca(self, result: StrategyResult):
        """记录定投操作"""
        try:
            record = {
                'timestamp': result.timestamp,
                'asset': result.asset_symbol,
                'price': result.current_price,
                'quantity': result.quantity,
                'amount': result.indicators['invest_amount'],
                'type': self.dca_type
            }
            self.dca_history.append(record)
            
            # 只保留最近100条记录
            if len(self.dca_history) > 100:
                self.dca_history = self.dca_history[-100:]
                
        except Exception as e:
            logger.error(f"记录定投失败: {e}")
    
    def calculate_position_size(self,
                               capital: float,
                               current_price: float,
                               risk_per_trade: float = 0.02) -> float:
        """
        定投策略使用固定金额，不基于资本计算仓位
        """
        return self.base_amount / current_price
    
    def get_dca_statistics(self) -> Optional[Dict]:
        """获取定投统计数据"""
        try:
            if not self.dca_history:
                return None
            
            df = pd.DataFrame(self.dca_history)
            
            # 计算统计指标
            total_invested = df['amount'].sum()
            total_quantity = df['quantity'].sum()
            avg_price = total_invested / total_quantity if total_quantity > 0 else 0
            
            current_price = df['price'].iloc[-1]
            current_value = total_quantity * current_price
            profit = current_value - total_invested
            profit_rate = profit / total_invested * 100 if total_invested > 0 else 0
            
            return {
                'total_invested': total_invested,
                'total_quantity': total_quantity,
                'avg_price': avg_price,
                'current_price': current_price,
                'current_value': current_value,
                'profit': profit,
                'profit_rate': profit_rate,
                'num_investments': len(df),
                'first_date': df['timestamp'].iloc[0],
                'last_date': df['timestamp'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"计算定投统计失败: {e}")
            return None
    
    def simulate_dca(self,
                    data: pd.DataFrame,
                    start_date: str,
                    end_date: str) -> Dict:
        """
        模拟定投回测
        
        Args:
            data: 历史价格数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        try:
            # 筛选日期范围
            mask = (data.index >= start_date) & (data.index <= end_date)
            backtest_data = data[mask].copy()
            
            if backtest_data.empty:
                logger.warning("回测数据为空")
                return {}
            
            # 模拟定投
            investments = []
            last_date = None
            
            for date, row in backtest_data.iterrows():
                # 检查是否到定投时间
                if last_date is None:
                    should_invest = True
                else:
                    days_diff = (date - last_date).days
                    should_invest = days_diff >= self.frequency
                
                if should_invest:
                    price = row['close']
                    quantity = self.base_amount / price
                    
                    investments.append({
                        'date': date,
                        'price': price,
                        'quantity': quantity,
                        'amount': self.base_amount
                    })
                    
                    last_date = date
            
            if not investments:
                return {}
            
            # 计算收益
            df_invest = pd.DataFrame(investments)
            total_invested = df_invest['amount'].sum()
            total_quantity = df_invest['quantity'].sum()
            avg_price = total_invested / total_quantity
            
            final_price = backtest_data['close'].iloc[-1]
            final_value = total_quantity * final_price
            profit = final_value - total_invested
            profit_rate = profit / total_invested * 100
            
            return {
                'total_invested': total_invested,
                'total_quantity': total_quantity,
                'avg_price': avg_price,
                'final_price': final_price,
                'final_value': final_value,
                'profit': profit,
                'profit_rate': profit_rate,
                'num_investments': len(investments),
                'investments': investments
            }
            
        except Exception as e:
            logger.error(f"定投回测失败: {e}")
            return {}

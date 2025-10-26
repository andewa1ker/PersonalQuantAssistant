"""
ETF估值策略
基于格雷厄姆价值投资理论，通过PE/PB百分位分析判断估值水平
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_strategy import BaseStrategy, StrategyResult


class ETFValuationStrategy(BaseStrategy):
    """ETF估值策略"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化ETF估值策略
        
        配置参数:
            pe_lookback_days: PE历史回溯天数 (默认: 252*3 = 3年)
            pb_lookback_days: PB历史回溯天数 (默认: 252*3 = 3年)
            buy_percentile: 买入百分位阈值 (默认: 30)
            sell_percentile: 卖出百分位阈值 (默认: 70)
            min_data_points: 最少数据点数量 (默认: 100)
        """
        super().__init__(config)
        
        # 配置参数
        self.pe_lookback_days = self.get_config_value('pe_lookback_days', 252 * 3)
        self.pb_lookback_days = self.get_config_value('pb_lookback_days', 252 * 3)
        self.buy_percentile = self.get_config_value('buy_percentile', 30)
        self.sell_percentile = self.get_config_value('sell_percentile', 70)
        self.min_data_points = self.get_config_value('min_data_points', 100)
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> StrategyResult:
        """
        分析ETF估值并生成策略结果
        
        Args:
            data: 包含价格和估值指标的DataFrame
                 必需列: close, pe (可选), pb (可选)
            **kwargs: 其他参数
                asset_symbol: 资产标识
                capital: 可用资金
                
        Returns:
            StrategyResult
        """
        try:
            asset_symbol = kwargs.get('asset_symbol', 'Unknown')
            capital = kwargs.get('capital', 100000)
            
            # 验证数据
            if not self.validate_data(data, ['close']):
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=0.0,
                    reason="数据不完整"
                )
            
            current_price = float(data['close'].iloc[-1])
            
            # 计算估值指标
            valuation_metrics = self._calculate_valuation_metrics(data)
            
            if not valuation_metrics['has_valid_data']:
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=current_price,
                    reason="估值数据不足"
                )
            
            # 生成交易信号
            action, confidence, reason = self._generate_signal(valuation_metrics)
            
            # 计算仓位大小
            quantity = 0.0
            if action == 'buy':
                quantity = self.calculate_position_size(
                    capital=capital,
                    current_price=current_price,
                    risk_per_trade=0.02
                )
            
            # 计算价格目标
            target_price, stop_loss = self._calculate_price_targets(
                current_price=current_price,
                action=action,
                valuation_metrics=valuation_metrics
            )
            
            # 评估风险等级
            risk_level = self._assess_risk_level(valuation_metrics)
            
            # 创建结果
            result = StrategyResult(
                strategy_name=self.name,
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                action=action,
                quantity=quantity,
                confidence=confidence,
                current_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                take_profit=None,
                reason=reason,
                indicators=valuation_metrics,
                risk_level=risk_level,
                expected_return=self._estimate_return(valuation_metrics),
                holding_period=90  # 建议持有3个月
            )
            
            self.log_strategy_action(result)
            return result
            
        except Exception as e:
            logger.error(f"ETF估值分析失败: {e}")
            return self.create_hold_result(
                asset_symbol=kwargs.get('asset_symbol', 'Unknown'),
                current_price=0.0,
                reason=f"分析出错: {str(e)}"
            )
    
    def _calculate_valuation_metrics(self, data: pd.DataFrame) -> Dict:
        """计算估值指标"""
        metrics = {
            'has_valid_data': False,
            'pe_current': None,
            'pe_percentile': None,
            'pe_mean': None,
            'pe_std': None,
            'pb_current': None,
            'pb_percentile': None,
            'pb_mean': None,
            'pb_std': None,
            'price_percentile': None
        }
        
        try:
            # PE分析
            if 'pe' in data.columns:
                pe_data = data['pe'].dropna()
                if len(pe_data) >= self.min_data_points:
                    pe_current = float(pe_data.iloc[-1])
                    # 过滤异常值（PE在0-100之间）
                    pe_valid = pe_data[(pe_data > 0) & (pe_data < 100)]
                    
                    if len(pe_valid) >= self.min_data_points:
                        metrics['pe_current'] = pe_current
                        metrics['pe_percentile'] = self._calculate_percentile(
                            pe_valid, pe_current
                        )
                        metrics['pe_mean'] = float(pe_valid.mean())
                        metrics['pe_std'] = float(pe_valid.std())
                        metrics['has_valid_data'] = True
            
            # PB分析
            if 'pb' in data.columns:
                pb_data = data['pb'].dropna()
                if len(pb_data) >= self.min_data_points:
                    pb_current = float(pb_data.iloc[-1])
                    # 过滤异常值（PB在0-10之间）
                    pb_valid = pb_data[(pb_data > 0) & (pb_data < 10)]
                    
                    if len(pb_valid) >= self.min_data_points:
                        metrics['pb_current'] = pb_current
                        metrics['pb_percentile'] = self._calculate_percentile(
                            pb_valid, pb_current
                        )
                        metrics['pb_mean'] = float(pb_valid.mean())
                        metrics['pb_std'] = float(pb_valid.std())
                        metrics['has_valid_data'] = True
            
            # 价格百分位
            price_data = data['close'].dropna()
            if len(price_data) >= self.min_data_points:
                current_price = float(price_data.iloc[-1])
                metrics['price_percentile'] = self._calculate_percentile(
                    price_data, current_price
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算估值指标失败: {e}")
            return metrics
    
    def _calculate_percentile(self, data: pd.Series, value: float) -> float:
        """计算百分位"""
        try:
            # 计算小于当前值的数据点比例
            percentile = (data < value).sum() / len(data) * 100
            return float(percentile)
        except Exception as e:
            logger.error(f"计算百分位失败: {e}")
            return 50.0
    
    def _generate_signal(self, metrics: Dict) -> tuple:
        """
        生成交易信号
        
        Returns:
            (action, confidence, reason)
        """
        try:
            signals = []
            reasons = []
            
            # PE信号
            if metrics['pe_percentile'] is not None:
                pe_pct = metrics['pe_percentile']
                if pe_pct < self.buy_percentile:
                    signals.append('buy')
                    reasons.append(f"PE处于{pe_pct:.1f}分位（低估值）")
                elif pe_pct > self.sell_percentile:
                    signals.append('sell')
                    reasons.append(f"PE处于{pe_pct:.1f}分位（高估值）")
            
            # PB信号
            if metrics['pb_percentile'] is not None:
                pb_pct = metrics['pb_percentile']
                if pb_pct < self.buy_percentile:
                    signals.append('buy')
                    reasons.append(f"PB处于{pb_pct:.1f}分位（低估值）")
                elif pb_pct > self.sell_percentile:
                    signals.append('sell')
                    reasons.append(f"PB处于{pb_pct:.1f}分位（高估值）")
            
            # 价格百分位辅助判断
            if metrics['price_percentile'] is not None:
                price_pct = metrics['price_percentile']
                if price_pct < 20:
                    reasons.append(f"价格处于近期低位（{price_pct:.1f}分位）")
                elif price_pct > 80:
                    reasons.append(f"价格处于近期高位（{price_pct:.1f}分位）")
            
            # 综合判断
            if not signals:
                return 'hold', 0.0, "估值处于合理区间"
            
            buy_count = signals.count('buy')
            sell_count = signals.count('sell')
            
            if buy_count > sell_count:
                confidence = min(0.9, 0.5 + buy_count * 0.2)
                return 'buy', confidence, "; ".join(reasons)
            elif sell_count > buy_count:
                confidence = min(0.9, 0.5 + sell_count * 0.2)
                return 'sell', confidence, "; ".join(reasons)
            else:
                return 'hold', 0.3, "估值信号混合，建议观望"
                
        except Exception as e:
            logger.error(f"生成信号失败: {e}")
            return 'hold', 0.0, f"信号生成出错: {str(e)}"
    
    def _calculate_price_targets(self,
                                 current_price: float,
                                 action: str,
                                 valuation_metrics: Dict) -> tuple:
        """
        计算价格目标
        
        Returns:
            (target_price, stop_loss)
        """
        try:
            if action == 'buy':
                # 目标价格：基于均值回归
                if valuation_metrics['pe_mean'] and valuation_metrics['pe_current']:
                    pe_ratio = valuation_metrics['pe_mean'] / valuation_metrics['pe_current']
                    target_price = current_price * pe_ratio
                else:
                    target_price = current_price * 1.15  # 默认15%收益目标
                
                # 止损：-8%
                stop_loss = current_price * 0.92
                
            elif action == 'sell':
                target_price = None  # 卖出不设目标价
                stop_loss = None
            else:
                target_price = None
                stop_loss = None
            
            return target_price, stop_loss
            
        except Exception as e:
            logger.error(f"计算价格目标失败: {e}")
            return None, None
    
    def _assess_risk_level(self, metrics: Dict) -> str:
        """评估风险等级"""
        try:
            # 基于估值的极端程度评估风险
            risk_scores = []
            
            if metrics['pe_percentile'] is not None:
                pe_pct = metrics['pe_percentile']
                if pe_pct < 10 or pe_pct > 90:
                    risk_scores.append(2)  # 高风险
                elif pe_pct < 30 or pe_pct > 70:
                    risk_scores.append(1)  # 中风险
                else:
                    risk_scores.append(0)  # 低风险
            
            if metrics['pb_percentile'] is not None:
                pb_pct = metrics['pb_percentile']
                if pb_pct < 10 or pb_pct > 90:
                    risk_scores.append(2)
                elif pb_pct < 30 or pb_pct > 70:
                    risk_scores.append(1)
                else:
                    risk_scores.append(0)
            
            if not risk_scores:
                return 'medium'
            
            avg_risk = sum(risk_scores) / len(risk_scores)
            
            if avg_risk >= 1.5:
                return 'high'
            elif avg_risk >= 0.5:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"评估风险等级失败: {e}")
            return 'medium'
    
    def _estimate_return(self, metrics: Dict) -> Optional[float]:
        """估算预期收益率"""
        try:
            if metrics['pe_percentile'] is not None:
                pe_pct = metrics['pe_percentile']
                # 低估值区域预期更高收益
                if pe_pct < 20:
                    return 0.20  # 20%
                elif pe_pct < 30:
                    return 0.15  # 15%
                elif pe_pct > 80:
                    return -0.10  # -10%
                elif pe_pct > 70:
                    return -0.05  # -5%
            
            return 0.08  # 默认8%
            
        except Exception as e:
            logger.error(f"估算收益率失败: {e}")
            return None
    
    def calculate_position_size(self,
                               capital: float,
                               current_price: float,
                               risk_per_trade: float = 0.02) -> float:
        """
        计算仓位大小
        
        ETF策略使用固定比例仓位
        
        Args:
            capital: 可用资金
            current_price: 当前价格
            risk_per_trade: 单笔风险比例（ETF策略中代表最大仓位比例）
            
        Returns:
            建议购买数量
        """
        try:
            if current_price <= 0:
                return 0.0
            
            # ETF策略使用保守的仓位管理
            # 每次最多投入20%资金
            max_position_value = capital * 0.20
            quantity = max_position_value / current_price
            
            # 向下取整到100的倍数（ETF通常以100为单位交易）
            quantity = int(quantity / 100) * 100
            
            return float(quantity)
            
        except Exception as e:
            logger.error(f"计算仓位大小失败: {e}")
            return 0.0

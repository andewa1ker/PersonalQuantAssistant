"""
加密货币动量策略
基于趋势跟踪和动量指标的加密货币交易策略
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_strategy import BaseStrategy, StrategyResult


class CryptoMomentumStrategy(BaseStrategy):
    """加密货币动量策略"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化加密货币动量策略
        
        配置参数:
            ma_fast: 快速均线周期 (默认: 10)
            ma_slow: 慢速均线周期 (默认: 30)
            rsi_period: RSI周期 (默认: 14)
            rsi_oversold: RSI超卖阈值 (默认: 30)
            rsi_overbought: RSI超买阈值 (默认: 70)
            volume_ma_period: 成交量均线周期 (默认: 20)
            volume_surge_factor: 成交量激增因子 (默认: 2.0)
            atr_period: ATR周期 (默认: 14)
            atr_multiplier: ATR止损倍数 (默认: 2.0)
        """
        super().__init__(config)
        
        # 配置参数
        self.ma_fast = self.get_config_value('ma_fast', 10)
        self.ma_slow = self.get_config_value('ma_slow', 30)
        self.rsi_period = self.get_config_value('rsi_period', 14)
        self.rsi_oversold = self.get_config_value('rsi_oversold', 30)
        self.rsi_overbought = self.get_config_value('rsi_overbought', 70)
        self.volume_ma_period = self.get_config_value('volume_ma_period', 20)
        self.volume_surge_factor = self.get_config_value('volume_surge_factor', 2.0)
        self.atr_period = self.get_config_value('atr_period', 14)
        self.atr_multiplier = self.get_config_value('atr_multiplier', 2.0)
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> StrategyResult:
        """
        分析加密货币动量并生成策略结果
        
        Args:
            data: 包含OHLCV数据的DataFrame
                 必需列: open, high, low, close, volume
            **kwargs: 其他参数
                asset_symbol: 资产标识
                capital: 可用资金
                
        Returns:
            StrategyResult
        """
        try:
            asset_symbol = kwargs.get('asset_symbol', 'Unknown')
            capital = kwargs.get('capital', 10000)
            
            # 验证数据
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not self.validate_data(data, required_columns):
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=0.0,
                    reason="数据不完整"
                )
            
            # 计算技术指标
            indicators = self._calculate_indicators(data)
            
            if not indicators['valid']:
                return self.create_hold_result(
                    asset_symbol=asset_symbol,
                    current_price=float(data['close'].iloc[-1]),
                    reason="指标计算失败"
                )
            
            current_price = indicators['current_price']
            
            # 生成交易信号
            action, confidence, reason = self._generate_signal(indicators)
            
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
                indicators=indicators
            )
            
            # 评估风险等级
            risk_level = self._assess_risk_level(indicators)
            
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
                take_profit=target_price if action == 'buy' else None,
                reason=reason,
                indicators=indicators,
                risk_level=risk_level,
                expected_return=self._estimate_return(indicators),
                holding_period=7  # 建议持有1周
            )
            
            self.log_strategy_action(result)
            return result
            
        except Exception as e:
            logger.error(f"加密货币动量分析失败: {e}")
            return self.create_hold_result(
                asset_symbol=kwargs.get('asset_symbol', 'Unknown'),
                current_price=0.0,
                reason=f"分析出错: {str(e)}"
            )
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """计算技术指标"""
        indicators = {'valid': False}
        
        try:
            # 基本数据
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            volume = data['volume'].values
            
            indicators['current_price'] = float(close[-1])
            
            # 1. 移动平均线
            if len(close) >= self.ma_slow:
                ma_fast = pd.Series(close).rolling(self.ma_fast).mean()
                ma_slow = pd.Series(close).rolling(self.ma_slow).mean()
                
                indicators['ma_fast'] = float(ma_fast.iloc[-1])
                indicators['ma_slow'] = float(ma_slow.iloc[-1])
                indicators['ma_cross'] = 'golden' if ma_fast.iloc[-1] > ma_slow.iloc[-1] else 'death'
                
                # 检查最近交叉
                if len(ma_fast) >= 2 and len(ma_slow) >= 2:
                    prev_diff = ma_fast.iloc[-2] - ma_slow.iloc[-2]
                    curr_diff = ma_fast.iloc[-1] - ma_slow.iloc[-1]
                    indicators['recent_cross'] = (prev_diff * curr_diff < 0)
                else:
                    indicators['recent_cross'] = False
            
            # 2. RSI
            if len(close) >= self.rsi_period + 1:
                rsi = self._calculate_rsi(close, self.rsi_period)
                indicators['rsi'] = float(rsi[-1])
                
                if rsi[-1] < self.rsi_oversold:
                    indicators['rsi_signal'] = 'oversold'
                elif rsi[-1] > self.rsi_overbought:
                    indicators['rsi_signal'] = 'overbought'
                else:
                    indicators['rsi_signal'] = 'neutral'
            
            # 3. 动量
            if len(close) >= 14:
                momentum = (close[-1] - close[-14]) / close[-14] * 100
                indicators['momentum_14d'] = float(momentum)
            
            # 4. 成交量分析
            if len(volume) >= self.volume_ma_period:
                volume_ma = pd.Series(volume).rolling(self.volume_ma_period).mean()
                indicators['volume_current'] = float(volume[-1])
                indicators['volume_ma'] = float(volume_ma.iloc[-1])
                indicators['volume_surge'] = volume[-1] > volume_ma.iloc[-1] * self.volume_surge_factor
            
            # 5. ATR（平均真实波动幅度）
            if len(data) >= self.atr_period:
                atr = self._calculate_atr(data, self.atr_period)
                indicators['atr'] = float(atr[-1])
                indicators['atr_percent'] = float(atr[-1] / close[-1] * 100)
            
            # 6. 趋势强度
            if len(close) >= 20:
                # 使用线性回归斜率衡量趋势强度
                x = np.arange(20)
                y = close[-20:]
                slope = np.polyfit(x, y, 1)[0]
                indicators['trend_strength'] = float(slope / close[-1] * 100)  # 标准化
            
            # 7. 支撑阻力位
            if len(high) >= 20 and len(low) >= 20:
                recent_high = np.max(high[-20:])
                recent_low = np.min(low[-20:])
                indicators['resistance'] = float(recent_high)
                indicators['support'] = float(recent_low)
                
                # 距离支撑阻力位的距离
                indicators['distance_to_resistance'] = (recent_high - close[-1]) / close[-1] * 100
                indicators['distance_to_support'] = (close[-1] - recent_low) / close[-1] * 100
            
            indicators['valid'] = True
            return indicators
            
        except Exception as e:
            logger.error(f"计算指标失败: {e}")
            return indicators
    
    def _calculate_rsi(self, prices: np.ndarray, period: int) -> np.ndarray:
        """计算RSI"""
        try:
            deltas = np.diff(prices)
            gain = np.where(deltas > 0, deltas, 0)
            loss = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = pd.Series(gain).rolling(period).mean().values
            avg_loss = pd.Series(loss).rolling(period).mean().values
            
            rs = avg_gain / (avg_loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"计算RSI失败: {e}")
            return np.array([50.0])
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> np.ndarray:
        """计算ATR"""
        try:
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            
            tr1 = high - low
            tr2 = np.abs(high - np.roll(close, 1))
            tr3 = np.abs(low - np.roll(close, 1))
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = pd.Series(tr).rolling(period).mean().values
            
            return atr
        except Exception as e:
            logger.error(f"计算ATR失败: {e}")
            return np.array([0.0])
    
    def _generate_signal(self, indicators: Dict) -> tuple:
        """
        生成交易信号
        
        Returns:
            (action, confidence, reason)
        """
        try:
            buy_signals = []
            sell_signals = []
            reasons = []
            
            # 1. 均线信号
            if 'ma_cross' in indicators:
                if indicators['ma_cross'] == 'golden':
                    buy_signals.append(1)
                    if indicators.get('recent_cross', False):
                        buy_signals.append(1)  # 刚发生金叉，加强信号
                        reasons.append("均线金叉")
                    else:
                        reasons.append("多头排列")
                else:
                    sell_signals.append(1)
                    if indicators.get('recent_cross', False):
                        sell_signals.append(1)
                        reasons.append("均线死叉")
                    else:
                        reasons.append("空头排列")
            
            # 2. RSI信号
            if 'rsi_signal' in indicators:
                if indicators['rsi_signal'] == 'oversold':
                    buy_signals.append(1)
                    reasons.append(f"RSI超卖({indicators['rsi']:.1f})")
                elif indicators['rsi_signal'] == 'overbought':
                    sell_signals.append(1)
                    reasons.append(f"RSI超买({indicators['rsi']:.1f})")
            
            # 3. 动量信号
            if 'momentum_14d' in indicators:
                momentum = indicators['momentum_14d']
                if momentum > 10:
                    buy_signals.append(1)
                    reasons.append(f"强劲上涨动量({momentum:.1f}%)")
                elif momentum < -10:
                    sell_signals.append(1)
                    reasons.append(f"下跌动量({momentum:.1f}%)")
            
            # 4. 成交量确认
            if indicators.get('volume_surge', False):
                if len(buy_signals) > len(sell_signals):
                    buy_signals.append(1)
                    reasons.append("成交量放大确认")
                elif len(sell_signals) > len(buy_signals):
                    sell_signals.append(1)
                    reasons.append("成交量放大确认")
            
            # 5. 趋势强度
            if 'trend_strength' in indicators:
                trend = indicators['trend_strength']
                if abs(trend) > 1:  # 每日变化>1%
                    if trend > 0:
                        buy_signals.append(1)
                        reasons.append("强劲上升趋势")
                    else:
                        sell_signals.append(1)
                        reasons.append("明显下降趋势")
            
            # 综合判断
            buy_score = sum(buy_signals)
            sell_score = sum(sell_signals)
            
            if buy_score > sell_score and buy_score >= 2:
                confidence = min(0.9, 0.4 + buy_score * 0.15)
                return 'buy', confidence, "; ".join(reasons)
            elif sell_score > buy_score and sell_score >= 2:
                confidence = min(0.9, 0.4 + sell_score * 0.15)
                return 'sell', confidence, "; ".join(reasons)
            else:
                return 'hold', 0.0, "信号不足，建议观望"
                
        except Exception as e:
            logger.error(f"生成信号失败: {e}")
            return 'hold', 0.0, f"信号生成出错: {str(e)}"
    
    def _calculate_price_targets(self,
                                 current_price: float,
                                 action: str,
                                 indicators: Dict) -> tuple:
        """
        计算价格目标
        
        Returns:
            (target_price, stop_loss)
        """
        try:
            if action == 'buy':
                # 目标价格：基于ATR
                atr = indicators.get('atr', current_price * 0.03)
                target_price = current_price + atr * 3  # 3倍ATR为目标
                
                # 止损：基于ATR
                stop_loss = current_price - atr * self.atr_multiplier
                
                # 检查支撑阻力位
                if 'resistance' in indicators:
                    target_price = min(target_price, indicators['resistance'] * 0.98)
                if 'support' in indicators:
                    stop_loss = max(stop_loss, indicators['support'])
                
            elif action == 'sell':
                target_price = None
                stop_loss = None
            else:
                target_price = None
                stop_loss = None
            
            return target_price, stop_loss
            
        except Exception as e:
            logger.error(f"计算价格目标失败: {e}")
            return None, None
    
    def _assess_risk_level(self, indicators: Dict) -> str:
        """评估风险等级"""
        try:
            risk_factors = 0
            
            # 1. 波动性
            if 'atr_percent' in indicators:
                atr_pct = indicators['atr_percent']
                if atr_pct > 5:
                    risk_factors += 2
                elif atr_pct > 3:
                    risk_factors += 1
            
            # 2. RSI极端值
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 20 or rsi > 80:
                    risk_factors += 1
            
            # 3. 趋势强度
            if 'trend_strength' in indicators:
                if abs(indicators['trend_strength']) > 2:
                    risk_factors += 1
            
            if risk_factors >= 3:
                return 'high'
            elif risk_factors >= 1:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"评估风险等级失败: {e}")
            return 'medium'
    
    def _estimate_return(self, indicators: Dict) -> Optional[float]:
        """估算预期收益率"""
        try:
            # 基于动量和趋势强度估算
            momentum = indicators.get('momentum_14d', 0)
            trend = indicators.get('trend_strength', 0)
            
            # 简单加权
            expected = (momentum * 0.3 + trend * 7 * 0.7) / 100
            
            # 限制在合理范围
            return max(-0.20, min(0.30, expected))
            
        except Exception as e:
            logger.error(f"估算收益率失败: {e}")
            return None
    
    def calculate_position_size(self,
                               capital: float,
                               current_price: float,
                               risk_per_trade: float = 0.02) -> float:
        """
        计算仓位大小
        
        加密货币策略使用更激进的仓位管理
        
        Args:
            capital: 可用资金
            current_price: 当前价格
            risk_per_trade: 单笔风险比例（默认2%）
            
        Returns:
            建议购买数量
        """
        try:
            if current_price <= 0:
                return 0.0
            
            # 加密货币策略：基于凯利公式的动态仓位
            # 假设历史胜率55%，盈亏比2:1
            kelly = self.calculate_kelly_criterion(
                win_rate=0.55,
                avg_win=0.10,
                avg_loss=0.05
            )
            
            # 使用半凯利（更保守）
            position_ratio = kelly * 0.5
            
            # 每次投入资金
            position_value = capital * position_ratio
            quantity = position_value / current_price
            
            # 加密货币可以使用小数
            return round(quantity, 6)
            
        except Exception as e:
            logger.error(f"计算仓位大小失败: {e}")
            return 0.0

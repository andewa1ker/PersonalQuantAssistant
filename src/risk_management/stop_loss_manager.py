"""
止损止盈管理模块
实现多种止损止盈策略
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_risk import BaseRiskManager, StopLossTarget


class StopLossManager(BaseRiskManager):
    """止损止盈管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化止损止盈管理器
        
        配置参数:
            default_stop_loss_pct: 默认止损百分比 (默认: 0.05, 即5%)
            default_take_profit_pct: 默认止盈百分比 (默认: 0.15, 即15%)
            atr_period: ATR计算周期 (默认: 14)
            atr_stop_multiplier: ATR止损倍数 (默认: 2.0)
            atr_profit_multiplier: ATR止盈倍数 (默认: 3.0)
            risk_reward_ratio: 风险收益比 (默认: 3.0)
        """
        super().__init__(config)
        
        self.default_stop_loss_pct = self.get_config_value('default_stop_loss_pct', 0.05)
        self.default_take_profit_pct = self.get_config_value('default_take_profit_pct', 0.15)
        self.atr_period = self.get_config_value('atr_period', 14)
        self.atr_stop_multiplier = self.get_config_value('atr_stop_multiplier', 2.0)
        self.atr_profit_multiplier = self.get_config_value('atr_profit_multiplier', 3.0)
        self.risk_reward_ratio = self.get_config_value('risk_reward_ratio', 3.0)
    
    def calculate_fixed_stop_loss(
        self,
        current_price: float,
        direction: str = 'long',
        **kwargs
    ) -> StopLossTarget:
        """
        计算固定百分比止损止盈
        
        Args:
            current_price: 当前价格
            direction: 方向 ('long' 或 'short')
            **kwargs:
                asset_symbol: 资产标识
                stop_loss_pct: 止损百分比 (可选)
                take_profit_pct: 止盈百分比 (可选)
                risk_reward_ratio: 风险收益比 (可选)
                
        Returns:
            StopLossTarget对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        stop_loss_pct = kwargs.get('stop_loss_pct', self.default_stop_loss_pct)
        take_profit_pct = kwargs.get('take_profit_pct')
        rr_ratio = kwargs.get('risk_reward_ratio', self.risk_reward_ratio)
        
        try:
            if direction == 'long':
                # 做多：止损在下方，止盈在上方
                stop_loss_price = current_price * (1 - stop_loss_pct)
                
                if take_profit_pct is None:
                    # 根据风险收益比计算止盈
                    take_profit_pct = stop_loss_pct * rr_ratio
                
                take_profit_price = current_price * (1 + take_profit_pct)
                
            else:  # short
                # 做空：止损在上方，止盈在下方
                stop_loss_price = current_price * (1 + stop_loss_pct)
                
                if take_profit_pct is None:
                    take_profit_pct = stop_loss_pct * rr_ratio
                
                take_profit_price = current_price * (1 - take_profit_pct)
            
            reason = (f"固定百分比: 止损{stop_loss_pct:.1%}, 止盈{take_profit_pct:.1%}, "
                     f"风险收益比1:{rr_ratio:.1f}")
            
            target = StopLossTarget(
                asset_symbol=asset_symbol,
                current_price=float(current_price),
                stop_loss_price=float(stop_loss_price),
                stop_loss_pct=float(stop_loss_pct),
                take_profit_price=float(take_profit_price),
                take_profit_pct=float(take_profit_pct),
                method='fixed',
                reason=reason,
                details={
                    'direction': direction,
                    'risk_reward_ratio': rr_ratio
                }
            )
            
            logger.info(f"固定止损计算: {asset_symbol} | "
                       f"当前: {current_price:.4f} | "
                       f"止损: {stop_loss_price:.4f} ({stop_loss_pct:.1%}) | "
                       f"止盈: {take_profit_price:.4f} ({take_profit_pct:.1%})")
            
            return target
            
        except Exception as e:
            logger.error(f"固定止损计算失败: {e}", exc_info=True)
            return self._create_default_target(asset_symbol, current_price)
    
    def calculate_atr_stop_loss(
        self,
        data: pd.DataFrame,
        direction: str = 'long',
        **kwargs
    ) -> StopLossTarget:
        """
        基于ATR的动态止损止盈
        ATR (Average True Range) - 平均真实波幅
        
        Args:
            data: 包含OHLC数据的DataFrame
            direction: 方向 ('long' 或 'short')
            **kwargs:
                asset_symbol: 资产标识
                atr_period: ATR周期 (可选)
                stop_multiplier: 止损倍数 (可选)
                profit_multiplier: 止盈倍数 (可选)
                
        Returns:
            StopLossTarget对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        period = kwargs.get('atr_period', self.atr_period)
        stop_mult = kwargs.get('stop_multiplier', self.atr_stop_multiplier)
        profit_mult = kwargs.get('profit_multiplier', self.atr_profit_multiplier)
        
        if not self.validate_data(data, ['high', 'low', 'close']):
            logger.warning(f"{asset_symbol}: 数据不足，使用固定止损")
            current_price = float(data['close'].iloc[-1]) if 'close' in data.columns else 0.0
            return self.calculate_fixed_stop_loss(current_price, direction, asset_symbol=asset_symbol)
        
        try:
            # 计算ATR
            atr = self._calculate_atr(data, period)
            current_price = float(data['close'].iloc[-1])
            
            if atr == 0:
                logger.warning(f"{asset_symbol}: ATR为0，使用固定止损")
                return self.calculate_fixed_stop_loss(current_price, direction, asset_symbol=asset_symbol)
            
            if direction == 'long':
                # 做多：止损 = 当前价 - ATR * 倍数
                stop_loss_price = current_price - (atr * stop_mult)
                take_profit_price = current_price + (atr * profit_mult)
            else:  # short
                # 做空：止损 = 当前价 + ATR * 倍数
                stop_loss_price = current_price + (atr * stop_mult)
                take_profit_price = current_price - (atr * profit_mult)
            
            stop_loss_pct = abs(stop_loss_price - current_price) / current_price
            take_profit_pct = abs(take_profit_price - current_price) / current_price
            
            reason = (f"ATR动态止损: ATR={atr:.4f}, "
                     f"止损倍数{stop_mult}x, 止盈倍数{profit_mult}x")
            
            target = StopLossTarget(
                asset_symbol=asset_symbol,
                current_price=float(current_price),
                stop_loss_price=float(stop_loss_price),
                stop_loss_pct=float(stop_loss_pct),
                take_profit_price=float(take_profit_price),
                take_profit_pct=float(take_profit_pct),
                method='atr',
                atr_value=float(atr),
                atr_multiplier=float(stop_mult),
                reason=reason,
                details={
                    'direction': direction,
                    'atr_period': period,
                    'stop_multiplier': stop_mult,
                    'profit_multiplier': profit_mult
                }
            )
            
            logger.info(f"ATR止损计算: {asset_symbol} | "
                       f"ATR: {atr:.4f} | "
                       f"止损: {stop_loss_price:.4f} | "
                       f"止盈: {take_profit_price:.4f}")
            
            return target
            
        except Exception as e:
            logger.error(f"ATR止损计算失败: {e}", exc_info=True)
            current_price = float(data['close'].iloc[-1])
            return self.calculate_fixed_stop_loss(current_price, direction, asset_symbol=asset_symbol)
    
    def calculate_支撑阻力_stop_loss(
        self,
        data: pd.DataFrame,
        direction: str = 'long',
        **kwargs
    ) -> StopLossTarget:
        """
        基于支撑阻力位的止损止盈
        
        Args:
            data: 价格数据
            direction: 方向
            **kwargs: 其他参数
            
        Returns:
            StopLossTarget对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        lookback = kwargs.get('lookback', 20)
        
        if not self.validate_data(data, ['high', 'low', 'close']):
            logger.warning(f"{asset_symbol}: 数据不足")
            current_price = float(data['close'].iloc[-1]) if 'close' in data.columns else 0.0
            return self.calculate_fixed_stop_loss(current_price, direction, asset_symbol=asset_symbol)
        
        try:
            current_price = float(data['close'].iloc[-1])
            recent_data = data.tail(lookback)
            
            # 找支撑位和阻力位
            support = float(recent_data['low'].min())
            resistance = float(recent_data['high'].max())
            
            if direction == 'long':
                # 做多：止损设在支撑位下方
                stop_loss_price = support * 0.99  # 支撑位下1%
                # 止盈设在阻力位附近
                take_profit_price = resistance * 0.99  # 阻力位下1%
            else:  # short
                # 做空：止损设在阻力位上方
                stop_loss_price = resistance * 1.01
                take_profit_price = support * 1.01
            
            stop_loss_pct = abs(stop_loss_price - current_price) / current_price
            take_profit_pct = abs(take_profit_price - current_price) / current_price
            
            reason = (f"支撑阻力位: 支撑{support:.4f}, 阻力{resistance:.4f}, "
                     f"回看{lookback}期")
            
            target = StopLossTarget(
                asset_symbol=asset_symbol,
                current_price=float(current_price),
                stop_loss_price=float(stop_loss_price),
                stop_loss_pct=float(stop_loss_pct),
                take_profit_price=float(take_profit_price),
                take_profit_pct=float(take_profit_pct),
                method='support_resistance',
                reason=reason,
                details={
                    'direction': direction,
                    'support': support,
                    'resistance': resistance,
                    'lookback': lookback
                }
            )
            
            logger.info(f"支撑阻力止损: {asset_symbol} | "
                       f"支撑: {support:.4f} | "
                       f"阻力: {resistance:.4f}")
            
            return target
            
        except Exception as e:
            logger.error(f"支撑阻力止损计算失败: {e}", exc_info=True)
            current_price = float(data['close'].iloc[-1])
            return self.calculate_fixed_stop_loss(current_price, direction, asset_symbol=asset_symbol)
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        计算ATR (Average True Range)
        
        Args:
            data: OHLC数据
            period: 周期
            
        Returns:
            ATR值
        """
        high = data['high']
        low = data['low']
        close = data['close']
        
        # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR = True Range的移动平均
        atr = float(true_range.rolling(window=period).mean().iloc[-1])
        
        return atr
    
    def _create_default_target(
        self, 
        asset_symbol: str, 
        current_price: float
    ) -> StopLossTarget:
        """创建默认止损止盈目标"""
        stop_loss_pct = self.default_stop_loss_pct
        take_profit_pct = self.default_take_profit_pct
        
        stop_loss_price = current_price * (1 - stop_loss_pct)
        take_profit_price = current_price * (1 + take_profit_pct)
        
        return StopLossTarget(
            asset_symbol=asset_symbol,
            current_price=float(current_price),
            stop_loss_price=float(stop_loss_price),
            stop_loss_pct=float(stop_loss_pct),
            take_profit_price=float(take_profit_price),
            take_profit_pct=float(take_profit_pct),
            method='default',
            reason="使用默认止损止盈配置"
        )
    
    def calculate_metrics(self, data: pd.DataFrame, **kwargs):
        """实现基类的抽象方法（这里不使用）"""
        pass

"""
仓位管理模块
实现基于风险的智能仓位计算
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_risk import BaseRiskManager, PositionSizing


class PositionManager(BaseRiskManager):
    """仓位管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化仓位管理器
        
        配置参数:
            max_position: 单品种最大仓位 (默认: 0.3, 即30%)
            min_position: 最小仓位 (默认: 0.05, 即5%)
            risk_per_trade: 单笔交易风险 (默认: 0.02, 即2%)
            kelly_fraction: 凯利分数调整 (默认: 0.25, 即25%凯利)
            volatility_target: 目标波动率 (默认: 0.15, 即15%)
        """
        super().__init__(config)
        
        self.max_position = self.get_config_value('max_position', 0.3)
        self.min_position = self.get_config_value('min_position', 0.05)
        self.risk_per_trade = self.get_config_value('risk_per_trade', 0.02)
        self.kelly_fraction = self.get_config_value('kelly_fraction', 0.25)
        self.volatility_target = self.get_config_value('volatility_target', 0.15)
    
    def calculate_position_kelly(
        self, 
        win_rate: float, 
        profit_loss_ratio: float,
        **kwargs
    ) -> PositionSizing:
        """
        使用凯利公式计算仓位
        
        凯利公式: f* = (p * b - q) / b
        其中: p = 胜率, q = 1-p, b = 盈亏比
        
        Args:
            win_rate: 胜率 (0-1)
            profit_loss_ratio: 盈亏比 (平均盈利/平均亏损)
            **kwargs: 
                asset_symbol: 资产标识
                kelly_fraction: 凯利分数调整 (默认使用配置值)
                
        Returns:
            PositionSizing对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        kelly_fraction = kwargs.get('kelly_fraction', self.kelly_fraction)
        
        try:
            # 计算完整凯利分数
            p = win_rate
            q = 1 - p
            b = profit_loss_ratio
            
            if b <= 0:
                logger.warning(f"{asset_symbol}: 盈亏比无效 ({b})")
                full_kelly = 0.0
            else:
                full_kelly = (p * b - q) / b
            
            # 应用调整因子（通常使用0.25-0.5的凯利，降低风险）
            adjusted_kelly = full_kelly * kelly_fraction
            
            # 限制在合理范围
            recommended = np.clip(adjusted_kelly, self.min_position, self.max_position)
            
            # 评估置信度
            confidence = self._calculate_confidence(win_rate, profit_loss_ratio)
            
            # 风险等级
            risk_level = self._assess_position_risk(recommended)
            
            reason = (f"凯利公式计算: 胜率{win_rate:.1%}, 盈亏比{profit_loss_ratio:.2f}, "
                     f"完整凯利{full_kelly:.1%}, 调整后{adjusted_kelly:.1%}")
            
            position = PositionSizing(
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                recommended_position=float(recommended),
                max_position=self.max_position,
                min_position=self.min_position,
                method='kelly',
                win_probability=float(win_rate),
                win_loss_ratio=float(profit_loss_ratio),
                risk_level=risk_level,
                confidence=float(confidence),
                reason=reason,
                details={
                    'full_kelly': float(full_kelly),
                    'kelly_fraction': kelly_fraction,
                    'adjusted_kelly': float(adjusted_kelly)
                }
            )
            
            logger.info(f"凯利仓位计算: {asset_symbol} | "
                       f"建议仓位: {recommended:.1%} | "
                       f"胜率: {win_rate:.1%} | "
                       f"盈亏比: {profit_loss_ratio:.2f}")
            
            return position
            
        except Exception as e:
            logger.error(f"凯利仓位计算失败: {e}", exc_info=True)
            return self._create_default_position(asset_symbol)
    
    def calculate_position_volatility(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> PositionSizing:
        """
        基于波动率的仓位调整
        目标波动率 / 实际波动率 = 仓位比例
        
        Args:
            data: 价格数据
            **kwargs:
                asset_symbol: 资产标识
                target_volatility: 目标波动率 (默认使用配置值)
                
        Returns:
            PositionSizing对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        target_vol = kwargs.get('target_volatility', self.volatility_target)
        
        if not self.validate_data(data, ['close']):
            return self._create_default_position(asset_symbol)
        
        try:
            returns = self.calculate_returns(data['close'])
            
            if len(returns) < 20:
                logger.warning(f"{asset_symbol}: 数据不足以计算波动率")
                return self._create_default_position(asset_symbol)
            
            # 计算年化波动率
            daily_vol = float(returns.std())
            annualized_vol = self.annualize_metric(daily_vol)
            
            # 目标波动率 / 实际波动率
            if annualized_vol > 0:
                position_ratio = target_vol / annualized_vol
            else:
                position_ratio = 0.0
            
            # 限制在合理范围
            recommended = np.clip(position_ratio, self.min_position, self.max_position)
            
            confidence = min(0.7, 1.0 - abs(annualized_vol - target_vol) / target_vol)
            risk_level = self._assess_position_risk(recommended)
            
            reason = (f"波动率调整: 目标{target_vol:.1%}, 实际{annualized_vol:.1%}, "
                     f"比例{position_ratio:.1%}")
            
            position = PositionSizing(
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                recommended_position=float(recommended),
                max_position=self.max_position,
                min_position=self.min_position,
                method='volatility',
                volatility=float(annualized_vol),
                risk_level=risk_level,
                confidence=float(confidence),
                reason=reason,
                details={
                    'target_volatility': target_vol,
                    'actual_volatility': float(annualized_vol),
                    'position_ratio': float(position_ratio)
                }
            )
            
            logger.info(f"波动率仓位计算: {asset_symbol} | "
                       f"建议仓位: {recommended:.1%} | "
                       f"波动率: {annualized_vol:.1%}")
            
            return position
            
        except Exception as e:
            logger.error(f"波动率仓位计算失败: {e}", exc_info=True)
            return self._create_default_position(asset_symbol)
    
    def calculate_position_fixed_risk(
        self,
        stop_loss_pct: float,
        **kwargs
    ) -> PositionSizing:
        """
        基于固定风险的仓位计算
        仓位 = 风险金额 / 止损幅度
        
        Args:
            stop_loss_pct: 止损百分比 (如0.05表示5%)
            **kwargs:
                asset_symbol: 资产标识
                risk_per_trade: 单笔风险 (默认使用配置值)
                
        Returns:
            PositionSizing对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        risk = kwargs.get('risk_per_trade', self.risk_per_trade)
        
        try:
            if stop_loss_pct <= 0:
                logger.warning(f"{asset_symbol}: 止损比例无效")
                return self._create_default_position(asset_symbol)
            
            # 仓位 = 愿意承担的风险 / 止损幅度
            recommended = risk / stop_loss_pct
            
            # 限制在合理范围
            recommended = np.clip(recommended, self.min_position, self.max_position)
            
            confidence = 0.8  # 固定风险法置信度较高
            risk_level = self._assess_position_risk(recommended)
            
            reason = f"固定风险法: 风险{risk:.1%}, 止损{stop_loss_pct:.1%}"
            
            position = PositionSizing(
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                recommended_position=float(recommended),
                max_position=self.max_position,
                min_position=self.min_position,
                method='fixed_risk',
                risk_level=risk_level,
                confidence=float(confidence),
                reason=reason,
                details={
                    'risk_per_trade': risk,
                    'stop_loss_pct': stop_loss_pct
                }
            )
            
            logger.info(f"固定风险仓位计算: {asset_symbol} | "
                       f"建议仓位: {recommended:.1%} | "
                       f"止损: {stop_loss_pct:.1%}")
            
            return position
            
        except Exception as e:
            logger.error(f"固定风险仓位计算失败: {e}", exc_info=True)
            return self._create_default_position(asset_symbol)
    
    def calculate_position_综合(
        self,
        data: pd.DataFrame,
        win_rate: Optional[float] = None,
        profit_loss_ratio: Optional[float] = None,
        **kwargs
    ) -> PositionSizing:
        """
        综合多种方法计算仓位
        
        Args:
            data: 价格数据
            win_rate: 胜率（可选）
            profit_loss_ratio: 盈亏比（可选）
            **kwargs: 其他参数
            
        Returns:
            PositionSizing对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        
        positions = []
        weights = []
        
        # 1. 波动率法
        try:
            pos_vol = self.calculate_position_volatility(data, asset_symbol=asset_symbol)
            positions.append(pos_vol.recommended_position)
            weights.append(0.4)
        except:
            pass
        
        # 2. 凯利法（如果有胜率和盈亏比）
        if win_rate is not None and profit_loss_ratio is not None:
            try:
                pos_kelly = self.calculate_position_kelly(
                    win_rate, 
                    profit_loss_ratio,
                    asset_symbol=asset_symbol
                )
                positions.append(pos_kelly.recommended_position)
                weights.append(0.4)
            except:
                pass
        
        # 3. 固定风险法
        try:
            stop_loss_pct = 0.05  # 默认5%止损
            pos_fixed = self.calculate_position_fixed_risk(
                stop_loss_pct,
                asset_symbol=asset_symbol
            )
            positions.append(pos_fixed.recommended_position)
            weights.append(0.2)
        except:
            pass
        
        if not positions:
            return self._create_default_position(asset_symbol)
        
        # 加权平均
        weights_sum = sum(weights[:len(positions)])
        normalized_weights = [w / weights_sum for w in weights[:len(positions)]]
        
        recommended = sum(p * w for p, w in zip(positions, normalized_weights))
        recommended = np.clip(recommended, self.min_position, self.max_position)
        
        risk_level = self._assess_position_risk(recommended)
        
        methods_used = []
        if len(positions) >= 1:
            methods_used.append('volatility')
        if len(positions) >= 2:
            methods_used.append('kelly')
        if len(positions) >= 3:
            methods_used.append('fixed_risk')
        
        reason = f"综合{len(positions)}种方法: {', '.join(methods_used)}"
        
        position = PositionSizing(
            asset_symbol=asset_symbol,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            recommended_position=float(recommended),
            max_position=self.max_position,
            min_position=self.min_position,
            method='综合',
            win_probability=win_rate,
            win_loss_ratio=profit_loss_ratio,
            risk_level=risk_level,
            confidence=0.75,
            reason=reason,
            details={
                'methods': methods_used,
                'positions': [float(p) for p in positions],
                'weights': normalized_weights
            }
        )
        
        logger.info(f"综合仓位计算: {asset_symbol} | 建议仓位: {recommended:.1%}")
        
        return position
    
    def _calculate_confidence(self, win_rate: float, pl_ratio: float) -> float:
        """
        计算仓位建议的置信度
        
        Args:
            win_rate: 胜率
            pl_ratio: 盈亏比
            
        Returns:
            置信度 (0-1)
        """
        # 胜率越接近50%或越高，置信度越高
        win_score = min(win_rate, 1 - win_rate) * 2  # 0-1
        
        # 盈亏比越高，置信度越高
        pl_score = min(pl_ratio / 3, 1.0)  # 盈亏比3以上满分
        
        confidence = (win_score * 0.4 + pl_score * 0.6)
        
        return float(confidence)
    
    def _assess_position_risk(self, position: float) -> str:
        """
        评估仓位的风险等级
        
        Args:
            position: 仓位比例
            
        Returns:
            风险等级
        """
        if position >= 0.5:
            return "high"
        elif position >= 0.3:
            return "medium"
        elif position >= 0.1:
            return "low"
        else:
            return "very_low"
    
    def _create_default_position(self, asset_symbol: str) -> PositionSizing:
        """创建默认仓位建议"""
        default_position = 0.1  # 默认10%
        
        return PositionSizing(
            asset_symbol=asset_symbol,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            recommended_position=default_position,
            max_position=self.max_position,
            min_position=self.min_position,
            method='default',
            risk_level='medium',
            confidence=0.5,
            reason="使用默认仓位配置"
        )
    
    def calculate_metrics(self, data: pd.DataFrame, **kwargs):
        """实现基类的抽象方法（这里不使用）"""
        pass

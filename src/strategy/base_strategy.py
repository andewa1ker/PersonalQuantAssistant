"""
策略基类
定义所有策略的通用接口和结构
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from loguru import logger


@dataclass
class StrategyResult:
    """策略执行结果"""
    
    # 基本信息
    strategy_name: str              # 策略名称
    asset_symbol: str               # 资产标识
    timestamp: str                  # 执行时间
    
    # 交易建议
    action: str                     # 操作：buy/sell/hold
    quantity: float                 # 建议数量
    confidence: float               # 信心度 (0-1)
    
    # 价格信息
    current_price: float            # 当前价格
    target_price: Optional[float]   # 目标价格
    stop_loss: Optional[float]      # 止损价格
    take_profit: Optional[float]    # 止盈价格
    
    # 分析数据
    reason: str                     # 操作原因
    indicators: Dict[str, Any]      # 相关指标
    risk_level: str                 # 风险等级：low/medium/high
    
    # 额外信息
    expected_return: Optional[float] = None  # 预期收益率
    holding_period: Optional[int] = None     # 建议持有天数
    notes: Optional[str] = None              # 备注
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'asset_symbol': self.asset_symbol,
            'timestamp': self.timestamp,
            'action': self.action,
            'quantity': self.quantity,
            'confidence': self.confidence,
            'current_price': self.current_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'reason': self.reason,
            'indicators': self.indicators,
            'risk_level': self.risk_level,
            'expected_return': self.expected_return,
            'holding_period': self.holding_period,
            'notes': self.notes
        }


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化策略
        
        Args:
            config: 策略配置参数
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        logger.info(f"初始化策略: {self.name}")
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, **kwargs) -> StrategyResult:
        """
        分析数据并生成策略结果
        
        Args:
            data: 价格数据
            **kwargs: 其他参数
            
        Returns:
            StrategyResult: 策略执行结果
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, 
                               capital: float,
                               current_price: float,
                               risk_per_trade: float = 0.02) -> float:
        """
        计算仓位大小
        
        Args:
            capital: 可用资金
            current_price: 当前价格
            risk_per_trade: 单笔风险比例（默认2%）
            
        Returns:
            建议购买数量
        """
        pass
    
    def validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 待验证的数据
            required_columns: 必需的列
            
        Returns:
            是否验证通过
        """
        try:
            if data is None or data.empty:
                logger.warning("数据为空")
                return False
            
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                logger.warning(f"缺少必需的列: {missing_columns}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return False
    
    def calculate_risk_reward_ratio(self,
                                   entry_price: float,
                                   target_price: float,
                                   stop_loss: float) -> float:
        """
        计算风险收益比
        
        Args:
            entry_price: 入场价格
            target_price: 目标价格
            stop_loss: 止损价格
            
        Returns:
            风险收益比
        """
        try:
            potential_profit = abs(target_price - entry_price)
            potential_loss = abs(entry_price - stop_loss)
            
            if potential_loss == 0:
                return float('inf')
            
            return potential_profit / potential_loss
            
        except Exception as e:
            logger.error(f"计算风险收益比失败: {e}")
            return 0.0
    
    def calculate_kelly_criterion(self,
                                  win_rate: float,
                                  avg_win: float,
                                  avg_loss: float) -> float:
        """
        计算凯利公式建议的仓位比例
        
        Args:
            win_rate: 胜率 (0-1)
            avg_win: 平均盈利比例
            avg_loss: 平均亏损比例
            
        Returns:
            建议仓位比例 (0-1)
        """
        try:
            if avg_loss == 0:
                return 0.0
            
            # Kelly = (p * b - q) / b
            # p: 胜率, q: 败率, b: 盈亏比
            b = avg_win / avg_loss
            kelly = (win_rate * b - (1 - win_rate)) / b
            
            # 限制在合理范围内
            kelly = max(0.0, min(kelly, 0.25))  # 最多25%
            
            return kelly
            
        except Exception as e:
            logger.error(f"计算Kelly准则失败: {e}")
            return 0.0
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def log_strategy_action(self, result: StrategyResult):
        """
        记录策略操作
        
        Args:
            result: 策略结果
        """
        logger.info(
            f"策略: {result.strategy_name} | "
            f"资产: {result.asset_symbol} | "
            f"操作: {result.action} | "
            f"价格: {result.current_price} | "
            f"信心度: {result.confidence:.2%} | "
            f"原因: {result.reason}"
        )
    
    def create_hold_result(self,
                          asset_symbol: str,
                          current_price: float,
                          reason: str = "暂无明确信号") -> StrategyResult:
        """
        创建持有结果
        
        Args:
            asset_symbol: 资产标识
            current_price: 当前价格
            reason: 原因
            
        Returns:
            StrategyResult
        """
        return StrategyResult(
            strategy_name=self.name,
            asset_symbol=asset_symbol,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            action='hold',
            quantity=0.0,
            confidence=0.0,
            current_price=current_price,
            target_price=None,
            stop_loss=None,
            take_profit=None,
            reason=reason,
            indicators={},
            risk_level='low'
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name}(config={self.config})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return self.__str__()

"""
风险管理基础模块
定义风险指标数据类和基础接口
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from loguru import logger


@dataclass
class RiskMetrics:
    """风险指标数据类"""
    
    # 基本信息
    asset_symbol: str
    timestamp: str
    
    # 收益指标
    total_return: float = 0.0  # 总收益率
    annualized_return: float = 0.0  # 年化收益率
    
    # 风险指标
    volatility: float = 0.0  # 波动率（年化）
    max_drawdown: float = 0.0  # 最大回撤
    var_95: float = 0.0  # 95% VaR
    cvar_95: float = 0.0  # 95% CVaR (条件VaR)
    
    # 风险调整收益指标
    sharpe_ratio: float = 0.0  # 夏普比率
    sortino_ratio: float = 0.0  # 索提诺比率
    calmar_ratio: float = 0.0  # 卡玛比率
    
    # 其他指标
    downside_volatility: float = 0.0  # 下行波动率
    win_rate: float = 0.0  # 胜率
    profit_loss_ratio: float = 0.0  # 盈亏比
    
    # 风险等级评估
    risk_level: str = "medium"  # low, medium, high, extreme
    risk_score: float = 50.0  # 0-100，越高越危险
    
    # 详细数据
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'asset_symbol': self.asset_symbol,
            'timestamp': self.timestamp,
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': self.volatility,
            'max_drawdown': self.max_drawdown,
            'var_95': self.var_95,
            'cvar_95': self.cvar_95,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'downside_volatility': self.downside_volatility,
            'win_rate': self.win_rate,
            'profit_loss_ratio': self.profit_loss_ratio,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'details': self.details
        }


@dataclass
class PositionSizing:
    """仓位管理建议"""
    
    asset_symbol: str
    timestamp: str
    
    # 仓位建议
    recommended_position: float  # 建议仓位百分比 (0-1)
    max_position: float  # 最大仓位百分比 (0-1)
    min_position: float = 0.0  # 最小仓位百分比 (0-1)
    
    # 计算依据
    method: str = "kelly"  # kelly, fixed, volatility, risk_parity
    win_probability: Optional[float] = None
    win_loss_ratio: Optional[float] = None
    volatility: Optional[float] = None
    
    # 风险参数
    risk_level: str = "medium"
    confidence: float = 0.0
    
    reason: str = ""
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'asset_symbol': self.asset_symbol,
            'timestamp': self.timestamp,
            'recommended_position': self.recommended_position,
            'max_position': self.max_position,
            'min_position': self.min_position,
            'method': self.method,
            'win_probability': self.win_probability,
            'win_loss_ratio': self.win_loss_ratio,
            'volatility': self.volatility,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'reason': self.reason,
            'details': self.details
        }


@dataclass
class StopLossTarget:
    """止损止盈目标"""
    
    asset_symbol: str
    current_price: float
    
    # 止损
    stop_loss_price: float
    stop_loss_pct: float  # 止损百分比
    
    # 止盈
    take_profit_price: float
    take_profit_pct: float  # 止盈百分比
    
    # 方法
    method: str = "fixed"  # fixed, atr, percentage, support_resistance
    
    # ATR相关（如果使用ATR方法）
    atr_value: Optional[float] = None
    atr_multiplier: float = 2.0
    
    reason: str = ""
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'asset_symbol': self.asset_symbol,
            'current_price': self.current_price,
            'stop_loss_price': self.stop_loss_price,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_price': self.take_profit_price,
            'take_profit_pct': self.take_profit_pct,
            'method': self.method,
            'atr_value': self.atr_value,
            'atr_multiplier': self.atr_multiplier,
            'reason': self.reason,
            'details': self.details
        }


@dataclass
class RiskAlert:
    """风险警报"""
    
    alert_type: str  # warning, critical, info
    asset_symbol: str
    timestamp: str
    
    title: str
    message: str
    metric_name: str  # 触发警报的指标名称
    metric_value: float  # 指标值
    threshold: float  # 阈值
    
    severity: int = 1  # 1-5，严重程度
    suggested_action: str = ""  # 建议采取的行动
    
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'alert_type': self.alert_type,
            'asset_symbol': self.asset_symbol,
            'timestamp': self.timestamp,
            'title': self.title,
            'message': self.message,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'severity': self.severity,
            'suggested_action': self.suggested_action,
            'details': self.details
        }


class BaseRiskManager(ABC):
    """风险管理基类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化风险管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        logger.info(f"初始化风险管理器: {self.name}")
    
    def get_config_value(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    @abstractmethod
    def calculate_metrics(self, data: pd.DataFrame, **kwargs) -> RiskMetrics:
        """
        计算风险指标
        
        Args:
            data: 价格/收益数据
            **kwargs: 其他参数
            
        Returns:
            RiskMetrics对象
        """
        pass
    
    def validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 数据DataFrame
            required_columns: 必需的列名列表
            
        Returns:
            是否有效
        """
        if data is None or len(data) == 0:
            logger.warning("数据为空")
            return False
        
        for col in required_columns:
            if col not in data.columns:
                logger.warning(f"缺少必需列: {col}")
                return False
        
        return True
    
    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """
        计算收益率
        
        Args:
            prices: 价格序列
            
        Returns:
            收益率序列
        """
        return prices.pct_change().dropna()
    
    def annualize_metric(self, metric: float, periods_per_year: int = 252) -> float:
        """
        年化指标
        
        Args:
            metric: 指标值
            periods_per_year: 每年的周期数（日线252，周线52）
            
        Returns:
            年化后的指标
        """
        return metric * np.sqrt(periods_per_year)
    
    def log_risk_alert(self, alert: RiskAlert):
        """
        记录风险警报
        
        Args:
            alert: 风险警报对象
        """
        level_map = {
            'info': logger.info,
            'warning': logger.warning,
            'critical': logger.error
        }
        
        log_func = level_map.get(alert.alert_type, logger.info)
        log_func(f"风险警报 | {alert.asset_symbol} | {alert.title} | "
                f"{alert.metric_name}: {alert.metric_value:.2f} (阈值: {alert.threshold:.2f})")

"""
风险监控告警模块
实时监控风险指标并生成告警
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_risk import BaseRiskManager, RiskAlert, RiskMetrics
from .risk_measurement import RiskMeasurement


class RiskMonitor(BaseRiskManager):
    """风险监控器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化风险监控器
        
        配置参数:
            max_drawdown_threshold: 最大回撤阈值 (默认: 0.20, 即20%)
            volatility_threshold: 波动率阈值 (默认: 0.40, 即40%)
            var_threshold: VaR阈值 (默认: 0.05, 即5%)
            min_sharpe_ratio: 最低夏普比率 (默认: 0.5)
            max_position_threshold: 最大单品种仓位 (默认: 0.30)
            总体风险等级阈值
        """
        super().__init__(config)
        
        self.max_drawdown_threshold = self.get_config_value('max_drawdown_threshold', 0.20)
        self.volatility_threshold = self.get_config_value('volatility_threshold', 0.40)
        self.var_threshold = self.get_config_value('var_threshold', 0.05)
        self.min_sharpe_ratio = self.get_config_value('min_sharpe_ratio', 0.5)
        self.max_position_threshold = self.get_config_value('max_position_threshold', 0.30)
        
        # 风险测量器
        self.risk_measurement = RiskMeasurement(config)
    
    def monitor_asset_risk(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> tuple:
        """
        监控单个资产的风险
        
        Args:
            data: 价格数据
            **kwargs:
                asset_symbol: 资产标识
                current_position: 当前仓位 (可选)
                
        Returns:
            (RiskMetrics, List[RiskAlert])
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        current_position = kwargs.get('current_position', 0.0)
        
        alerts = []
        
        # 计算风险指标
        metrics = self.risk_measurement.calculate_metrics(data, asset_symbol=asset_symbol)
        
        # 检查各项风险指标
        alerts.extend(self._check_drawdown(metrics))
        alerts.extend(self._check_volatility(metrics))
        alerts.extend(self._check_var(metrics))
        alerts.extend(self._check_sharpe_ratio(metrics))
        alerts.extend(self._check_position(asset_symbol, current_position))
        alerts.extend(self._check_risk_level(metrics))
        
        # 记录告警
        for alert in alerts:
            self.log_risk_alert(alert)
        
        logger.info(f"风险监控: {asset_symbol} | "
                   f"风险等级: {metrics.risk_level} | "
                   f"告警数: {len(alerts)}")
        
        return metrics, alerts
    
    def monitor_portfolio_risk(
        self,
        holdings: Dict[str, Dict],
        **kwargs
    ) -> List[RiskAlert]:
        """
        监控投资组合整体风险
        
        Args:
            holdings: 持仓字典 {asset_symbol: {'value': xxx, 'quantity': xxx}}
            **kwargs: 其他参数
            
        Returns:
            告警列表
        """
        alerts = []
        
        if not holdings:
            return alerts
        
        try:
            # 计算总值
            total_value = sum(h['value'] for h in holdings.values())
            
            if total_value == 0:
                return alerts
            
            # 检查单品种集中度
            for asset, holding in holdings.items():
                position_pct = holding['value'] / total_value
                
                if position_pct > self.max_position_threshold:
                    alert = RiskAlert(
                        alert_type='warning',
                        asset_symbol=asset,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        title='持仓集中度过高',
                        message=f'{asset}仓位占比{position_pct:.1%}，超过阈值{self.max_position_threshold:.1%}',
                        metric_name='position_concentration',
                        metric_value=position_pct,
                        threshold=self.max_position_threshold,
                        severity=3,
                        suggested_action='建议分散投资，降低单一资产风险敞口'
                    )
                    alerts.append(alert)
            
            # 检查持仓数量
            num_assets = len(holdings)
            if num_assets == 1:
                alert = RiskAlert(
                    alert_type='warning',
                    asset_symbol='Portfolio',
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    title='投资组合过于集中',
                    message=f'仅持有{num_assets}个资产，建议增加多元化',
                    metric_name='portfolio_diversity',
                    metric_value=num_assets,
                    threshold=3.0,
                    severity=2,
                    suggested_action='增加持仓品种，提高投资组合多样性'
                )
                alerts.append(alert)
            
            logger.info(f"投资组合监控: {num_assets}个资产 | 告警数: {len(alerts)}")
            
        except Exception as e:
            logger.error(f"投资组合监控失败: {e}", exc_info=True)
        
        return alerts
    
    def _check_drawdown(self, metrics: RiskMetrics) -> List[RiskAlert]:
        """检查回撤风险"""
        alerts = []
        
        if metrics.max_drawdown > self.max_drawdown_threshold:
            severity = 4 if metrics.max_drawdown > 0.3 else 3
            alert_type = 'critical' if severity >= 4 else 'warning'
            
            alert = RiskAlert(
                alert_type=alert_type,
                asset_symbol=metrics.asset_symbol,
                timestamp=metrics.timestamp,
                title='最大回撤超标',
                message=f'最大回撤{metrics.max_drawdown:.1%}，超过阈值{self.max_drawdown_threshold:.1%}',
                metric_name='max_drawdown',
                metric_value=metrics.max_drawdown,
                threshold=self.max_drawdown_threshold,
                severity=severity,
                suggested_action='考虑减仓或设置更严格的止损'
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_volatility(self, metrics: RiskMetrics) -> List[RiskAlert]:
        """检查波动率风险"""
        alerts = []
        
        if metrics.volatility > self.volatility_threshold:
            severity = 4 if metrics.volatility > 0.6 else 3
            alert_type = 'critical' if severity >= 4 else 'warning'
            
            alert = RiskAlert(
                alert_type=alert_type,
                asset_symbol=metrics.asset_symbol,
                timestamp=metrics.timestamp,
                title='波动率过高',
                message=f'年化波动率{metrics.volatility:.1%}，超过阈值{self.volatility_threshold:.1%}',
                metric_name='volatility',
                metric_value=metrics.volatility,
                threshold=self.volatility_threshold,
                severity=severity,
                suggested_action='高波动环境，建议降低仓位或使用期权对冲'
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_var(self, metrics: RiskMetrics) -> List[RiskAlert]:
        """检查VaR风险"""
        alerts = []
        
        if metrics.var_95 > self.var_threshold:
            alert = RiskAlert(
                alert_type='warning',
                asset_symbol=metrics.asset_symbol,
                timestamp=metrics.timestamp,
                title='VaR值偏高',
                message=f'95% VaR为{metrics.var_95:.1%}，超过阈值{self.var_threshold:.1%}',
                metric_name='var_95',
                metric_value=metrics.var_95,
                threshold=self.var_threshold,
                severity=2,
                suggested_action='潜在日损失较大，注意风险控制'
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_sharpe_ratio(self, metrics: RiskMetrics) -> List[RiskAlert]:
        """检查夏普比率"""
        alerts = []
        
        if metrics.sharpe_ratio < self.min_sharpe_ratio:
            severity = 3 if metrics.sharpe_ratio < 0 else 2
            alert_type = 'warning' if severity >= 3 else 'info'
            
            alert = RiskAlert(
                alert_type=alert_type,
                asset_symbol=metrics.asset_symbol,
                timestamp=metrics.timestamp,
                title='夏普比率偏低',
                message=f'夏普比率{metrics.sharpe_ratio:.2f}，低于阈值{self.min_sharpe_ratio:.2f}',
                metric_name='sharpe_ratio',
                metric_value=metrics.sharpe_ratio,
                threshold=self.min_sharpe_ratio,
                severity=severity,
                suggested_action='风险调整后收益不佳，考虑调整策略'
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_position(self, asset_symbol: str, position: float) -> List[RiskAlert]:
        """检查仓位"""
        alerts = []
        
        if position > self.max_position_threshold:
            alert = RiskAlert(
                alert_type='warning',
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                title='仓位过重',
                message=f'当前仓位{position:.1%}，超过建议上限{self.max_position_threshold:.1%}',
                metric_name='position',
                metric_value=position,
                threshold=self.max_position_threshold,
                severity=3,
                suggested_action='建议减仓至合理水平'
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_risk_level(self, metrics: RiskMetrics) -> List[RiskAlert]:
        """检查整体风险等级"""
        alerts = []
        
        if metrics.risk_level in ['high', 'extreme']:
            severity = 5 if metrics.risk_level == 'extreme' else 4
            alert_type = 'critical'
            
            alert = RiskAlert(
                alert_type=alert_type,
                asset_symbol=metrics.asset_symbol,
                timestamp=metrics.timestamp,
                title=f'风险等级: {metrics.risk_level.upper()}',
                message=f'综合风险评分{metrics.risk_score:.0f}/100，风险等级{metrics.risk_level}',
                metric_name='risk_score',
                metric_value=metrics.risk_score,
                threshold=50.0,
                severity=severity,
                suggested_action='高风险环境，建议谨慎操作或空仓观望'
            )
            alerts.append(alert)
        
        return alerts
    
    def calculate_metrics(self, data: pd.DataFrame, **kwargs) -> RiskMetrics:
        """实现基类方法"""
        return self.risk_measurement.calculate_metrics(data, **kwargs)

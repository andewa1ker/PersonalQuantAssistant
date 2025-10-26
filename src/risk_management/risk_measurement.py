"""
风险度量计算模块
实现VaR、CVaR、最大回撤、夏普比率等风险指标
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_risk import BaseRiskManager, RiskMetrics


class RiskMeasurement(BaseRiskManager):
    """风险度量计算器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化风险度量计算器
        
        配置参数:
            risk_free_rate: 无风险利率 (默认: 0.03, 即3%)
            confidence_level: 置信水平 (默认: 0.95)
            periods_per_year: 每年交易日数 (默认: 252)
        """
        super().__init__(config)
        
        self.risk_free_rate = self.get_config_value('risk_free_rate', 0.03)
        self.confidence_level = self.get_config_value('confidence_level', 0.95)
        self.periods_per_year = self.get_config_value('periods_per_year', 252)
    
    def calculate_metrics(self, data: pd.DataFrame, **kwargs) -> RiskMetrics:
        """
        计算全面的风险指标
        
        Args:
            data: 包含价格数据的DataFrame (需要'close'列)
            **kwargs: 
                asset_symbol: 资产标识
                
        Returns:
            RiskMetrics对象
        """
        asset_symbol = kwargs.get('asset_symbol', 'Unknown')
        
        # 验证数据
        if not self.validate_data(data, ['close']):
            return self._create_empty_metrics(asset_symbol)
        
        try:
            prices = data['close']
            returns = self.calculate_returns(prices)
            
            if len(returns) < 2:
                logger.warning(f"{asset_symbol}: 收益数据不足")
                return self._create_empty_metrics(asset_symbol)
            
            # 计算各项指标
            metrics = RiskMetrics(
                asset_symbol=asset_symbol,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 收益指标
            metrics.total_return = self._calculate_total_return(prices)
            metrics.annualized_return = self._calculate_annualized_return(returns)
            
            # 风险指标
            metrics.volatility = self._calculate_volatility(returns)
            metrics.max_drawdown = self._calculate_max_drawdown(prices)
            metrics.var_95 = self._calculate_var(returns, self.confidence_level)
            metrics.cvar_95 = self._calculate_cvar(returns, self.confidence_level)
            
            # 风险调整收益
            metrics.sharpe_ratio = self._calculate_sharpe_ratio(returns, metrics.volatility)
            metrics.sortino_ratio = self._calculate_sortino_ratio(returns)
            metrics.calmar_ratio = self._calculate_calmar_ratio(
                metrics.annualized_return, 
                metrics.max_drawdown
            )
            
            # 其他指标
            metrics.downside_volatility = self._calculate_downside_volatility(returns)
            metrics.win_rate = self._calculate_win_rate(returns)
            metrics.profit_loss_ratio = self._calculate_profit_loss_ratio(returns)
            
            # 风险等级评估
            metrics.risk_level, metrics.risk_score = self._assess_risk_level(metrics)
            
            # 详细数据
            metrics.details = {
                'data_points': len(returns),
                'positive_returns': int((returns > 0).sum()),
                'negative_returns': int((returns < 0).sum()),
                'best_day': float(returns.max()),
                'worst_day': float(returns.min()),
                'avg_return': float(returns.mean()),
                'median_return': float(returns.median())
            }
            
            logger.info(f"风险指标计算完成: {asset_symbol} | "
                       f"收益: {metrics.annualized_return:.2%} | "
                       f"波动: {metrics.volatility:.2%} | "
                       f"夏普: {metrics.sharpe_ratio:.2f} | "
                       f"最大回撤: {metrics.max_drawdown:.2%}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算风险指标失败: {e}", exc_info=True)
            return self._create_empty_metrics(asset_symbol)
    
    def _calculate_total_return(self, prices: pd.Series) -> float:
        """计算总收益率"""
        if len(prices) < 2:
            return 0.0
        return float((prices.iloc[-1] / prices.iloc[0]) - 1)
    
    def _calculate_annualized_return(self, returns: pd.Series) -> float:
        """计算年化收益率"""
        if len(returns) == 0:
            return 0.0
        
        # 使用几何平均
        cumulative_return = (1 + returns).prod()
        n_periods = len(returns)
        annualized = (cumulative_return ** (self.periods_per_year / n_periods)) - 1
        
        return float(annualized)
    
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """计算波动率（年化）"""
        if len(returns) < 2:
            return 0.0
        
        daily_vol = float(returns.std())
        annualized_vol = self.annualize_metric(daily_vol, self.periods_per_year)
        
        return annualized_vol
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """
        计算最大回撤
        
        Returns:
            最大回撤（正数表示下跌幅度）
        """
        if len(prices) < 2:
            return 0.0
        
        # 计算累计最高价
        cummax = prices.cummax()
        
        # 计算回撤
        drawdown = (prices - cummax) / cummax
        
        # 最大回撤（取绝对值）
        max_dd = float(abs(drawdown.min()))
        
        return max_dd
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算VaR (Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            VaR值（正数表示损失）
        """
        if len(returns) < 2:
            return 0.0
        
        var = float(abs(np.percentile(returns, (1 - confidence_level) * 100)))
        
        return var
    
    def _calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算CVaR (Conditional VaR / Expected Shortfall)
        条件VaR：超过VaR的平均损失
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            CVaR值（正数表示损失）
        """
        if len(returns) < 2:
            return 0.0
        
        var = -self._calculate_var(returns, confidence_level)
        
        # 计算低于VaR的收益的平均值
        tail_losses = returns[returns <= var]
        
        if len(tail_losses) > 0:
            cvar = float(abs(tail_losses.mean()))
        else:
            cvar = float(abs(var))
        
        return cvar
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, volatility: float) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            volatility: 年化波动率
            
        Returns:
            夏普比率
        """
        if volatility == 0 or len(returns) < 2:
            return 0.0
        
        # 年化收益
        annualized_return = self._calculate_annualized_return(returns)
        
        # 夏普比率 = (年化收益 - 无风险利率) / 年化波动率
        sharpe = (annualized_return - self.risk_free_rate) / volatility
        
        return float(sharpe)
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """
        计算索提诺比率
        只考虑下行波动率
        
        Returns:
            索提诺比率
        """
        if len(returns) < 2:
            return 0.0
        
        annualized_return = self._calculate_annualized_return(returns)
        downside_vol = self._calculate_downside_volatility(returns)
        
        if downside_vol == 0:
            return 0.0
        
        sortino = (annualized_return - self.risk_free_rate) / downside_vol
        
        return float(sortino)
    
    def _calculate_calmar_ratio(self, annualized_return: float, max_drawdown: float) -> float:
        """
        计算卡玛比率
        年化收益 / 最大回撤
        
        Returns:
            卡玛比率
        """
        if max_drawdown == 0:
            return 0.0
        
        calmar = annualized_return / max_drawdown
        
        return float(calmar)
    
    def _calculate_downside_volatility(self, returns: pd.Series) -> float:
        """
        计算下行波动率
        只考虑负收益的波动
        
        Returns:
            年化下行波动率
        """
        if len(returns) < 2:
            return 0.0
        
        # 只取负收益
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) < 2:
            return 0.0
        
        downside_vol = float(negative_returns.std())
        annualized_downside_vol = self.annualize_metric(downside_vol, self.periods_per_year)
        
        return annualized_downside_vol
    
    def _calculate_win_rate(self, returns: pd.Series) -> float:
        """计算胜率"""
        if len(returns) == 0:
            return 0.0
        
        wins = (returns > 0).sum()
        total = len(returns)
        
        return float(wins / total)
    
    def _calculate_profit_loss_ratio(self, returns: pd.Series) -> float:
        """
        计算盈亏比
        平均盈利 / 平均亏损
        """
        if len(returns) < 2:
            return 0.0
        
        profits = returns[returns > 0]
        losses = returns[returns < 0]
        
        if len(profits) == 0 or len(losses) == 0:
            return 0.0
        
        avg_profit = float(profits.mean())
        avg_loss = float(abs(losses.mean()))
        
        if avg_loss == 0:
            return 0.0
        
        pl_ratio = avg_profit / avg_loss
        
        return float(pl_ratio)
    
    def _assess_risk_level(self, metrics: RiskMetrics) -> tuple:
        """
        评估风险等级
        
        Returns:
            (risk_level, risk_score)
        """
        score = 0.0
        
        # 波动率评分 (0-30分)
        if metrics.volatility > 0.5:  # >50%
            score += 30
        elif metrics.volatility > 0.3:  # >30%
            score += 20
        elif metrics.volatility > 0.15:  # >15%
            score += 10
        
        # 最大回撤评分 (0-30分)
        if metrics.max_drawdown > 0.4:  # >40%
            score += 30
        elif metrics.max_drawdown > 0.25:  # >25%
            score += 20
        elif metrics.max_drawdown > 0.15:  # >15%
            score += 10
        
        # 夏普比率评分 (0-20分，负向)
        if metrics.sharpe_ratio < 0:
            score += 20
        elif metrics.sharpe_ratio < 0.5:
            score += 15
        elif metrics.sharpe_ratio < 1.0:
            score += 10
        
        # VaR评分 (0-20分)
        if metrics.var_95 > 0.05:  # >5%
            score += 20
        elif metrics.var_95 > 0.03:  # >3%
            score += 10
        
        # 确定风险等级
        if score >= 70:
            level = "extreme"
        elif score >= 50:
            level = "high"
        elif score >= 30:
            level = "medium"
        else:
            level = "low"
        
        return level, float(score)
    
    def _create_empty_metrics(self, asset_symbol: str) -> RiskMetrics:
        """创建空的风险指标对象"""
        return RiskMetrics(
            asset_symbol=asset_symbol,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            risk_level="unknown",
            risk_score=0.0
        )

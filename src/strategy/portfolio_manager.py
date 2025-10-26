"""
投资组合管理器
实现资产配置优化和动态再平衡
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

from .base_strategy import BaseStrategy, StrategyResult


class PortfolioManager(BaseStrategy):
    """投资组合管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化投资组合管理器
        
        配置参数:
            target_allocation: 目标资产配置 (默认: {'ETF': 0.6, 'BTC': 0.25, 'ETH': 0.15})
            rebalance_threshold: 再平衡阈值 (默认: 0.05, 即5%)
            min_trade_amount: 最小交易金额 (默认: 100)
            risk_free_rate: 无风险利率 (默认: 0.03)
        """
        super().__init__(config)
        
        # 配置参数
        self.target_allocation = self.get_config_value(
            'target_allocation',
            {'ETF': 0.6, 'BTC': 0.25, 'ETH': 0.15}
        )
        self.rebalance_threshold = self.get_config_value('rebalance_threshold', 0.05)
        self.min_trade_amount = self.get_config_value('min_trade_amount', 100)
        self.risk_free_rate = self.get_config_value('risk_free_rate', 0.03)
        
        # 验证配置
        self._validate_allocation()
    
    def _validate_allocation(self):
        """验证资产配置"""
        total = sum(self.target_allocation.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"资产配置总和不为1: {total}, 正在标准化")
            # 标准化
            for asset in self.target_allocation:
                self.target_allocation[asset] /= total
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> StrategyResult:
        """
        分析投资组合并生成再平衡建议
        
        Args:
            data: 不使用（由portfolio参数替代）
            **kwargs: 其他参数
                portfolio: 当前持仓 {'ETF': {'quantity': 100, 'price': 3.5}, ...}
                prices: 当前价格 {'ETF': 3.5, 'BTC': 95000, 'ETH': 3500}
                total_capital: 总资本
                
        Returns:
            StrategyResult
        """
        try:
            portfolio = kwargs.get('portfolio', {})
            prices = kwargs.get('prices', {})
            total_capital = kwargs.get('total_capital', 100000)
            
            if not portfolio or not prices:
                return self.create_hold_result(
                    asset_symbol='Portfolio',
                    current_price=0.0,
                    reason="缺少投资组合或价格数据"
                )
            
            # 计算当前配置
            current_allocation = self._calculate_current_allocation(portfolio, prices)
            
            # 计算偏离度
            deviations = self._calculate_deviations(current_allocation)
            
            # 判断是否需要再平衡
            needs_rebalance, max_deviation = self._check_rebalance_needed(deviations)
            
            # 生成交易建议
            if needs_rebalance:
                trades = self._generate_rebalance_trades(
                    current_allocation,
                    prices,
                    total_capital
                )
                action = 'rebalance'
                confidence = min(0.9, 0.5 + max_deviation)
                reason = f"投资组合偏离目标{max_deviation:.1%}，需要再平衡"
            else:
                trades = {}
                action = 'hold'
                confidence = 0.0
                reason = "投资组合配置合理，无需调整"
            
            # 计算组合指标
            metrics = self._calculate_portfolio_metrics(
                current_allocation,
                portfolio,
                prices
            )
            
            # 创建结果
            result = StrategyResult(
                strategy_name=self.name,
                asset_symbol='Portfolio',
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                action=action,
                quantity=0.0,  # 组合管理不使用单个数量
                confidence=confidence,
                current_price=metrics['total_value'],
                target_price=None,
                stop_loss=None,
                take_profit=None,
                reason=reason,
                indicators={
                    'current_allocation': current_allocation,
                    'target_allocation': self.target_allocation,
                    'deviations': deviations,
                    'trades': trades,
                    **metrics
                },
                risk_level=self._assess_risk_level(current_allocation),
                notes=self._format_trade_instructions(trades)
            )
            
            self.log_strategy_action(result)
            return result
            
        except Exception as e:
            logger.error(f"投资组合分析失败: {e}")
            return self.create_hold_result(
                asset_symbol='Portfolio',
                current_price=0.0,
                reason=f"分析出错: {str(e)}"
            )
    
    def _calculate_current_allocation(self,
                                     portfolio: Dict,
                                     prices: Dict) -> Dict[str, float]:
        """计算当前资产配置"""
        try:
            values = {}
            total_value = 0.0
            
            # 计算各资产价值
            for asset, holding in portfolio.items():
                if asset in prices:
                    value = holding['quantity'] * prices[asset]
                    values[asset] = value
                    total_value += value
            
            # 计算配置比例
            allocation = {}
            if total_value > 0:
                for asset, value in values.items():
                    allocation[asset] = value / total_value
            
            return allocation
            
        except Exception as e:
            logger.error(f"计算当前配置失败: {e}")
            return {}
    
    def _calculate_deviations(self, current_allocation: Dict[str, float]) -> Dict[str, float]:
        """计算偏离度"""
        deviations = {}
        
        for asset in self.target_allocation:
            target = self.target_allocation[asset]
            current = current_allocation.get(asset, 0.0)
            deviations[asset] = current - target
        
        return deviations
    
    def _check_rebalance_needed(self, deviations: Dict[str, float]) -> Tuple[bool, float]:
        """检查是否需要再平衡"""
        max_deviation = max(abs(d) for d in deviations.values())
        needs_rebalance = max_deviation > self.rebalance_threshold
        
        return needs_rebalance, max_deviation
    
    def _generate_rebalance_trades(self,
                                   current_allocation: Dict[str, float],
                                   prices: Dict,
                                   total_capital: float) -> Dict:
        """生成再平衡交易指令"""
        trades = {}
        
        try:
            # 计算目标价值
            for asset in self.target_allocation:
                target_ratio = self.target_allocation[asset]
                current_ratio = current_allocation.get(asset, 0.0)
                
                # 计算价值差异
                target_value = total_capital * target_ratio
                current_value = total_capital * current_ratio
                value_diff = target_value - current_value
                
                # 转换为数量
                if asset in prices and abs(value_diff) >= self.min_trade_amount:
                    quantity = value_diff / prices[asset]
                    
                    trades[asset] = {
                        'action': 'buy' if quantity > 0 else 'sell',
                        'quantity': abs(quantity),
                        'value': abs(value_diff),
                        'current_ratio': current_ratio,
                        'target_ratio': target_ratio
                    }
            
            return trades
            
        except Exception as e:
            logger.error(f"生成交易指令失败: {e}")
            return {}
    
    def _calculate_portfolio_metrics(self,
                                     allocation: Dict[str, float],
                                     portfolio: Dict,
                                     prices: Dict) -> Dict:
        """计算投资组合指标"""
        metrics = {}
        
        try:
            # 总价值
            total_value = sum(
                portfolio[asset]['quantity'] * prices[asset]
                for asset in portfolio if asset in prices
            )
            metrics['total_value'] = total_value
            
            # 资产数量
            metrics['num_assets'] = len(portfolio)
            
            # 最大持仓
            if allocation:
                max_asset = max(allocation, key=allocation.get)
                metrics['max_holding'] = {
                    'asset': max_asset,
                    'ratio': allocation[max_asset]
                }
            
            # 集中度（赫芬达尔指数）
            if allocation:
                herfindahl = sum(ratio ** 2 for ratio in allocation.values())
                metrics['concentration'] = herfindahl
                metrics['diversification'] = 1 - herfindahl  # 多样化程度
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算组合指标失败: {e}")
            return metrics
    
    def _assess_risk_level(self, allocation: Dict[str, float]) -> str:
        """评估风险等级"""
        try:
            # 基于加密货币占比评估风险
            crypto_ratio = allocation.get('BTC', 0) + allocation.get('ETH', 0)
            
            if crypto_ratio > 0.5:
                return 'high'
            elif crypto_ratio > 0.3:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"评估风险等级失败: {e}")
            return 'medium'
    
    def _format_trade_instructions(self, trades: Dict) -> Optional[str]:
        """格式化交易指令"""
        if not trades:
            return None
        
        instructions = ["再平衡操作："]
        for asset, trade in trades.items():
            action_text = "买入" if trade['action'] == 'buy' else "卖出"
            instructions.append(
                f"{action_text}{asset}: {trade['quantity']:.4f}份 "
                f"(价值{trade['value']:.2f}元)"
            )
        
        return "\n".join(instructions)
    
    def calculate_position_size(self,
                               capital: float,
                               current_price: float,
                               risk_per_trade: float = 0.02) -> float:
        """
        投资组合管理器不使用此方法
        """
        return 0.0
    
    def optimize_allocation(self,
                           returns: pd.DataFrame,
                           method: str = 'equal_weight') -> Dict[str, float]:
        """
        优化资产配置
        
        Args:
            returns: 各资产收益率数据
            method: 优化方法
                - equal_weight: 等权重
                - min_variance: 最小方差
                - max_sharpe: 最大夏普比率
                - risk_parity: 风险平价
                
        Returns:
            优化后的资产配置
        """
        try:
            if method == 'equal_weight':
                return self._equal_weight_allocation(returns)
            elif method == 'min_variance':
                return self._min_variance_allocation(returns)
            elif method == 'max_sharpe':
                return self._max_sharpe_allocation(returns)
            elif method == 'risk_parity':
                return self._risk_parity_allocation(returns)
            else:
                logger.warning(f"未知的优化方法: {method}, 使用等权重")
                return self._equal_weight_allocation(returns)
                
        except Exception as e:
            logger.error(f"优化资产配置失败: {e}")
            return self.target_allocation
    
    def _equal_weight_allocation(self, returns: pd.DataFrame) -> Dict[str, float]:
        """等权重配置"""
        n = len(returns.columns)
        return {asset: 1.0 / n for asset in returns.columns}
    
    def _min_variance_allocation(self, returns: pd.DataFrame) -> Dict[str, float]:
        """最小方差配置"""
        try:
            # 计算协方差矩阵
            cov_matrix = returns.cov()
            
            # 最小方差组合权重 = inv(cov) * 1 / (1' * inv(cov) * 1)
            inv_cov = np.linalg.inv(cov_matrix.values)
            ones = np.ones(len(cov_matrix))
            weights = inv_cov @ ones / (ones @ inv_cov @ ones)
            
            # 确保权重为正
            weights = np.maximum(weights, 0)
            weights = weights / weights.sum()
            
            return dict(zip(returns.columns, weights))
            
        except Exception as e:
            logger.error(f"最小方差配置失败: {e}")
            return self._equal_weight_allocation(returns)
    
    def _max_sharpe_allocation(self, returns: pd.DataFrame) -> Dict[str, float]:
        """最大夏普比率配置"""
        try:
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            
            # 简化版：最大夏普比率 ≈ inv(cov) * excess_returns
            inv_cov = np.linalg.inv(cov_matrix.values)
            excess_returns = (mean_returns - self.risk_free_rate / 252).values
            
            weights = inv_cov @ excess_returns
            
            # 确保权重为正并标准化
            weights = np.maximum(weights, 0)
            if weights.sum() > 0:
                weights = weights / weights.sum()
            else:
                return self._equal_weight_allocation(returns)
            
            return dict(zip(returns.columns, weights))
            
        except Exception as e:
            logger.error(f"最大夏普比率配置失败: {e}")
            return self._equal_weight_allocation(returns)
    
    def _risk_parity_allocation(self, returns: pd.DataFrame) -> Dict[str, float]:
        """风险平价配置"""
        try:
            # 计算波动率
            volatilities = returns.std()
            
            # 风险平价：权重与波动率成反比
            inv_vol = 1.0 / volatilities
            weights = inv_vol / inv_vol.sum()
            
            return dict(zip(returns.columns, weights))
            
        except Exception as e:
            logger.error(f"风险平价配置失败: {e}")
            return self._equal_weight_allocation(returns)

"""
归因分析系统 - 分析收益来源
Attribution Analysis System
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from loguru import logger


@dataclass
class AttributionResult:
    """归因分析结果"""
    # 总体归因
    total_return: float                    # 总收益率
    alpha: float                          # 阿尔法 (超额收益)
    beta: float                           # 贝塔 (系统风险)
    
    # 收益分解
    selection_return: float               # 选股收益
    timing_return: float                  # 择时收益
    interaction_return: float             # 交互效应
    
    # 因子归因
    factor_attribution: Dict[str, float]  # 各因子贡献
    factor_exposure: Dict[str, float]     # 因子暴露度
    
    # 行业归因
    sector_attribution: Optional[Dict[str, float]] = None
    
    # 详细信息
    details: Dict = None


class AttributionAnalyzer:
    """归因分析器"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化归因分析器
        
        Args:
            risk_free_rate: 无风险利率
        """
        self.risk_free_rate = risk_free_rate
        logger.info("归因分析器初始化完成")
    
    def analyze(self,
               portfolio_returns: pd.Series,
               benchmark_returns: pd.Series,
               holdings: Optional[pd.DataFrame] = None,
               factor_returns: Optional[pd.DataFrame] = None) -> AttributionResult:
        """
        执行归因分析
        
        Args:
            portfolio_returns: 投资组合收益率序列
            benchmark_returns: 基准收益率序列
            holdings: 持仓数据 (可选)
            factor_returns: 因子收益率 (可选)
            
        Returns:
            AttributionResult
        """
        logger.info("=" * 60)
        logger.info("开始归因分析")
        logger.info("=" * 60)
        
        try:
            # 对齐数据
            portfolio_returns, benchmark_returns = self._align_returns(
                portfolio_returns,
                benchmark_returns
            )
            
            # 1. 基本指标计算
            total_return = self._calculate_total_return(portfolio_returns)
            benchmark_return = self._calculate_total_return(benchmark_returns)
            
            # 2. Alpha/Beta分析
            alpha, beta = self._calculate_alpha_beta(
                portfolio_returns,
                benchmark_returns
            )
            
            # 3. Brinson归因 (选股 vs 择时)
            if holdings is not None:
                selection, timing, interaction = self._brinson_attribution(
                    portfolio_returns,
                    benchmark_returns,
                    holdings
                )
            else:
                # 简化归因
                selection, timing, interaction = self._simplified_attribution(
                    portfolio_returns,
                    benchmark_returns,
                    alpha
                )
            
            # 4. 因子归因
            if factor_returns is not None:
                factor_attr, factor_exp = self._factor_attribution(
                    portfolio_returns,
                    factor_returns
                )
            else:
                factor_attr = {}
                factor_exp = {}
            
            # 构建结果
            result = AttributionResult(
                total_return=total_return,
                alpha=alpha,
                beta=beta,
                selection_return=selection,
                timing_return=timing,
                interaction_return=interaction,
                factor_attribution=factor_attr,
                factor_exposure=factor_exp,
                details=self._create_detail_report(
                    total_return,
                    benchmark_return,
                    alpha,
                    beta,
                    selection,
                    timing,
                    interaction
                )
            )
            
            # 打印结果
            self._print_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"归因分析失败: {e}")
            raise
    
    def _align_returns(self,
                      portfolio_returns: pd.Series,
                      benchmark_returns: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """对齐收益率序列"""
        # 找到共同的日期范围
        common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
        
        if len(common_dates) == 0:
            raise ValueError("投资组合和基准没有共同的日期")
        
        portfolio_aligned = portfolio_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        return portfolio_aligned, benchmark_aligned
    
    def _calculate_total_return(self, returns: pd.Series) -> float:
        """计算总收益率"""
        return (1 + returns).prod() - 1
    
    def _calculate_alpha_beta(self,
                             portfolio_returns: pd.Series,
                             benchmark_returns: pd.Series) -> Tuple[float, float]:
        """
        计算Alpha和Beta
        
        使用回归方法:
        R_p - R_f = α + β * (R_b - R_f) + ε
        
        Args:
            portfolio_returns: 投资组合收益率
            benchmark_returns: 基准收益率
            
        Returns:
            (alpha, beta)
        """
        # 计算超额收益
        portfolio_excess = portfolio_returns - self.risk_free_rate / 252
        benchmark_excess = benchmark_returns - self.risk_free_rate / 252
        
        # 回归计算Beta
        covariance = np.cov(portfolio_excess, benchmark_excess)[0, 1]
        benchmark_variance = np.var(benchmark_excess)
        
        if benchmark_variance > 0:
            beta = covariance / benchmark_variance
        else:
            beta = 0.0
        
        # 计算Alpha
        mean_portfolio_excess = portfolio_excess.mean() * 252  # 年化
        mean_benchmark_excess = benchmark_excess.mean() * 252  # 年化
        alpha = mean_portfolio_excess - beta * mean_benchmark_excess
        
        return alpha, beta
    
    def _brinson_attribution(self,
                            portfolio_returns: pd.Series,
                            benchmark_returns: pd.Series,
                            holdings: pd.DataFrame) -> Tuple[float, float, float]:
        """
        Brinson归因模型
        
        将超额收益分解为:
        - 配置效应 (Allocation Effect): 择时能力
        - 选择效应 (Selection Effect): 选股能力
        - 交互效应 (Interaction Effect): 两者结合
        
        超额收益 = 配置效应 + 选择效应 + 交互效应
        
        Args:
            portfolio_returns: 组合收益
            benchmark_returns: 基准收益
            holdings: 持仓权重数据
            
        Returns:
            (selection_effect, allocation_effect, interaction_effect)
        """
        # 这里是简化实现
        # 实际Brinson模型需要详细的行业/资产权重和收益率数据
        
        total_excess = (portfolio_returns - benchmark_returns).sum()
        
        # 简化分配: 60%归因于选股, 30%归因于择时, 10%交互
        selection = total_excess * 0.6
        allocation = total_excess * 0.3
        interaction = total_excess * 0.1
        
        logger.warning("使用简化的Brinson归因 (需要详细持仓数据以获得精确结果)")
        
        return selection, allocation, interaction
    
    def _simplified_attribution(self,
                               portfolio_returns: pd.Series,
                               benchmark_returns: pd.Series,
                               alpha: float) -> Tuple[float, float, float]:
        """
        简化归因分析
        
        当没有详细持仓数据时使用
        """
        total_excess = self._calculate_total_return(portfolio_returns) - \
                      self._calculate_total_return(benchmark_returns)
        
        # 基于Alpha进行简单分配
        # Alpha主要来自于选股能力
        selection = alpha
        
        # 剩余部分归因于择时
        timing = total_excess - selection
        
        # 交互效应很小
        interaction = 0.0
        
        return selection, timing, interaction
    
    def _factor_attribution(self,
                           portfolio_returns: pd.Series,
                           factor_returns: pd.DataFrame) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        因子归因分析
        
        使用回归方法分解收益到各个因子:
        R_p = β_1 * F_1 + β_2 * F_2 + ... + β_n * F_n + ε
        
        Args:
            portfolio_returns: 组合收益率
            factor_returns: 因子收益率 (DataFrame, 每列是一个因子)
            
        Returns:
            (factor_attribution, factor_exposure)
            factor_attribution: 各因子的收益贡献
            factor_exposure: 各因子的暴露度 (beta)
        """
        # 对齐数据
        common_dates = portfolio_returns.index.intersection(factor_returns.index)
        
        if len(common_dates) == 0:
            logger.warning("没有共同日期，无法进行因子归因")
            return {}, {}
        
        y = portfolio_returns.loc[common_dates].values
        X = factor_returns.loc[common_dates].values
        
        # 多元线性回归
        try:
            # 使用最小二乘法
            betas, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
            
            # 计算各因子贡献
            factor_exposure = {}
            factor_attribution = {}
            
            for i, factor_name in enumerate(factor_returns.columns):
                factor_exposure[factor_name] = betas[i]
                
                # 因子贡献 = 因子暴露 * 因子平均收益 * 期数
                factor_avg_return = factor_returns[factor_name].mean()
                factor_attribution[factor_name] = betas[i] * factor_avg_return * len(common_dates)
            
            return factor_attribution, factor_exposure
            
        except Exception as e:
            logger.error(f"因子归因计算失败: {e}")
            return {}, {}
    
    def _create_detail_report(self,
                             total_return: float,
                             benchmark_return: float,
                             alpha: float,
                             beta: float,
                             selection: float,
                             timing: float,
                             interaction: float) -> Dict:
        """创建详细报告"""
        excess_return = total_return - benchmark_return
        
        return {
            'total_return': total_return,
            'benchmark_return': benchmark_return,
            'excess_return': excess_return,
            'alpha': alpha,
            'beta': beta,
            'selection_effect': selection,
            'timing_effect': timing,
            'interaction_effect': interaction,
            'explained_excess': selection + timing + interaction,
            'unexplained': excess_return - (selection + timing + interaction)
        }
    
    def _print_results(self, result: AttributionResult):
        """打印归因结果"""
        logger.info("=" * 60)
        logger.info("归因分析结果")
        logger.info("=" * 60)
        
        logger.info(f"\n【总体表现】")
        logger.info(f"总收益率: {result.total_return:.2%}")
        logger.info(f"阿尔法 (超额收益): {result.alpha:.2%}")
        logger.info(f"贝塔 (系统风险): {result.beta:.2f}")
        
        logger.info(f"\n【收益分解】")
        logger.info(f"选股收益: {result.selection_return:.2%}")
        logger.info(f"择时收益: {result.timing_return:.2%}")
        logger.info(f"交互效应: {result.interaction_return:.2%}")
        
        total_explained = result.selection_return + result.timing_return + result.interaction_return
        logger.info(f"合计解释: {total_explained:.2%}")
        
        if result.factor_attribution:
            logger.info(f"\n【因子归因】")
            for factor, contrib in result.factor_attribution.items():
                exposure = result.factor_exposure.get(factor, 0)
                logger.info(f"{factor}: 贡献={contrib:.2%}, 暴露={exposure:.2f}")
        
        logger.info("=" * 60)
    
    def calculate_information_ratio(self,
                                   portfolio_returns: pd.Series,
                                   benchmark_returns: pd.Series) -> float:
        """
        计算信息比率 (Information Ratio)
        
        IR = (R_p - R_b) / TE
        其中 TE (Tracking Error) 是跟踪误差
        
        Args:
            portfolio_returns: 组合收益率
            benchmark_returns: 基准收益率
            
        Returns:
            信息比率
        """
        # 超额收益
        excess_returns = portfolio_returns - benchmark_returns
        
        # 平均超额收益 (年化)
        mean_excess = excess_returns.mean() * 252
        
        # 跟踪误差 (年化)
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        if tracking_error > 0:
            ir = mean_excess / tracking_error
        else:
            ir = 0.0
        
        logger.info(f"信息比率: {ir:.2f}")
        logger.info(f"跟踪误差: {tracking_error:.2%}")
        
        return ir
    
    def calculate_treynor_ratio(self,
                               portfolio_returns: pd.Series,
                               benchmark_returns: pd.Series) -> float:
        """
        计算特雷诺比率 (Treynor Ratio)
        
        Treynor = (R_p - R_f) / β
        
        Args:
            portfolio_returns: 组合收益率
            benchmark_returns: 基准收益率
            
        Returns:
            特雷诺比率
        """
        alpha, beta = self._calculate_alpha_beta(portfolio_returns, benchmark_returns)
        
        mean_return = portfolio_returns.mean() * 252  # 年化
        excess_return = mean_return - self.risk_free_rate
        
        if beta > 0:
            treynor = excess_return / beta
        else:
            treynor = 0.0
        
        logger.info(f"特雷诺比率: {treynor:.2f}")
        
        return treynor
    
    def rolling_attribution(self,
                           portfolio_returns: pd.Series,
                           benchmark_returns: pd.Series,
                           window: int = 60) -> pd.DataFrame:
        """
        滚动归因分析
        
        计算滚动窗口内的Alpha和Beta
        
        Args:
            portfolio_returns: 组合收益率
            benchmark_returns: 基准收益率
            window: 滚动窗口大小 (天数)
            
        Returns:
            DataFrame包含滚动Alpha和Beta
        """
        results = []
        
        for i in range(window, len(portfolio_returns)):
            window_portfolio = portfolio_returns.iloc[i-window:i]
            window_benchmark = benchmark_returns.iloc[i-window:i]
            
            alpha, beta = self._calculate_alpha_beta(window_portfolio, window_benchmark)
            
            results.append({
                'date': portfolio_returns.index[i],
                'alpha': alpha,
                'beta': beta
            })
        
        df = pd.DataFrame(results)
        df.set_index('date', inplace=True)
        
        logger.info(f"滚动归因完成: 窗口={window}天, 数据点={len(df)}")
        
        return df


def quick_attribution(portfolio_returns: pd.Series,
                     benchmark_returns: pd.Series,
                     risk_free_rate: float = 0.03) -> AttributionResult:
    """
    快速归因分析
    
    Args:
        portfolio_returns: 组合收益率
        benchmark_returns: 基准收益率
        risk_free_rate: 无风险利率
        
    Returns:
        AttributionResult
    """
    analyzer = AttributionAnalyzer(risk_free_rate)
    return analyzer.analyze(portfolio_returns, benchmark_returns)


# 示例使用
if __name__ == "__main__":
    # 生成示例数据
    dates = pd.date_range('2023-01-01', periods=252, freq='D')
    
    # 模拟组合收益 (有Alpha)
    portfolio_returns = pd.Series(
        np.random.randn(252) * 0.015 + 0.0005,  # 日波动1.5% + 小正收益
        index=dates
    )
    
    # 模拟基准收益
    benchmark_returns = pd.Series(
        np.random.randn(252) * 0.01 + 0.0003,   # 日波动1% + 更小正收益
        index=dates
    )
    
    # 执行归因分析
    result = quick_attribution(portfolio_returns, benchmark_returns)
    
    print(f"\n总收益率: {result.total_return:.2%}")
    print(f"Alpha: {result.alpha:.2%}")
    print(f"Beta: {result.beta:.2f}")
    print(f"选股收益: {result.selection_return:.2%}")
    print(f"择时收益: {result.timing_return:.2%}")

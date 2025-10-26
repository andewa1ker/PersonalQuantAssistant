"""
波动率分析器
提供波动率相关指标和风险评估
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger


class VolatilityAnalyzer:
    """波动率分析器"""
    
    def __init__(self):
        """初始化波动率分析器"""
        logger.info("初始化波动率分析器")
    
    def calculate_historical_volatility(self, data: pd.DataFrame, period: int = 20) -> Dict:
        """
        计算历史波动率
        
        Args:
            data: 价格数据
            period: 计算周期
            
        Returns:
            波动率信息
        """
        try:
            df = data.copy()
            
            # 计算日收益率
            df['returns'] = df['close'].pct_change()
            
            # 计算滚动标准差（年化波动率）
            df['volatility'] = df['returns'].rolling(window=period).std() * np.sqrt(252)
            
            current_vol = df['volatility'].iloc[-1] * 100
            avg_vol = df['volatility'].tail(60).mean() * 100
            
            # 判断波动率水平
            if current_vol > avg_vol * 1.5:
                vol_level = "高波动"
            elif current_vol > avg_vol * 0.7:
                vol_level = "正常波动"
            else:
                vol_level = "低波动"
            
            result = {
                'current_volatility': round(current_vol, 2),
                'average_volatility': round(avg_vol, 2),
                'volatility_level': vol_level,
                'period': period
            }
            
            logger.debug(f"历史波动率: {current_vol:.2f}%, 级别: {vol_level}")
            return result
            
        except Exception as e:
            logger.error(f"计算历史波动率失败: {e}")
            return {'current_volatility': 0, 'volatility_level': '未知'}
    
    def calculate_parkinson_volatility(self, data: pd.DataFrame, period: int = 20) -> float:
        """
        计算Parkinson波动率（使用高低价）
        比简单波动率更准确
        
        Args:
            data: 价格数据，需要有high和low列
            period: 计算周期
            
        Returns:
            Parkinson波动率
        """
        try:
            df = data.tail(period).copy()
            
            # Parkinson公式
            hl_ratio = np.log(df['high'] / df['low']) ** 2
            parkinson_vol = np.sqrt(hl_ratio.mean() / (4 * np.log(2))) * np.sqrt(252)
            
            logger.debug(f"Parkinson波动率: {parkinson_vol * 100:.2f}%")
            return parkinson_vol
            
        except Exception as e:
            logger.error(f"计算Parkinson波动率失败: {e}")
            return 0.0
    
    def analyze_volatility_regime(self, data: pd.DataFrame) -> Dict:
        """
        分析波动率状态
        
        Args:
            data: 价格数据
            
        Returns:
            波动率状态分析
        """
        try:
            df = data.copy()
            
            # 计算短期和长期波动率
            df['returns'] = df['close'].pct_change()
            short_vol = df['returns'].tail(10).std() * np.sqrt(252) * 100
            medium_vol = df['returns'].tail(30).std() * np.sqrt(252) * 100
            long_vol = df['returns'].tail(60).std() * np.sqrt(252) * 100
            
            # 波动率趋势
            if short_vol > medium_vol > long_vol:
                trend = "波动率上升"
                regime = "expanding"
            elif short_vol < medium_vol < long_vol:
                trend = "波动率下降"
                regime = "contracting"
            else:
                trend = "波动率稳定"
                regime = "stable"
            
            # 计算波动率百分位
            all_vols = df['returns'].rolling(window=20).std().dropna() * np.sqrt(252) * 100
            current_vol = short_vol
            percentile = (all_vols < current_vol).sum() / len(all_vols) * 100
            
            result = {
                'short_term_vol': round(short_vol, 2),
                'medium_term_vol': round(medium_vol, 2),
                'long_term_vol': round(long_vol, 2),
                'trend': trend,
                'regime': regime,
                'percentile': round(percentile, 1)
            }
            
            logger.debug(f"波动率状态: {trend}, 百分位: {percentile:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"分析波动率状态失败: {e}")
            return {'trend': '未知', 'regime': 'unknown'}
    
    def calculate_bollinger_squeeze(self, data: pd.DataFrame, period: int = 20) -> Dict:
        """
        检测布林带挤压（Bollinger Squeeze）
        布林带收窄通常预示着即将出现大行情
        
        Args:
            data: 包含布林带数据的DataFrame
            period: 分析周期
            
        Returns:
            挤压状态信息
        """
        try:
            df = data.copy()
            
            # 确保有布林带数据
            if 'BOLL_WIDTH' not in df.columns:
                # 计算布林带宽度
                ma = df['close'].rolling(window=period).mean()
                std = df['close'].rolling(window=period).std()
                df['BOLL_WIDTH'] = (std * 2 / ma * 100)
            
            current_width = df['BOLL_WIDTH'].iloc[-1]
            avg_width = df['BOLL_WIDTH'].tail(100).mean()
            
            # 判断挤压状态
            if current_width < avg_width * 0.5:
                squeeze_status = "强挤压"
                description = "布林带极度收窄，可能即将突破"
            elif current_width < avg_width * 0.7:
                squeeze_status = "挤压"
                description = "布林带收窄，关注突破方向"
            elif current_width > avg_width * 1.5:
                squeeze_status = "扩张"
                description = "布林带扩张，波动率上升"
            else:
                squeeze_status = "正常"
                description = "布林带宽度正常"
            
            result = {
                'current_width': round(current_width, 2),
                'average_width': round(avg_width, 2),
                'squeeze_status': squeeze_status,
                'description': description
            }
            
            logger.debug(f"布林带挤压: {squeeze_status}")
            return result
            
        except Exception as e:
            logger.error(f"检测布林带挤压失败: {e}")
            return {'squeeze_status': '未知'}
    
    def calculate_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """
        计算风险指标
        
        Args:
            data: 价格数据
            
        Returns:
            风险指标字典
        """
        try:
            df = data.copy()
            df['returns'] = df['close'].pct_change()
            
            # 最大回撤
            cumulative = (1 + df['returns']).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # 夏普比率 (假设无风险利率为3%)
            risk_free_rate = 0.03 / 252  # 日无风险利率
            excess_returns = df['returns'] - risk_free_rate
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            
            # Value at Risk (95%置信度)
            var_95 = df['returns'].quantile(0.05) * 100
            
            # 上行/下行波动率
            positive_returns = df['returns'][df['returns'] > 0]
            negative_returns = df['returns'][df['returns'] < 0]
            
            upside_vol = positive_returns.std() * np.sqrt(252) * 100 if len(positive_returns) > 0 else 0
            downside_vol = negative_returns.std() * np.sqrt(252) * 100 if len(negative_returns) > 0 else 0
            
            result = {
                'max_drawdown': round(max_drawdown, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'var_95': round(var_95, 2),
                'upside_volatility': round(upside_vol, 2),
                'downside_volatility': round(downside_vol, 2)
            }
            
            logger.debug(f"风险指标: 最大回撤={max_drawdown:.2f}%, 夏普={sharpe_ratio:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}
    
    def get_volatility_summary(self, data: pd.DataFrame) -> Dict:
        """
        获取波动率综合分析
        
        Args:
            data: 价格数据
            
        Returns:
            综合波动率分析
        """
        try:
            hist_vol = self.calculate_historical_volatility(data)
            parkinson_vol = self.calculate_parkinson_volatility(data)
            regime = self.analyze_volatility_regime(data)
            squeeze = self.calculate_bollinger_squeeze(data)
            risk_metrics = self.calculate_risk_metrics(data)
            
            summary = {
                'historical_volatility': hist_vol,
                'parkinson_volatility': round(parkinson_vol * 100, 2),
                'volatility_regime': regime,
                'bollinger_squeeze': squeeze,
                'risk_metrics': risk_metrics,
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info("生成波动率综合分析成功")
            return summary
            
        except Exception as e:
            logger.error(f"生成波动率综合分析失败: {e}")
            return {}

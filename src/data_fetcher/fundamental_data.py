"""
基本面数据获取模块 - 财报、估值、行业数据
Fundamental Data Fetcher
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

try:
    import akshare as ak
except ImportError:
    logger.warning("AKShare未安装，部分功能不可用")
    ak = None


class FundamentalDataFetcher:
    """基本面数据获取器"""
    
    def __init__(self):
        """初始化基本面数据获取器"""
        self.cache = {}
        logger.info("基本面数据获取器初始化完成")
    
    def get_financial_statement(self,
                               symbol: str,
                               statement_type: str = 'income',
                               period: str = 'annual') -> Optional[pd.DataFrame]:
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
            statement_type: 报表类型 ('income', 'balance', 'cashflow')
            period: 报告期 ('annual'年报, 'quarter'季报)
            
        Returns:
            财务报表DataFrame
        """
        if ak is None:
            logger.error("AKShare未安装")
            return None
        
        try:
            logger.info(f"获取财务报表: {symbol} | {statement_type} | {period}")
            
            if statement_type == 'income':
                # 利润表
                df = ak.stock_financial_report_sina(stock=symbol, symbol="利润表")
            elif statement_type == 'balance':
                # 资产负债表
                df = ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
            elif statement_type == 'cashflow':
                # 现金流量表
                df = ak.stock_financial_report_sina(stock=symbol, symbol="现金流量表")
            else:
                logger.error(f"不支持的报表类型: {statement_type}")
                return None
            
            logger.info(f"成功获取财务报表: {len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取财务报表失败: {e}")
            return None
    
    def get_valuation_metrics(self, symbol: str) -> Optional[Dict]:
        """
        获取估值指标
        
        Args:
            symbol: 股票代码
            
        Returns:
            估值指标字典
        """
        if ak is None:
            logger.error("AKShare未安装")
            return None
        
        try:
            logger.info(f"获取估值指标: {symbol}")
            
            # 获取实时数据 (包含PE/PB)
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol]
            
            if stock_data.empty:
                logger.warning(f"未找到股票: {symbol}")
                return None
            
            row = stock_data.iloc[0]
            
            metrics = {
                'symbol': symbol,
                'name': row.get('名称', 'N/A'),
                'price': row.get('最新价', 0),
                'pe_ratio': row.get('市盈率-动态', 0),
                'pb_ratio': row.get('市净率', 0),
                'market_cap': row.get('总市值', 0),
                'circulating_cap': row.get('流通市值', 0),
                'pe_ttm': row.get('市盈率-动态', 0),  # TTM市盈率
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 计算额外指标
            metrics['ps_ratio'] = self._calculate_ps_ratio(symbol)
            metrics['dividend_yield'] = self._get_dividend_yield(symbol)
            
            logger.info(f"估值指标: PE={metrics['pe_ratio']:.2f}, PB={metrics['pb_ratio']:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取估值指标失败: {e}")
            return None
    
    def get_valuation_history(self,
                             symbol: str,
                             indicator: str = 'pe',
                             start_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        获取估值历史数据
        
        Args:
            symbol: 股票代码
            indicator: 指标类型 ('pe', 'pb', 'ps')
            start_date: 开始日期
            
        Returns:
            估值历史DataFrame
        """
        if ak is None:
            return None
        
        try:
            logger.info(f"获取估值历史: {symbol} | {indicator}")
            
            # 获取历史PE/PB数据
            df = ak.stock_a_indicator_lg(symbol=symbol)
            
            if df is None or df.empty:
                logger.warning(f"未找到估值历史: {symbol}")
                return None
            
            # 过滤日期
            if start_date:
                df = df[df['trade_date'] >= start_date]
            
            # 选择指标
            columns_map = {
                'pe': 'pe_ttm',
                'pb': 'pb',
                'ps': 'ps_ttm'
            }
            
            if indicator in columns_map:
                indicator_col = columns_map[indicator]
                if indicator_col in df.columns:
                    result = df[['trade_date', indicator_col]].copy()
                    result.columns = ['date', indicator]
                    result.set_index('date', inplace=True)
                    
                    logger.info(f"估值历史数据: {len(result)}条")
                    return result
            
            return df
            
        except Exception as e:
            logger.error(f"获取估值历史失败: {e}")
            return None
    
    def calculate_valuation_percentile(self,
                                       symbol: str,
                                       indicator: str = 'pe',
                                       lookback_days: int = 1000) -> Optional[Dict]:
        """
        计算估值分位数
        
        Args:
            symbol: 股票代码
            indicator: 指标 ('pe', 'pb', 'ps')
            lookback_days: 回溯天数
            
        Returns:
            分位数信息
        """
        try:
            # 获取历史数据
            start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y%m%d')
            hist_df = self.get_valuation_history(symbol, indicator, start_date)
            
            if hist_df is None or hist_df.empty:
                return None
            
            # 当前值
            current_metrics = self.get_valuation_metrics(symbol)
            if current_metrics is None:
                return None
            
            indicator_key = f"{indicator}_ratio"
            current_value = current_metrics.get(indicator_key, 0)
            
            if current_value <= 0:
                logger.warning(f"当前{indicator}值无效: {current_value}")
                return None
            
            # 计算分位数
            hist_values = hist_df[indicator].dropna()
            percentile = (hist_values < current_value).sum() / len(hist_values) * 100
            
            result = {
                'symbol': symbol,
                'indicator': indicator,
                'current_value': current_value,
                'percentile': percentile,
                'min': hist_values.min(),
                'max': hist_values.max(),
                'mean': hist_values.mean(),
                'median': hist_values.median(),
                'std': hist_values.std(),
                'lookback_days': lookback_days,
                'data_points': len(hist_values)
            }
            
            # 估值水平判断
            if percentile < 20:
                result['level'] = '低估'
            elif percentile < 40:
                result['level'] = '偏低'
            elif percentile < 60:
                result['level'] = '合理'
            elif percentile < 80:
                result['level'] = '偏高'
            else:
                result['level'] = '高估'
            
            logger.info(f"估值分位数: {indicator}={current_value:.2f} "
                       f"({percentile:.1f}%, {result['level']})")
            
            return result
            
        except Exception as e:
            logger.error(f"计算估值分位数失败: {e}")
            return None
    
    def get_industry_comparison(self, symbol: str) -> Optional[Dict]:
        """
        获取行业对比数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            行业对比数据
        """
        if ak is None:
            return None
        
        try:
            logger.info(f"获取行业对比: {symbol}")
            
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            
            if stock_info.empty:
                return None
            
            # 提取行业信息
            industry_row = stock_info[stock_info['item'] == '行业']
            if industry_row.empty:
                logger.warning(f"未找到行业信息: {symbol}")
                return None
            
            industry = industry_row.iloc[0]['value']
            
            # 获取行业平均估值 (简化实现)
            comparison = {
                'symbol': symbol,
                'industry': industry,
                'stock_pe': 0,
                'industry_avg_pe': 0,
                'relative_pe': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d')
            }
            
            # 获取个股估值
            metrics = self.get_valuation_metrics(symbol)
            if metrics:
                comparison['stock_pe'] = metrics.get('pe_ratio', 0)
                comparison['stock_pb'] = metrics.get('pb_ratio', 0)
            
            logger.info(f"行业对比: {industry}")
            
            return comparison
            
        except Exception as e:
            logger.error(f"获取行业对比失败: {e}")
            return None
    
    def get_financial_indicators(self, symbol: str) -> Optional[Dict]:
        """
        获取财务指标
        
        Args:
            symbol: 股票代码
            
        Returns:
            财务指标字典
        """
        if ak is None:
            return None
        
        try:
            logger.info(f"获取财务指标: {symbol}")
            
            # 获取主要财务指标
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            if df is None or df.empty:
                logger.warning(f"未找到财务指标: {symbol}")
                return None
            
            # 取最新一期数据
            latest = df.iloc[0]
            
            indicators = {
                'symbol': symbol,
                'report_date': latest.get('报告期', 'N/A'),
                # 盈利能力
                'roe': latest.get('净资产收益率', 0),        # ROE
                'roa': latest.get('总资产净利率', 0),         # ROA
                'gross_margin': latest.get('销售毛利率', 0),  # 毛利率
                'net_margin': latest.get('销售净利率', 0),    # 净利率
                # 营运能力
                'asset_turnover': latest.get('总资产周转率', 0),
                'inventory_turnover': latest.get('存货周转率', 0),
                # 偿债能力
                'debt_ratio': latest.get('资产负债率', 0),
                'current_ratio': latest.get('流动比率', 0),
                'quick_ratio': latest.get('速动比率', 0),
                # 成长能力
                'revenue_growth': latest.get('营业收入增长率', 0),
                'profit_growth': latest.get('净利润增长率', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d')
            }
            
            logger.info(f"财务指标: ROE={indicators['roe']:.2f}%, "
                       f"负债率={indicators['debt_ratio']:.2f}%")
            
            return indicators
            
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return None
    
    def _calculate_ps_ratio(self, symbol: str) -> float:
        """计算市销率"""
        try:
            # 简化实现
            return 0.0
        except:
            return 0.0
    
    def _get_dividend_yield(self, symbol: str) -> float:
        """获取股息率"""
        try:
            # 简化实现
            return 0.0
        except:
            return 0.0
    
    def get_comprehensive_analysis(self, symbol: str) -> Optional[Dict]:
        """
        获取综合分析
        
        Args:
            symbol: 股票代码
            
        Returns:
            综合分析数据
        """
        try:
            logger.info(f"=" * 60)
            logger.info(f"综合分析: {symbol}")
            logger.info(f"=" * 60)
            
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 1. 估值指标
            valuation = self.get_valuation_metrics(symbol)
            if valuation:
                analysis['valuation'] = valuation
            
            # 2. 估值分位数
            pe_percentile = self.calculate_valuation_percentile(symbol, 'pe')
            if pe_percentile:
                analysis['pe_percentile'] = pe_percentile
            
            pb_percentile = self.calculate_valuation_percentile(symbol, 'pb')
            if pb_percentile:
                analysis['pb_percentile'] = pb_percentile
            
            # 3. 财务指标
            financial = self.get_financial_indicators(symbol)
            if financial:
                analysis['financial'] = financial
            
            # 4. 行业对比
            industry = self.get_industry_comparison(symbol)
            if industry:
                analysis['industry'] = industry
            
            # 5. 综合评分
            analysis['score'] = self._calculate_comprehensive_score(analysis)
            
            logger.info(f"综合分析完成")
            logger.info(f"=" * 60)
            
            return analysis
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return None
    
    def _calculate_comprehensive_score(self, analysis: Dict) -> Dict:
        """计算综合评分"""
        scores = {
            'valuation_score': 50,     # 估值得分 (0-100)
            'profitability_score': 50,  # 盈利能力得分
            'growth_score': 50,         # 成长能力得分
            'safety_score': 50,         # 安全性得分
            'total_score': 50           # 总分
        }
        
        # 估值评分
        if 'pe_percentile' in analysis:
            pe_pct = analysis['pe_percentile'].get('percentile', 50)
            # 分位数越低越好
            scores['valuation_score'] = 100 - pe_pct
        
        # 盈利能力评分
        if 'financial' in analysis:
            fin = analysis['financial']
            roe = fin.get('roe', 0)
            net_margin = fin.get('net_margin', 0)
            
            # ROE > 15% 优秀, < 5% 较差
            roe_score = min(100, max(0, (roe - 5) / 10 * 100))
            margin_score = min(100, max(0, (net_margin) * 5))
            
            scores['profitability_score'] = (roe_score + margin_score) / 2
        
        # 成长能力评分
        if 'financial' in analysis:
            fin = analysis['financial']
            revenue_growth = fin.get('revenue_growth', 0)
            profit_growth = fin.get('profit_growth', 0)
            
            # 增长率 > 20% 优秀
            rev_score = min(100, max(0, (revenue_growth + 10) * 2.5))
            profit_score = min(100, max(0, (profit_growth + 10) * 2.5))
            
            scores['growth_score'] = (rev_score + profit_score) / 2
        
        # 安全性评分
        if 'financial' in analysis:
            fin = analysis['financial']
            debt_ratio = fin.get('debt_ratio', 0)
            current_ratio = fin.get('current_ratio', 0)
            
            # 负债率 < 50% 好, > 70% 差
            debt_score = min(100, max(0, (70 - debt_ratio) * 2))
            # 流动比率 > 2 好
            liquidity_score = min(100, current_ratio / 2 * 100)
            
            scores['safety_score'] = (debt_score + liquidity_score) / 2
        
        # 总分
        weights = {
            'valuation_score': 0.3,
            'profitability_score': 0.3,
            'growth_score': 0.2,
            'safety_score': 0.2
        }
        
        total = sum(scores[k] * weights[k] for k in weights.keys())
        scores['total_score'] = total
        
        # 评级
        if total >= 80:
            scores['rating'] = 'A'
        elif total >= 60:
            scores['rating'] = 'B'
        elif total >= 40:
            scores['rating'] = 'C'
        else:
            scores['rating'] = 'D'
        
        return scores


# 便捷函数
def get_stock_fundamentals(symbol: str) -> Optional[Dict]:
    """
    快速获取股票基本面数据
    
    Args:
        symbol: 股票代码
        
    Returns:
        基本面数据
    """
    fetcher = FundamentalDataFetcher()
    return fetcher.get_comprehensive_analysis(symbol)

"""
技术分析器
提供常用技术指标的计算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger


class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self):
        """初始化技术分析器"""
        logger.info("初始化技术分析器")
    
    def calculate_ma(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        计算移动平均线 (MA)
        
        Args:
            data: 包含价格数据的DataFrame，需要有'close'列
            periods: MA周期列表，默认[5, 10, 20, 60]
            
        Returns:
            包含MA数据的DataFrame
        """
        try:
            df = data.copy()
            
            for period in periods:
                df[f'MA{period}'] = df['close'].rolling(window=period).mean()
            
            logger.debug(f"计算MA成功，周期: {periods}")
            return df
            
        except Exception as e:
            logger.error(f"计算MA失败: {e}")
            return data
    
    def calculate_ema(self, data: pd.DataFrame, periods: List[int] = [12, 26]) -> pd.DataFrame:
        """
        计算指数移动平均线 (EMA)
        
        Args:
            data: 包含价格数据的DataFrame
            periods: EMA周期列表
            
        Returns:
            包含EMA数据的DataFrame
        """
        try:
            df = data.copy()
            
            for period in periods:
                df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
            logger.debug(f"计算EMA成功，周期: {periods}")
            return df
            
        except Exception as e:
            logger.error(f"计算EMA失败: {e}")
            return data
    
    def calculate_macd(self, data: pd.DataFrame, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> pd.DataFrame:
        """
        计算MACD指标 (Moving Average Convergence Divergence)
        
        Args:
            data: 价格数据
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9
            
        Returns:
            包含MACD、Signal、Histogram的DataFrame
        """
        try:
            df = data.copy()
            
            # 计算快慢EMA
            ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
            ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
            
            # MACD = 快线 - 慢线
            df['MACD'] = ema_fast - ema_slow
            
            # Signal线 = MACD的EMA
            df['MACD_Signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
            
            # 柱状图 = MACD - Signal
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            logger.debug("计算MACD成功")
            return df
            
        except Exception as e:
            logger.error(f"计算MACD失败: {e}")
            return data
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算相对强弱指标 (RSI)
        
        Args:
            data: 价格数据
            period: RSI周期，默认14
            
        Returns:
            包含RSI的DataFrame
        """
        try:
            df = data.copy()
            
            # 计算价格变化
            delta = df['close'].diff()
            
            # 分离上涨和下跌
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # 计算RS和RSI
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            logger.debug(f"计算RSI成功，周期: {period}")
            return df
            
        except Exception as e:
            logger.error(f"计算RSI失败: {e}")
            return data
    
    def calculate_kdj(self, data: pd.DataFrame, 
                     n: int = 9, 
                     m1: int = 3, 
                     m2: int = 3) -> pd.DataFrame:
        """
        计算KDJ指标 (Stochastic Oscillator)
        
        Args:
            data: 价格数据，需要有high、low、close列
            n: RSV周期，默认9
            m1: K值平滑周期，默认3
            m2: D值平滑周期，默认3
            
        Returns:
            包含K、D、J的DataFrame
        """
        try:
            df = data.copy()
            
            # 计算RSV (未成熟随机值)
            low_n = df['low'].rolling(window=n).min()
            high_n = df['high'].rolling(window=n).max()
            rsv = (df['close'] - low_n) / (high_n - low_n) * 100
            
            # 计算K、D、J
            df['K'] = rsv.ewm(com=m1-1, adjust=False).mean()
            df['D'] = df['K'].ewm(com=m2-1, adjust=False).mean()
            df['J'] = 3 * df['K'] - 2 * df['D']
            
            logger.debug(f"计算KDJ成功，参数: n={n}, m1={m1}, m2={m2}")
            return df
            
        except Exception as e:
            logger.error(f"计算KDJ失败: {e}")
            return data
    
    def calculate_boll(self, data: pd.DataFrame, 
                      period: int = 20, 
                      std_dev: float = 2.0) -> pd.DataFrame:
        """
        计算布林带 (Bollinger Bands)
        
        Args:
            data: 价格数据
            period: 周期，默认20
            std_dev: 标准差倍数，默认2
            
        Returns:
            包含BOLL_UPPER、BOLL_MIDDLE、BOLL_LOWER的DataFrame
        """
        try:
            df = data.copy()
            
            # 中轨 = MA
            df['BOLL_MIDDLE'] = df['close'].rolling(window=period).mean()
            
            # 标准差
            std = df['close'].rolling(window=period).std()
            
            # 上轨和下轨
            df['BOLL_UPPER'] = df['BOLL_MIDDLE'] + (std * std_dev)
            df['BOLL_LOWER'] = df['BOLL_MIDDLE'] - (std * std_dev)
            
            # 计算布林带宽度
            df['BOLL_WIDTH'] = (df['BOLL_UPPER'] - df['BOLL_LOWER']) / df['BOLL_MIDDLE'] * 100
            
            logger.debug(f"计算布林带成功，周期: {period}, 标准差: {std_dev}")
            return df
            
        except Exception as e:
            logger.error(f"计算布林带失败: {e}")
            return data
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算平均真实波幅 (ATR - Average True Range)
        
        Args:
            data: 价格数据，需要有high、low、close列
            period: ATR周期，默认14
            
        Returns:
            包含ATR的DataFrame
        """
        try:
            df = data.copy()
            
            # 计算真实波幅 (TR)
            df['H-L'] = df['high'] - df['low']
            df['H-PC'] = abs(df['high'] - df['close'].shift(1))
            df['L-PC'] = abs(df['low'] - df['close'].shift(1))
            
            df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
            
            # 计算ATR
            df['ATR'] = df['TR'].rolling(window=period).mean()
            
            # 清理临时列
            df.drop(['H-L', 'H-PC', 'L-PC', 'TR'], axis=1, inplace=True)
            
            logger.debug(f"计算ATR成功，周期: {period}")
            return df
            
        except Exception as e:
            logger.error(f"计算ATR失败: {e}")
            return data
    
    def calculate_obv(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算能量潮 (OBV - On Balance Volume)
        
        Args:
            data: 价格数据，需要有close和volume列
            
        Returns:
            包含OBV的DataFrame
        """
        try:
            df = data.copy()
            
            # 计算OBV
            df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
            
            logger.debug("计算OBV成功")
            return df
            
        except Exception as e:
            logger.error(f"计算OBV失败: {e}")
            return data
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            data: 原始价格数据
            
        Returns:
            包含所有技术指标的DataFrame
        """
        try:
            df = data.copy()
            
            # 确保数据按时间排序
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            # 计算各类指标
            df = self.calculate_ma(df)
            df = self.calculate_ema(df)
            df = self.calculate_macd(df)
            df = self.calculate_rsi(df)
            df = self.calculate_kdj(df)
            df = self.calculate_boll(df)
            df = self.calculate_atr(df)
            
            # 如果有成交量，计算OBV
            if 'volume' in df.columns:
                df = self.calculate_obv(df)
            
            logger.info("计算所有技术指标成功")
            return df
            
        except Exception as e:
            logger.error(f"计算所有技术指标失败: {e}")
            return data
    
    def get_indicator_summary(self, data: pd.DataFrame) -> Dict:
        """
        获取技术指标汇总信息
        
        Args:
            data: 包含技术指标的DataFrame
            
        Returns:
            指标汇总字典
        """
        try:
            latest = data.iloc[-1]
            summary = {
                'price': {
                    'current': latest.get('close', 0),
                    'change': latest.get('close', 0) - data.iloc[-2].get('close', 0) if len(data) > 1 else 0
                },
                'ma': {
                    'MA5': latest.get('MA5', 0),
                    'MA10': latest.get('MA10', 0),
                    'MA20': latest.get('MA20', 0),
                    'MA60': latest.get('MA60', 0)
                },
                'macd': {
                    'MACD': latest.get('MACD', 0),
                    'Signal': latest.get('MACD_Signal', 0),
                    'Histogram': latest.get('MACD_Hist', 0)
                },
                'rsi': {
                    'RSI': latest.get('RSI', 0)
                },
                'kdj': {
                    'K': latest.get('K', 0),
                    'D': latest.get('D', 0),
                    'J': latest.get('J', 0)
                },
                'boll': {
                    'Upper': latest.get('BOLL_UPPER', 0),
                    'Middle': latest.get('BOLL_MIDDLE', 0),
                    'Lower': latest.get('BOLL_LOWER', 0),
                    'Width': latest.get('BOLL_WIDTH', 0)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取指标汇总失败: {e}")
            return {}

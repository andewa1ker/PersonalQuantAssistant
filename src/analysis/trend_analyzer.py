"""
趋势分析器
提供趋势识别、支撑阻力位分析功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        """初始化趋势分析器"""
        logger.info("初始化趋势分析器")
    
    def identify_trend(self, data: pd.DataFrame, period: int = 20) -> Dict:
        """
        识别当前趋势
        
        Args:
            data: 价格数据，需要有close列
            period: 分析周期
            
        Returns:
            趋势信息字典
        """
        try:
            df = data.tail(period).copy()
            
            # 计算价格变化
            price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
            
            # 计算移动平均线排列
            ma5 = df['close'].tail(5).mean()
            ma10 = df['close'].tail(10).mean()
            ma20 = df['close'].tail(20).mean() if len(df) >= 20 else ma10
            
            current_price = df['close'].iloc[-1]
            
            # 判断趋势
            if price_change > 5:
                trend = "强势上涨"
                strength = "strong_bullish"
            elif price_change > 2:
                trend = "上涨"
                strength = "bullish"
            elif price_change > -2:
                trend = "震荡"
                strength = "neutral"
            elif price_change > -5:
                trend = "下跌"
                strength = "bearish"
            else:
                trend = "强势下跌"
                strength = "strong_bearish"
            
            # 均线排列
            if ma5 > ma10 > ma20 and current_price > ma5:
                ma_alignment = "多头排列"
            elif ma5 < ma10 < ma20 and current_price < ma5:
                ma_alignment = "空头排列"
            else:
                ma_alignment = "混乱"
            
            result = {
                'trend': trend,
                'strength': strength,
                'price_change': round(price_change, 2),
                'ma_alignment': ma_alignment,
                'ma5': round(ma5, 2),
                'ma10': round(ma10, 2),
                'ma20': round(ma20, 2),
                'current_price': round(current_price, 2)
            }
            
            logger.debug(f"趋势识别结果: {trend}")
            return result
            
        except Exception as e:
            logger.error(f"趋势识别失败: {e}")
            return {'trend': '未知', 'strength': 'unknown'}
    
    def find_support_resistance(self, data: pd.DataFrame, 
                               window: int = 20,
                               num_levels: int = 3) -> Dict[str, List[float]]:
        """
        寻找支撑位和阻力位
        
        Args:
            data: 价格数据
            window: 分析窗口
            num_levels: 返回的支撑/阻力位数量
            
        Returns:
            包含支撑位和阻力位的字典
        """
        try:
            df = data.tail(100).copy()  # 使用最近100个数据点
            
            # 找局部高点和低点
            highs = []
            lows = []
            
            for i in range(window, len(df) - window):
                # 检查是否为局部高点
                if df['high'].iloc[i] == df['high'].iloc[i-window:i+window+1].max():
                    highs.append(df['high'].iloc[i])
                
                # 检查是否为局部低点
                if df['low'].iloc[i] == df['low'].iloc[i-window:i+window+1].min():
                    lows.append(df['low'].iloc[i])
            
            # 聚类相近的价格水平
            def cluster_levels(levels, tolerance=0.02):
                if not levels:
                    return []
                
                levels = sorted(levels)
                clusters = []
                current_cluster = [levels[0]]
                
                for level in levels[1:]:
                    if (level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                        current_cluster.append(level)
                    else:
                        clusters.append(np.mean(current_cluster))
                        current_cluster = [level]
                
                clusters.append(np.mean(current_cluster))
                return clusters
            
            # 获取聚类后的支撑位和阻力位
            support_levels = cluster_levels(lows)
            resistance_levels = cluster_levels(highs)
            
            # 按距离当前价格排序
            current_price = df['close'].iloc[-1]
            support_levels = sorted(support_levels, key=lambda x: abs(current_price - x))[:num_levels]
            resistance_levels = sorted(resistance_levels, key=lambda x: abs(current_price - x))[:num_levels]
            
            result = {
                'support': [round(x, 2) for x in sorted(support_levels, reverse=True)],
                'resistance': [round(x, 2) for x in sorted(resistance_levels)]
            }
            
            logger.debug(f"找到支撑位: {result['support']}, 阻力位: {result['resistance']}")
            return result
            
        except Exception as e:
            logger.error(f"寻找支撑阻力位失败: {e}")
            return {'support': [], 'resistance': []}
    
    def calculate_trend_strength(self, data: pd.DataFrame) -> Dict:
        """
        计算趋势强度
        使用ADX (Average Directional Index)
        
        Args:
            data: 价格数据，需要有high、low、close列
            
        Returns:
            趋势强度信息
        """
        try:
            df = data.tail(50).copy()
            period = 14
            
            # 计算+DM和-DM
            df['H-L'] = df['high'] - df['low']
            df['H-PC'] = df['high'] - df['close'].shift(1)
            df['L-PC'] = df['low'] - df['close'].shift(1)
            
            df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
            
            df['+DM'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                                 df['high'] - df['high'].shift(1), 0)
            df['+DM'] = np.where(df['+DM'] < 0, 0, df['+DM'])
            
            df['-DM'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                                 df['low'].shift(1) - df['low'], 0)
            df['-DM'] = np.where(df['-DM'] < 0, 0, df['-DM'])
            
            # 计算ATR
            atr = df['TR'].rolling(window=period).mean()
            
            # 计算+DI和-DI
            plus_di = 100 * (df['+DM'].rolling(window=period).mean() / atr)
            minus_di = 100 * (df['-DM'].rolling(window=period).mean() / atr)
            
            # 计算DX和ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=period).mean()
            
            latest_adx = adx.iloc[-1]
            latest_plus_di = plus_di.iloc[-1]
            latest_minus_di = minus_di.iloc[-1]
            
            # 判断趋势强度
            if latest_adx > 40:
                strength_desc = "强趋势"
            elif latest_adx > 25:
                strength_desc = "中等趋势"
            else:
                strength_desc = "弱趋势/震荡"
            
            # 判断趋势方向
            if latest_plus_di > latest_minus_di:
                direction = "上涨"
            else:
                direction = "下跌"
            
            result = {
                'adx': round(latest_adx, 2),
                'plus_di': round(latest_plus_di, 2),
                'minus_di': round(latest_minus_di, 2),
                'strength_description': strength_desc,
                'direction': direction
            }
            
            logger.debug(f"趋势强度: ADX={latest_adx:.2f}, {strength_desc}")
            return result
            
        except Exception as e:
            logger.error(f"计算趋势强度失败: {e}")
            return {'adx': 0, 'strength_description': '未知'}
    
    def detect_divergence(self, data: pd.DataFrame) -> Dict:
        """
        检测价格与指标的背离
        
        Args:
            data: 包含价格和RSI数据的DataFrame
            
        Returns:
            背离信息
        """
        try:
            df = data.tail(50).copy()
            
            if 'RSI' not in df.columns:
                return {'divergence': 'none', 'description': '需要RSI数据'}
            
            # 找价格和RSI的局部高低点
            window = 5
            price_highs = []
            price_lows = []
            rsi_highs = []
            rsi_lows = []
            
            for i in range(window, len(df) - window):
                if df['close'].iloc[i] == df['close'].iloc[i-window:i+window+1].max():
                    price_highs.append((i, df['close'].iloc[i]))
                    rsi_highs.append((i, df['RSI'].iloc[i]))
                
                if df['close'].iloc[i] == df['close'].iloc[i-window:i+window+1].min():
                    price_lows.append((i, df['close'].iloc[i]))
                    rsi_lows.append((i, df['RSI'].iloc[i]))
            
            divergence_type = 'none'
            description = '未检测到明显背离'
            
            # 检测顶背离（价格创新高，RSI不创新高）
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                if (price_highs[-1][1] > price_highs[-2][1] and 
                    rsi_highs[-1][1] < rsi_highs[-2][1]):
                    divergence_type = 'bearish'
                    description = '顶背离：价格创新高但RSI走弱，可能见顶'
            
            # 检测底背离（价格创新低，RSI不创新低）
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                if (price_lows[-1][1] < price_lows[-2][1] and 
                    rsi_lows[-1][1] > rsi_lows[-2][1]):
                    divergence_type = 'bullish'
                    description = '底背离：价格创新低但RSI走强，可能见底'
            
            result = {
                'divergence': divergence_type,
                'description': description
            }
            
            if divergence_type != 'none':
                logger.info(f"检测到背离: {description}")
            
            return result
            
        except Exception as e:
            logger.error(f"检测背离失败: {e}")
            return {'divergence': 'error', 'description': str(e)}
    
    def get_trend_summary(self, data: pd.DataFrame) -> Dict:
        """
        获取趋势分析综合报告
        
        Args:
            data: 价格数据
            
        Returns:
            综合趋势分析
        """
        try:
            trend_info = self.identify_trend(data)
            sr_levels = self.find_support_resistance(data)
            strength_info = self.calculate_trend_strength(data)
            divergence_info = self.detect_divergence(data)
            
            summary = {
                'trend': trend_info,
                'support_resistance': sr_levels,
                'trend_strength': strength_info,
                'divergence': divergence_info,
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info("生成趋势分析综合报告成功")
            return summary
            
        except Exception as e:
            logger.error(f"生成趋势分析综合报告失败: {e}")
            return {}

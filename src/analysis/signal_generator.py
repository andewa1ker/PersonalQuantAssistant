"""
信号生成器
整合技术指标生成交易信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger
from .technical_analyzer import TechnicalAnalyzer
from .trend_analyzer import TrendAnalyzer
from .volatility_analyzer import VolatilityAnalyzer


class SignalGenerator:
    """交易信号生成器"""
    
    def __init__(self):
        """初始化信号生成器"""
        self.technical = TechnicalAnalyzer()
        self.trend = TrendAnalyzer()
        self.volatility = VolatilityAnalyzer()
        logger.info("初始化信号生成器")
    
    def generate_ma_signal(self, data: pd.DataFrame) -> Dict:
        """
        基于移动平均线生成信号
        
        Args:
            data: 包含MA数据的DataFrame
            
        Returns:
            MA信号
        """
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            signal = "中性"
            strength = 0
            reasons = []
            
            # 金叉/死叉
            if 'MA5' in latest and 'MA10' in latest:
                if prev['MA5'] <= prev['MA10'] and latest['MA5'] > latest['MA10']:
                    signal = "买入"
                    strength += 2
                    reasons.append("MA5上穿MA10形成金叉")
                elif prev['MA5'] >= prev['MA10'] and latest['MA5'] < latest['MA10']:
                    signal = "卖出"
                    strength -= 2
                    reasons.append("MA5下穿MA10形成死叉")
            
            # 价格与均线关系
            current_price = latest['close']
            if 'MA20' in latest:
                if current_price > latest['MA20']:
                    strength += 1
                    reasons.append("价格在MA20上方")
                else:
                    strength -= 1
                    reasons.append("价格在MA20下方")
            
            # 均线排列
            if 'MA5' in latest and 'MA10' in latest and 'MA20' in latest:
                if latest['MA5'] > latest['MA10'] > latest['MA20']:
                    strength += 1
                    reasons.append("多头排列")
                elif latest['MA5'] < latest['MA10'] < latest['MA20']:
                    strength -= 1
                    reasons.append("空头排列")
            
            # 确定最终信号
            if signal == "中性":
                if strength >= 2:
                    signal = "买入"
                elif strength <= -2:
                    signal = "卖出"
            
            result = {
                'signal': signal,
                'strength': strength,
                'reasons': reasons
            }
            
            logger.debug(f"MA信号: {signal}, 强度: {strength}")
            return result
            
        except Exception as e:
            logger.error(f"生成MA信号失败: {e}")
            return {'signal': '中性', 'strength': 0, 'reasons': []}
    
    def generate_macd_signal(self, data: pd.DataFrame) -> Dict:
        """
        基于MACD生成信号
        
        Args:
            data: 包含MACD数据的DataFrame
            
        Returns:
            MACD信号
        """
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            signal = "中性"
            strength = 0
            reasons = []
            
            if 'MACD' not in latest or 'MACD_Signal' not in latest:
                return {'signal': '中性', 'strength': 0, 'reasons': ['缺少MACD数据']}
            
            # MACD金叉/死叉
            if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
                signal = "买入"
                strength += 2
                reasons.append("MACD金叉")
            elif prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
                signal = "卖出"
                strength -= 2
                reasons.append("MACD死叉")
            
            # MACD柱状图变化
            if 'MACD_Hist' in latest:
                if latest['MACD_Hist'] > 0 and prev['MACD_Hist'] <= 0:
                    strength += 1
                    reasons.append("MACD柱状图转正")
                elif latest['MACD_Hist'] < 0 and prev['MACD_Hist'] >= 0:
                    strength -= 1
                    reasons.append("MACD柱状图转负")
                
                # 柱状图增强/减弱
                if abs(latest['MACD_Hist']) > abs(prev['MACD_Hist']):
                    if latest['MACD_Hist'] > 0:
                        reasons.append("多头动能增强")
                    else:
                        reasons.append("空头动能增强")
            
            # 零轴位置
            if latest['MACD'] > 0:
                strength += 0.5
                reasons.append("MACD在零轴上方")
            else:
                strength -= 0.5
                reasons.append("MACD在零轴下方")
            
            # 确定最终信号
            if signal == "中性":
                if strength >= 2:
                    signal = "买入"
                elif strength <= -2:
                    signal = "卖出"
            
            result = {
                'signal': signal,
                'strength': int(strength),
                'reasons': reasons
            }
            
            logger.debug(f"MACD信号: {signal}, 强度: {strength}")
            return result
            
        except Exception as e:
            logger.error(f"生成MACD信号失败: {e}")
            return {'signal': '中性', 'strength': 0, 'reasons': []}
    
    def generate_rsi_signal(self, data: pd.DataFrame) -> Dict:
        """
        基于RSI生成信号
        
        Args:
            data: 包含RSI数据的DataFrame
            
        Returns:
            RSI信号
        """
        try:
            latest = data.iloc[-1]
            
            if 'RSI' not in latest:
                return {'signal': '中性', 'strength': 0, 'reasons': ['缺少RSI数据']}
            
            rsi = latest['RSI']
            signal = "中性"
            strength = 0
            reasons = []
            
            # RSI超买超卖
            if rsi < 30:
                signal = "买入"
                strength = 2
                reasons.append(f"RSI={rsi:.1f}，超卖")
            elif rsi < 40:
                strength = 1
                reasons.append(f"RSI={rsi:.1f}，接近超卖")
            elif rsi > 70:
                signal = "卖出"
                strength = -2
                reasons.append(f"RSI={rsi:.1f}，超买")
            elif rsi > 60:
                strength = -1
                reasons.append(f"RSI={rsi:.1f}，接近超买")
            else:
                reasons.append(f"RSI={rsi:.1f}，中性区域")
            
            result = {
                'signal': signal,
                'strength': strength,
                'reasons': reasons,
                'rsi_value': round(rsi, 2)
            }
            
            logger.debug(f"RSI信号: {signal}, RSI值: {rsi:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"生成RSI信号失败: {e}")
            return {'signal': '中性', 'strength': 0, 'reasons': []}
    
    def generate_kdj_signal(self, data: pd.DataFrame) -> Dict:
        """
        基于KDJ生成信号
        
        Args:
            data: 包含KDJ数据的DataFrame
            
        Returns:
            KDJ信号
        """
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            if 'K' not in latest or 'D' not in latest:
                return {'signal': '中性', 'strength': 0, 'reasons': ['缺少KDJ数据']}
            
            k = latest['K']
            d = latest['D']
            j = latest['J']
            
            signal = "中性"
            strength = 0
            reasons = []
            
            # KDJ金叉/死叉
            if prev['K'] <= prev['D'] and k > d:
                signal = "买入"
                strength += 2
                reasons.append("KDJ金叉")
            elif prev['K'] >= prev['D'] and k < d:
                signal = "卖出"
                strength -= 2
                reasons.append("KDJ死叉")
            
            # 超买超卖
            if j < 20:
                strength += 1
                reasons.append(f"J值={j:.1f}，超卖")
            elif j > 80:
                strength -= 1
                reasons.append(f"J值={j:.1f}，超买")
            
            # 确定最终信号
            if signal == "中性":
                if strength >= 2:
                    signal = "买入"
                elif strength <= -2:
                    signal = "卖出"
            
            result = {
                'signal': signal,
                'strength': strength,
                'reasons': reasons,
                'k_value': round(k, 2),
                'd_value': round(d, 2),
                'j_value': round(j, 2)
            }
            
            logger.debug(f"KDJ信号: {signal}, K={k:.2f}, D={d:.2f}, J={j:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"生成KDJ信号失败: {e}")
            return {'signal': '中性', 'strength': 0, 'reasons': []}
    
    def generate_comprehensive_signal(self, data: pd.DataFrame) -> Dict:
        """
        生成综合交易信号
        整合多个指标
        
        Args:
            data: 包含所有技术指标的DataFrame
            
        Returns:
            综合信号
        """
        try:
            # 获取各个指标的信号
            ma_signal = self.generate_ma_signal(data)
            macd_signal = self.generate_macd_signal(data)
            rsi_signal = self.generate_rsi_signal(data)
            kdj_signal = self.generate_kdj_signal(data)
            
            # 计算综合强度
            total_strength = (
                ma_signal['strength'] +
                macd_signal['strength'] +
                rsi_signal['strength'] +
                kdj_signal['strength']
            )
            
            # 计算买入/卖出信号数量
            signals = [ma_signal['signal'], macd_signal['signal'], 
                      rsi_signal['signal'], kdj_signal['signal']]
            buy_count = signals.count('买入')
            sell_count = signals.count('卖出')
            
            # 确定最终信号
            if buy_count >= 3 or total_strength >= 5:
                final_signal = "强烈买入"
                confidence = "高"
            elif buy_count >= 2 or total_strength >= 3:
                final_signal = "买入"
                confidence = "中"
            elif sell_count >= 3 or total_strength <= -5:
                final_signal = "强烈卖出"
                confidence = "高"
            elif sell_count >= 2 or total_strength <= -3:
                final_signal = "卖出"
                confidence = "中"
            else:
                final_signal = "观望"
                confidence = "低"
            
            # 汇总原因
            all_reasons = []
            if ma_signal['reasons']:
                all_reasons.extend([f"MA: {r}" for r in ma_signal['reasons']])
            if macd_signal['reasons']:
                all_reasons.extend([f"MACD: {r}" for r in macd_signal['reasons']])
            if rsi_signal['reasons']:
                all_reasons.extend([f"RSI: {r}" for r in rsi_signal['reasons']])
            if kdj_signal['reasons']:
                all_reasons.extend([f"KDJ: {r}" for r in kdj_signal['reasons']])
            
            result = {
                'signal': final_signal,
                'confidence': confidence,
                'total_strength': total_strength,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'reasons': all_reasons[:5],  # 只取前5个原因
                'individual_signals': {
                    'ma': ma_signal['signal'],
                    'macd': macd_signal['signal'],
                    'rsi': rsi_signal['signal'],
                    'kdj': kdj_signal['signal']
                },
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"生成综合信号: {final_signal}, 信心度: {confidence}, 强度: {total_strength}")
            return result
            
        except Exception as e:
            logger.error(f"生成综合信号失败: {e}")
            return {'signal': '观望', 'confidence': '低', 'reasons': [str(e)]}
    
    def analyze_with_signals(self, data: pd.DataFrame) -> Dict:
        """
        完整分析并生成信号
        
        Args:
            data: 原始价格数据
            
        Returns:
            包含技术分析和交易信号的完整报告
        """
        try:
            # 计算所有技术指标
            analyzed_data = self.technical.calculate_all_indicators(data)
            
            # 生成交易信号
            signals = self.generate_comprehensive_signal(analyzed_data)
            
            # 获取趋势分析
            trend_summary = self.trend.get_trend_summary(analyzed_data)
            
            # 获取波动率分析
            vol_summary = self.volatility.get_volatility_summary(analyzed_data)
            
            # 组合完整报告
            report = {
                'data': analyzed_data,
                'signals': signals,
                'trend_analysis': trend_summary,
                'volatility_analysis': vol_summary,
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info("完成完整技术分析和信号生成")
            return report
            
        except Exception as e:
            logger.error(f"完整分析失败: {e}")
            return {'signals': {'signal': '错误', 'reasons': [str(e)]}}

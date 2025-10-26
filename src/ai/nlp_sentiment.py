"""
NLP情感分析 - 新闻、公告、社交媒体情感分析
NLP Sentiment Analysis for Financial Text
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
import re
from collections import Counter

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    logger.warning("jieba未安装，中文分词功能不可用")
    JIEBA_AVAILABLE = False


@dataclass
class SentimentConfig:
    """情感分析配置"""
    # 词典路径
    positive_dict_path: str = "data/sentiment/positive.txt"
    negative_dict_path: str = "data/sentiment/negative.txt"
    
    # 情感阈值
    positive_threshold: float = 0.3
    negative_threshold: float = -0.3
    
    # 关键词提取
    topk_keywords: int = 10


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    sentiment_score: float          # [-1, 1]
    sentiment_label: str            # 'positive', 'neutral', 'negative'
    positive_words: List[str]
    negative_words: List[str]
    keywords: List[Tuple[str, float]]
    timestamp: str


class ChineseSentimentAnalyzer:
    """中文情感分析器"""
    
    def __init__(self, config: Optional[SentimentConfig] = None):
        """
        初始化情感分析器
        
        Args:
            config: 情感配置
        """
        if not JIEBA_AVAILABLE:
            logger.warning("jieba未安装，使用简化版情感分析")
        
        self.config = config or SentimentConfig()
        
        # 加载情感词典
        self.positive_words = self._load_sentiment_dict('positive')
        self.negative_words = self._load_sentiment_dict('negative')
        
        logger.info(f"情感分析器初始化完成 (正向词: {len(self.positive_words)}, "
                   f"负向词: {len(self.negative_words)})")
    
    def _load_sentiment_dict(self, dict_type: str) -> set:
        """
        加载情感词典
        
        Args:
            dict_type: 'positive' or 'negative'
            
        Returns:
            情感词集合
        """
        # 内置基础情感词典
        if dict_type == 'positive':
            default_words = {
                '上涨', '增长', '提升', '改善', '优化', '突破', '创新', '盈利',
                '增加', '提高', '扩大', '优秀', '强劲', '稳定', '利好', '积极',
                '超预期', '超额', '领先', '成功', '卓越', '优质', '良好', '看好',
                '买入', '推荐', '增持', '收益', '利润', '赢利', '增收', '回升'
            }
        else:  # negative
            default_words = {
                '下跌', '下降', '减少', '亏损', '损失', '风险', '危机', '问题',
                '困难', '挑战', '压力', '恶化', '滞后', '疲软', '低迷', '利空',
                '负面', '消极', '担忧', '警惕', '卖出', '减持', '回调', '下行',
                '不及预期', '低于预期', '失败', '违规', '处罚', '暂停', '调查', '风险'
            }
        
        # TODO: 从文件加载自定义词典
        # try:
        #     path = (self.config.positive_dict_path if dict_type == 'positive' 
        #            else self.config.negative_dict_path)
        #     with open(path, 'r', encoding='utf-8') as f:
        #         custom_words = set(line.strip() for line in f)
        #     default_words.update(custom_words)
        # except FileNotFoundError:
        #     logger.debug(f"未找到自定义{dict_type}词典，使用默认词典")
        
        return default_words
    
    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除邮箱
        text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
        
        # 去除特殊字符（保留中文、英文、数字）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 文本
            
        Returns:
            词语列表
        """
        if JIEBA_AVAILABLE:
            return list(jieba.cut(text))
        else:
            # 简单的字符级分词
            return list(text)
    
    def calculate_sentiment_score(self, words: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        计算情感得分
        
        Args:
            words: 词语列表
            
        Returns:
            (情感得分, 正向词, 负向词)
        """
        positive_count = 0
        negative_count = 0
        
        positive_found = []
        negative_found = []
        
        for word in words:
            if word in self.positive_words:
                positive_count += 1
                positive_found.append(word)
            elif word in self.negative_words:
                negative_count += 1
                negative_found.append(word)
        
        total = positive_count + negative_count
        
        if total == 0:
            sentiment_score = 0.0
        else:
            # 归一化到[-1, 1]
            sentiment_score = (positive_count - negative_count) / total
        
        return sentiment_score, positive_found, negative_found
    
    def extract_keywords(self, text: str, topk: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        提取关键词
        
        Args:
            text: 文本
            topk: 提取前K个关键词
            
        Returns:
            [(关键词, 权重)]
        """
        if topk is None:
            topk = self.config.topk_keywords
        
        if JIEBA_AVAILABLE:
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=topk, withWeight=True)
            return keywords
        else:
            # 简单的词频统计
            words = self.tokenize(text)
            word_freq = Counter(words)
            keywords = word_freq.most_common(topk)
            # 归一化权重
            max_freq = max(freq for _, freq in keywords) if keywords else 1
            keywords = [(word, freq / max_freq) for word, freq in keywords]
            return keywords
    
    def analyze(self, text: str) -> SentimentResult:
        """
        分析文本情感
        
        Args:
            text: 文本
            
        Returns:
            SentimentResult
        """
        # 预处理
        cleaned_text = self.preprocess_text(text)
        
        # 分词
        words = self.tokenize(cleaned_text)
        
        # 计算情感得分
        sentiment_score, positive_words, negative_words = self.calculate_sentiment_score(words)
        
        # 情感标签
        if sentiment_score >= self.config.positive_threshold:
            sentiment_label = 'positive'
        elif sentiment_score <= self.config.negative_threshold:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        # 提取关键词
        keywords = self.extract_keywords(cleaned_text)
        
        result = SentimentResult(
            text=text[:100] + '...' if len(text) > 100 else text,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            positive_words=positive_words,
            negative_words=negative_words,
            keywords=keywords,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return result
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        批量分析
        
        Args:
            texts: 文本列表
            
        Returns:
            结果列表
        """
        results = []
        
        for text in texts:
            try:
                result = self.analyze(text)
                results.append(result)
            except Exception as e:
                logger.warning(f"分析失败: {e}")
        
        return results


class FinancialSentimentAggregator:
    """金融情感聚合器"""
    
    def __init__(self):
        """初始化聚合器"""
        self.analyzer = ChineseSentimentAnalyzer()
    
    def aggregate_news_sentiment(self, 
                                news_df: pd.DataFrame,
                                text_column: str = 'content',
                                time_column: str = 'publish_time') -> pd.DataFrame:
        """
        聚合新闻情感
        
        Args:
            news_df: 新闻DataFrame
            text_column: 文本列名
            time_column: 时间列名
            
        Returns:
            情感聚合DataFrame
        """
        logger.info("聚合新闻情感...")
        
        if text_column not in news_df.columns:
            logger.error(f"列不存在: {text_column}")
            return pd.DataFrame()
        
        # 分析每条新闻
        sentiments = []
        
        for _, row in news_df.iterrows():
            text = str(row[text_column])
            result = self.analyzer.analyze(text)
            
            sentiments.append({
                'time': row.get(time_column, datetime.now()),
                'sentiment_score': result.sentiment_score,
                'sentiment_label': result.sentiment_label
            })
        
        sentiment_df = pd.DataFrame(sentiments)
        
        # 按时间聚合
        if time_column in news_df.columns:
            sentiment_df['date'] = pd.to_datetime(sentiment_df['time']).dt.date
            
            daily_sentiment = sentiment_df.groupby('date').agg({
                'sentiment_score': ['mean', 'std', 'count']
            }).reset_index()
            
            daily_sentiment.columns = ['date', 'sentiment_mean', 'sentiment_std', 'news_count']
            
            logger.info(f"聚合完成，共 {len(daily_sentiment)} 天数据")
            
            return daily_sentiment
        
        return sentiment_df
    
    def calculate_sentiment_index(self,
                                 sentiment_df: pd.DataFrame,
                                 window: int = 5) -> pd.DataFrame:
        """
        计算情感指数
        
        Args:
            sentiment_df: 情感DataFrame
            window: 滚动窗口
            
        Returns:
            包含情感指数的DataFrame
        """
        df = sentiment_df.copy()
        
        # 移动平均
        df['sentiment_ma'] = df['sentiment_mean'].rolling(window=window).mean()
        
        # 情感动量
        df['sentiment_momentum'] = df['sentiment_mean'].diff(window)
        
        # 情感波动率
        df['sentiment_volatility'] = df['sentiment_mean'].rolling(window=window).std()
        
        # 综合情感指数 (0-100)
        # 正向情感越强、波动越小，指数越高
        df['sentiment_index'] = (
            (df['sentiment_ma'] + 1) * 50  # 归一化到[0, 100]
            - df['sentiment_volatility'] * 20  # 降低波动的影响
        ).clip(0, 100)
        
        return df
    
    def generate_sentiment_signal(self,
                                 sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        生成情感交易信号
        
        Args:
            sentiment_df: 情感DataFrame
            
        Returns:
            包含信号的DataFrame
        """
        df = sentiment_df.copy()
        
        # 计算情感指数
        df = self.calculate_sentiment_index(df)
        
        # 生成信号
        df['signal'] = 0
        
        # 强烈看多
        df.loc[df['sentiment_index'] > 70, 'signal'] = 1
        
        # 强烈看空
        df.loc[df['sentiment_index'] < 30, 'signal'] = -1
        
        # 情感反转信号
        df['sentiment_change'] = df['sentiment_mean'].diff()
        
        # 从极度悲观反转
        df.loc[(df['sentiment_mean'].shift(1) < -0.5) & (df['sentiment_change'] > 0.3), 'signal'] = 1
        
        # 从极度乐观反转
        df.loc[(df['sentiment_mean'].shift(1) > 0.5) & (df['sentiment_change'] < -0.3), 'signal'] = -1
        
        return df


# 便捷函数
def quick_sentiment_analysis(text: str) -> Dict:
    """
    快速情感分析
    
    Args:
        text: 文本
        
    Returns:
        情感分析结果字典
    """
    analyzer = ChineseSentimentAnalyzer()
    result = analyzer.analyze(text)
    
    return {
        'sentiment_score': result.sentiment_score,
        'sentiment_label': result.sentiment_label,
        'positive_words': result.positive_words,
        'negative_words': result.negative_words,
        'keywords': result.keywords
    }


def analyze_news_sentiment(news_list: List[str]) -> pd.DataFrame:
    """
    分析新闻列表情感
    
    Args:
        news_list: 新闻文本列表
        
    Returns:
        情感分析结果DataFrame
    """
    analyzer = ChineseSentimentAnalyzer()
    results = analyzer.analyze_batch(news_list)
    
    data = []
    for result in results:
        data.append({
            'sentiment_score': result.sentiment_score,
            'sentiment_label': result.sentiment_label,
            'positive_words_count': len(result.positive_words),
            'negative_words_count': len(result.negative_words),
            'top_keywords': ', '.join([kw for kw, _ in result.keywords[:5]])
        })
    
    return pd.DataFrame(data)

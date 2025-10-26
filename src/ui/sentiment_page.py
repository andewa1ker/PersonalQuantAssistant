"""
情感分析页面 - 新闻情感展示
Sentiment Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from loguru import logger

from src.ai.nlp_sentiment import ChineseSentimentAnalyzer, FinancialSentimentAggregator, quick_sentiment_analysis


def show_sentiment_page():
    """显示情感分析页面"""
    st.title("💬 情感分析")
    
    tabs = st.tabs(["📝 单文本分析", "📰 批量新闻", "📊 情感指数", "🎯 交易信号"])
    
    with tabs[0]:
        show_single_text_analysis()
    
    with tabs[1]:
        show_batch_news_analysis()
    
    with tabs[2]:
        show_sentiment_index()
    
    with tabs[3]:
        show_trading_signals()


def show_single_text_analysis():
    """单文本情感分析"""
    st.header("单文本情感分析")
    
    text = st.text_area(
        "输入文本",
        height=150,
        placeholder="输入要分析的新闻、公告或社交媒体内容...",
        key="single_text"
    )
    
    if st.button("🔍 分析情感", key="analyze_single"):
        if not text.strip():
            st.warning("请输入文本")
            return
        
        with st.spinner("分析中..."):
            try:
                result = quick_sentiment_analysis(text)
                
                st.success("分析完成！")
                
                # 情感得分
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("情感得分", f"{result['sentiment_score']:.3f}")
                
                with col2:
                    label_emoji = {
                        'positive': '😊 正面',
                        'neutral': '😐 中性',
                        'negative': '😞 负面'
                    }
                    st.metric("情感标签", label_emoji.get(result['sentiment_label'], result['sentiment_label']))
                
                with col3:
                    st.metric("正向词数", len(result['positive_words']))
                    st.metric("负向词数", len(result['negative_words']))
                
                # 情感词汇
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ 正向词汇")
                    if result['positive_words']:
                        st.write(", ".join(result['positive_words']))
                    else:
                        st.write("_无_")
                
                with col2:
                    st.subheader("❌ 负向词汇")
                    if result['negative_words']:
                        st.write(", ".join(result['negative_words']))
                    else:
                        st.write("_无_")
                
                # 关键词
                st.markdown("---")
                st.subheader("🔑 关键词")
                
                if result['keywords']:
                    keywords_str = " | ".join([f"{kw} ({weight:.3f})" for kw, weight in result['keywords']])
                    st.write(keywords_str)
                
                # 情感可视化
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=result['sentiment_score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    delta={'reference': 0},
                    gauge={
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-1, -0.3], 'color': "#FF6B6B"},
                            {'range': [-0.3, 0.3], 'color': "#FFA500"},
                            {'range': [0.3, 1], 'color': "#51CF66"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': result['sentiment_score']
                        }
                    }
                ))
                fig.update_layout(
                    title="情感得分",
                    height=300,
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"分析失败: {e}")
                logger.error(f"情感分析失败: {e}", exc_info=True)


def show_batch_news_analysis():
    """批量新闻分析"""
    st.header("批量新闻分析")
    
    st.info("💡 输入多条新闻，每行一条")
    
    news_text = st.text_area(
        "新闻列表",
        height=200,
        placeholder="每行输入一条新闻...\n例如：\n公司业绩超预期，净利润增长50%\n股价大跌，面临退市风险\n...",
        key="batch_news"
    )
    
    if st.button("📊 批量分析", key="analyze_batch"):
        if not news_text.strip():
            st.warning("请输入新闻")
            return
        
        news_list = [line.strip() for line in news_text.split('\n') if line.strip()]
        
        if not news_list:
            st.warning("没有有效的新闻")
            return
        
        with st.spinner(f"分析 {len(news_list)} 条新闻..."):
            try:
                from src.ai.nlp_sentiment import analyze_news_sentiment
                
                result_df = analyze_news_sentiment(news_list)
                
                st.success(f"分析完成！共 {len(result_df)} 条")
                
                # 统计
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_score = result_df['sentiment_score'].mean()
                    st.metric("平均情感", f"{avg_score:.3f}")
                
                with col2:
                    positive_count = (result_df['sentiment_label'] == 'positive').sum()
                    st.metric("正面新闻", f"{positive_count} 条")
                
                with col3:
                    neutral_count = (result_df['sentiment_label'] == 'neutral').sum()
                    st.metric("中性新闻", f"{neutral_count} 条")
                
                with col4:
                    negative_count = (result_df['sentiment_label'] == 'negative').sum()
                    st.metric("负面新闻", f"{negative_count} 条")
                
                # 详细结果
                st.markdown("---")
                st.subheader("详细结果")
                st.dataframe(result_df, use_container_width=True)
                
                # 情感分布
                fig = go.Figure(data=[
                    go.Histogram(
                        x=result_df['sentiment_score'],
                        nbinsx=20,
                        marker_color='#00D9FF'
                    )
                ])
                fig.update_layout(
                    title="情感得分分布",
                    xaxis_title="情感得分",
                    yaxis_title="数量",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"批量分析失败: {e}")


def show_sentiment_index():
    """情感指数"""
    st.header("情感指数")
    
    st.info("💡 基于历史新闻构建情感指数")
    
    # 模拟数据（实际应从数据库获取）
    if st.button("📈 生成情感指数", key="gen_index"):
        with st.spinner("生成中..."):
            try:
                # 生成模拟数据
                dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
                
                sentiment_data = {
                    'date': dates,
                    'sentiment_mean': np.random.normal(0.1, 0.3, 60),
                    'sentiment_std': np.random.uniform(0.1, 0.3, 60),
                    'news_count': np.random.randint(5, 30, 60)
                }
                
                sentiment_df = pd.DataFrame(sentiment_data)
                
                # 计算情感指数
                aggregator = FinancialSentimentAggregator()
                index_df = aggregator.calculate_sentiment_index(sentiment_df)
                
                # 显示
                st.subheader("情感指数走势")
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=index_df['date'],
                    y=index_df['sentiment_index'],
                    mode='lines',
                    name='情感指数',
                    line=dict(color='#00D9FF', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 217, 255, 0.1)'
                ))
                
                # 添加阈值线
                fig.add_hline(y=70, line_dash="dash", line_color="green", 
                            annotation_text="强势区")
                fig.add_hline(y=30, line_dash="dash", line_color="red", 
                            annotation_text="弱势区")
                
                fig.update_layout(
                    title="情感指数 (0-100)",
                    xaxis_title="日期",
                    yaxis_title="指数值",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 情感动量
                st.markdown("---")
                st.subheader("情感动量")
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=index_df['date'],
                    y=index_df['sentiment_momentum'],
                    marker_color=index_df['sentiment_momentum'].apply(
                        lambda x: '#51CF66' if x > 0 else '#FF6B6B'
                    ),
                    name='情感动量'
                ))
                
                fig.update_layout(
                    title="情感动量变化",
                    xaxis_title="日期",
                    yaxis_title="动量",
                    template="plotly_dark",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"生成失败: {e}")


def show_trading_signals():
    """交易信号"""
    st.header("情感交易信号")
    
    st.info("💡 基于情感指数生成交易信号")
    
    if st.button("🎯 生成信号", key="gen_signals"):
        with st.spinner("生成中..."):
            try:
                # 模拟数据
                dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
                
                sentiment_data = {
                    'date': dates,
                    'sentiment_mean': np.random.normal(0.1, 0.3, 60),
                    'sentiment_std': np.random.uniform(0.1, 0.3, 60),
                    'news_count': np.random.randint(5, 30, 60)
                }
                
                sentiment_df = pd.DataFrame(sentiment_data)
                
                # 生成信号
                aggregator = FinancialSentimentAggregator()
                signal_df = aggregator.generate_sentiment_signal(sentiment_df)
                
                # 显示信号
                st.subheader("交易信号")
                
                # 最新信号
                latest_signal = signal_df.iloc[-1]['signal']
                signal_text = {
                    1: "📈 买入",
                    0: "➖ 观望",
                    -1: "📉 卖出"
                }
                signal_color = {
                    1: "green",
                    0: "gray",
                    -1: "red"
                }
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("最新信号", signal_text.get(latest_signal, "未知"))
                
                with col2:
                    st.metric("情感指数", f"{signal_df.iloc[-1]['sentiment_index']:.1f}")
                
                with col3:
                    st.metric("情感均值", f"{signal_df.iloc[-1]['sentiment_mean']:.3f}")
                
                # 信号历史
                fig = go.Figure()
                
                # 情感指数
                fig.add_trace(go.Scatter(
                    x=signal_df['date'],
                    y=signal_df['sentiment_index'],
                    mode='lines',
                    name='情感指数',
                    line=dict(color='#00D9FF'),
                    yaxis='y'
                ))
                
                # 信号
                buy_signals = signal_df[signal_df['signal'] == 1]
                sell_signals = signal_df[signal_df['signal'] == -1]
                
                if not buy_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=buy_signals['date'],
                        y=buy_signals['sentiment_index'],
                        mode='markers',
                        name='买入信号',
                        marker=dict(color='green', size=15, symbol='triangle-up')
                    ))
                
                if not sell_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=sell_signals['date'],
                        y=sell_signals['sentiment_index'],
                        mode='markers',
                        name='卖出信号',
                        marker=dict(color='red', size=15, symbol='triangle-down')
                    ))
                
                fig.update_layout(
                    title="情感信号历史",
                    xaxis_title="日期",
                    yaxis_title="情感指数",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 信号统计
                st.markdown("---")
                st.subheader("信号统计")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    buy_count = (signal_df['signal'] == 1).sum()
                    st.metric("买入信号数", buy_count)
                
                with col2:
                    sell_count = (signal_df['signal'] == -1).sum()
                    st.metric("卖出信号数", sell_count)
                
                with col3:
                    hold_count = (signal_df['signal'] == 0).sum()
                    st.metric("观望次数", hold_count)
                
            except Exception as e:
                st.error(f"生成失败: {e}")


# 缺少numpy导入
import numpy as np


if __name__ == "__main__":
    show_sentiment_page()

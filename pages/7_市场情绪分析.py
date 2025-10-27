"""
💬 市场情绪分析
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, kpi_card

inject_css()

# 初始化NLP情感分析器
@st.cache_resource
def init_sentiment_analyzer():
    try:
        from ai.nlp_sentiment import ChineseSentimentAnalyzer, SentimentConfig
        config = SentimentConfig()
        return ChineseSentimentAnalyzer(config)
    except Exception as e:
        st.error(f"情感分析器初始化失败: {str(e)}")
        return None

sentiment_analyzer = init_sentiment_analyzer()

st.title('💬 市场情绪分析')
st.caption('NLP情感分析 · 舆情监控 · 情绪指标')

st.divider()

# 单文本情感分析
section_header('message-square', '文本情感分析', '分析单条新闻或公告情感')

input_text = st.text_area(
    '输入文本',
    placeholder='输入新闻、公告或社交媒体文本...',
    height=120,
    key='input_text'
)

if st.button('🔍 分析情感', type='primary'):
    if not input_text.strip():
        st.warning('请输入文本内容')
    elif not sentiment_analyzer:
        st.error('情感分析器未初始化')
    else:
        with st.spinner('正在分析...'):
            try:
                result = sentiment_analyzer.analyze(input_text)
                
                # 显示结果
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    score = result.sentiment_score
                    label_map = {
                        'positive': '😊 正面',
                        'neutral': '😐 中性',
                        'negative': '😟 负面'
                    }
                    st.metric('情感倾向', label_map.get(result.sentiment_label, '未知'))
                
                with col2:
                    st.metric('情感得分', f'{result.sentiment_score:.3f}')
                
                with col3:
                    strength = abs(result.sentiment_score)
                    if strength < 0.2:
                        intensity = '弱'
                    elif strength < 0.5:
                        intensity = '中等'
                    else:
                        intensity = '强'
                    st.metric('情感强度', intensity)
                
                # 情感词汇
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('**🟢 正面词汇**')
                    if result.positive_words:
                        pos_text = ', '.join(result.positive_words)
                        st.success(pos_text)
                    else:
                        st.info('未检测到正面词汇')
                
                with col2:
                    st.markdown('**🔴 负面词汇**')
                    if result.negative_words:
                        neg_text = ', '.join(result.negative_words)
                        st.error(neg_text)
                    else:
                        st.info('未检测到负面词汇')
                
                # 关键词
                if result.keywords:
                    st.markdown('**🔑 关键词提取**')
                    keywords_str = ', '.join([f'{kw}({weight:.2f})' for kw, weight in result.keywords[:10]])
                    st.code(keywords_str, language='text')
                
            except Exception as e:
                st.error(f'分析失败: {str(e)}')
                import traceback
                st.code(traceback.format_exc())

st.divider()

# 批量情感分析
section_header('list', '批量情感分析', '分析多条文本的情感分布')

with st.expander('📋 批量分析', expanded=False):
    batch_texts = st.text_area(
        '输入多条文本（每行一条）',
        placeholder='每行输入一条新闻或公告...\n例如：\n比特币价格突破新高\n市场出现恐慌性抛售',
        height=150,
        key='batch_texts'
    )
    
    if st.button('🚀 批量分析', type='primary'):
        if not batch_texts.strip():
            st.warning('请输入文本内容')
        elif not sentiment_analyzer:
            st.error('情感分析器未初始化')
        else:
            texts = [t.strip() for t in batch_texts.split('\n') if t.strip()]
            
            if not texts:
                st.warning('没有有效的文本')
            else:
                with st.spinner(f'正在分析 {len(texts)} 条文本...'):
                    try:
                        results = sentiment_analyzer.analyze_batch(texts)
                        
                        # 统计
                        positive_count = sum(1 for r in results if r.sentiment_label == 'positive')
                        negative_count = sum(1 for r in results if r.sentiment_label == 'negative')
                        neutral_count = sum(1 for r in results if r.sentiment_label == 'neutral')
                        avg_score = sum(r.sentiment_score for r in results) / len(results)
                        
                        # 显示统计
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            kpi_card('总文本数', str(len(texts)), '', 'neutral')
                        
                        with col2:
                            pct = (positive_count / len(texts) * 100) if len(texts) > 0 else 0
                            kpi_card('正面', f'{positive_count}条', f'{pct:.1f}%', 'up')
                        
                        with col3:
                            pct = (negative_count / len(texts) * 100) if len(texts) > 0 else 0
                            kpi_card('负面', f'{negative_count}条', f'{pct:.1f}%', 'down')
                        
                        with col4:
                            kpi_card('平均得分', f'{avg_score:.3f}', '', 'neutral')
                        
                        # 情感分布饼图
                        fig = go.Figure(data=[go.Pie(
                            labels=['正面', '中性', '负面'],
                            values=[positive_count, neutral_count, negative_count],
                            marker=dict(colors=['#00D9FF', '#888', '#FF4B4B']),
                            hole=0.4
                        )])
                        fig.update_layout(
                            title='情感分布',
                            template='plotly_dark',
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 详细结果表
                        st.markdown('### 详细结果')
                        table_data = []
                        for i, result in enumerate(results, 1):
                            label_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}
                            table_data.append({
                                '序号': i,
                                '文本': result.text[:50] + '...' if len(result.text) > 50 else result.text,
                                '情感': f"{label_emoji[result.sentiment_label]} {result.sentiment_label}",
                                '得分': f'{result.sentiment_score:.3f}',
                                '正面词': len(result.positive_words),
                                '负面词': len(result.negative_words)
                            })
                        
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, hide_index=True, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f'批量分析失败: {str(e)}')
                        import traceback
                        st.code(traceback.format_exc())

st.divider()

# 情绪指标示例
section_header('activity', '市场情绪指标', '基于历史数据的情绪趋势')

st.info('💡 此模块展示情绪指标的计算方法，实际应用需要连接真实新闻数据源')

# 模拟情绪时间序列
dates = [(datetime.now() - timedelta(days=30-i)).strftime('%m-%d') for i in range(30)]
sentiment_scores = [0.3 + 0.4 * (i % 7 - 3) / 7 for i in range(30)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=sentiment_scores,
    mode='lines+markers',
    name='情绪指数',
    line=dict(color='#00D9FF', width=2),
    fill='tozeroy',
    fillcolor='rgba(0, 217, 255, 0.1)'
))
fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="中性线")
fig.update_layout(
    title='市场情绪趋势 (近30日)',
    xaxis_title='日期',
    yaxis_title='情绪得分',
    template='plotly_dark',
    height=350
)
st.plotly_chart(fig, use_container_width=True)

# 情绪指标说明
with st.expander('ℹ️ 情绪指标说明'):
    st.markdown("""
    ### 情感得分
    - **范围**: -1 (极度负面) 到 +1 (极度正面)
    - **中性区间**: -0.3 到 +0.3
    - **计算方法**: (正面词数 - 负面词数) / 总情感词数
    
    ### 应用场景
    1. **市场情绪监控**: 追踪新闻、公告的整体情感倾向
    2. **反向指标**: 极度乐观/悲观可能预示反转
    3. **组合策略**: 与技术指标结合使用
    4. **风险预警**: 负面情绪激增时提高警惕
    
    ### 数据来源建议
    - 财经新闻网站 (新浪财经、东方财富等)
    - 社交媒体 (微博、Twitter等)
    - 公司公告
    - 分析师报告
    """)

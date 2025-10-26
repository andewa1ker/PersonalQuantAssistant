"""
🛡️ 风险管理中心
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, kpi_card, pill_badge

inject_css()

st.title('🛡️ 风险管理中心')
st.caption('实时风控监控 · 智能预警系统')

st.divider()

# 风险指标
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card('风险评分', '72/100', '良好', None)
with col2:
    kpi_card('最大回撤', '-8.5%', '安全', None)
with col3:
    kpi_card('夏普比率', '1.85', '优秀', None)
with col4:
    kpi_card('波动率', '12.3%', '中等', None)

st.divider()

# 风险分布
section_header('shield-check', '风险分析', '各维度风险评估')

col1, col2 = st.columns(2)

with col1:
    # 雷达图
    categories = ['市场风险', '流动性风险', '信用风险', '操作风险', '合规风险']
    values = [75, 82, 90, 68, 95]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255,122,41,0.2)',
        line=dict(color=TOKENS['accent'], width=2),
        name='当前风险',
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color=TOKENS['text_weak']),
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color=TOKENS['text_weak']),
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=350,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.markdown(f'<div style="padding:1rem 0"></div>', unsafe_allow_html=True)
    
    for cat, val in zip(categories, values):
        tone = 'success' if val >= 80 else 'warning' if val >= 60 else 'danger'
        color = '#4CAF50' if val >= 80 else '#FFA726' if val >= 60 else '#EF5350'
        
        st.markdown(f'''<div style="margin-bottom:1.5rem">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
        <span style="color:{TOKENS['text']};font-weight:500">{cat}</span>
        <span style="color:{color};font-weight:600">{val}分</span>
        </div>
        <div style="height:8px;background:{TOKENS['panel']};border-radius:4px;overflow:hidden">
        <div style="height:100%;background:{color};width:{val}%;transition:all 0.3s"></div>
        </div></div>''', unsafe_allow_html=True)

st.divider()

# 预警列表
section_header('alert-triangle', '风险预警', '需要关注的风险事件')

alerts = [
    {'type': '高', 'msg': '策略A仓位接近上限 (95%)', 'time': '5分钟前', 'tone': 'danger'},
    {'type': '中', 'msg': '波动率超过历史平均水平', 'time': '1小时前', 'tone': 'warning'},
    {'type': '低', 'msg': '系统自动调仓提醒', 'time': '2小时前', 'tone': 'info'},
]

for alert in alerts:
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        st.markdown(pill_badge(alert['type'], alert['tone']), unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="padding:0.5rem 0">{alert["msg"]}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="color:{TOKENS["text_weak"]};padding:0.5rem 0;text-align:right">{alert["time"]}</div>', unsafe_allow_html=True)

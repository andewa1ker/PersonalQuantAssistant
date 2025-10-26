"""
PersonalQuantAssistant - 欢迎页面
"""
import streamlit as st
from design_system import inject_css, TOKENS
from ds_icons import icon

inject_css()

st.title('🎯 Personal Quant Assistant')
st.markdown(f'<h3 style="color:{TOKENS["text_weak"]};font-weight:400">AI驱动的量化投资分析平台</h3>', unsafe_allow_html=True)

st.divider()

# 功能介绍
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'''<div style="background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
    border-radius:18px;padding:2rem;text-align:center;min-height:220px">
    <div style="font-size:3rem;margin-bottom:1rem">{icon('dashboard', 48, TOKENS['accent'])}</div>
    <h3 style="margin:0 0 0.75rem">实时监控</h3>
    <p style="color:{TOKENS['text_weak']};margin:0">多维度资产监控<br/>智能风险预警系统</p>
    </div>''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''<div style="background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
    border-radius:18px;padding:2rem;text-align:center;min-height:220px">
    <div style="font-size:3rem;margin-bottom:1rem">{icon('wand', 48, TOKENS['accent'])}</div>
    <h3 style="margin:0 0 0.75rem">量化策略</h3>
    <p style="color:{TOKENS['text_weak']};margin:0">AI智能信号分析<br/>多策略组合优化</p>
    </div>''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''<div style="background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
    border-radius:18px;padding:2rem;text-align:center;min-height:220px">
    <div style="font-size:3rem;margin-bottom:1rem">{icon('shield-check', 48, TOKENS['accent'])}</div>
    <h3 style="margin:0 0 0.75rem">风险管理</h3>
    <p style="color:{TOKENS['text_weak']};margin:0">实时风险评估<br/>智能止损止盈</p>
    </div>''', unsafe_allow_html=True)

st.divider()

# 快速导航
st.markdown(f'''<h2 style="margin:2rem 0 1rem">
<span class="icon">{icon('layers', 24, TOKENS['accent'])}</span>
快速开始</h2>''', unsafe_allow_html=True)

st.info('👈 请从左侧菜单选择功能模块开始使用')

# 统计数据
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('支持策略', '8+')
with col2:
    st.metric('数据源', '4+')
with col3:
    st.metric('更新频率', '实时')
with col4:
    st.metric('AI模型', '3+')

st.divider()

# 系统状态
st.markdown(f'''<h3 style="margin:1.5rem 0 1rem">
<span class="icon">{icon('activity', 20, TOKENS['accent'])}</span>
系统状态</h3>''', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.success('✅ 所有服务运行正常')
    st.info('💡 提示：首次使用请先在"系统设置"中配置数据源')
with col2:
    st.markdown(f'''<div style="background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
    border-radius:12px;padding:1.5rem">
    <div style="color:{TOKENS['text_weak']};margin-bottom:0.5rem">版本信息</div>
    <div style="font-weight:600;font-size:1.25rem">v2.0.0</div>
    <div style="color:{TOKENS['text_weak']};font-size:0.9rem;margin-top:0.5rem">设计系统重构版</div>
    </div>''', unsafe_allow_html=True)

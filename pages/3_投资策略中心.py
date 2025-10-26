"""
🎯 投资策略中心
"""
import streamlit as st
import pandas as pd
from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, pill_badge, form_row

inject_css()

st.title('🎯 投资策略中心')
st.caption('自定义量化策略 · 智能参数优化')

st.divider()

# 策略列表
section_header('wand', '我的策略', '已配置策略列表')

strategies = [
    {'name': '动量突破策略', 'status': '运行中', 'return': '+12.5%', 'tone': 'success'},
    {'name': '均值回归策略', 'status': '运行中', 'return': '+8.3%', 'tone': 'success'},
    {'name': '趋势跟踪策略', 'status': '已暂停', 'return': '+5.2%', 'tone': 'warning'},
    {'name': '套利策略A', 'status': '测试中', 'return': '+2.1%', 'tone': 'info'},
]

for s in strategies:
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f'<div style="font-weight:600;padding:0.5rem 0">{s["name"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(pill_badge(s['status'], s['tone']), unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="color:#4CAF50;font-weight:600;padding:0.5rem 0">{s["return"]}</div>', unsafe_allow_html=True)
    with col4:
        st.button('编辑', key=f'edit_{s["name"]}', use_container_width=True)

st.divider()

# 新建策略
section_header('sliders-vertical', '策略配置', '创建新策略或调整参数')

with st.expander('📝 创建新策略', expanded=False):
    form_row('策略名称', lambda: st.text_input('', placeholder='输入策略名称', key='new_strategy_name', label_visibility='collapsed'))
    form_row('策略类型', lambda: st.selectbox('', ['动量策略', '均值回归', '趋势跟踪', '套利策略'], key='strategy_type', label_visibility='collapsed'))
    form_row('交易周期', lambda: st.select_slider('', options=['日内', '日线', '周线', '月线'], key='period', label_visibility='collapsed'))
    form_row('止损比例', lambda: st.slider('', 0.0, 20.0, 5.0, 0.5, key='stop_loss', label_visibility='collapsed', format='%g%%'))
    form_row('仓位上限', lambda: st.slider('', 0, 100, 30, 5, key='position_limit', label_visibility='collapsed', format='%g%%'))
    
    st.markdown('<div style="margin-top:1.5rem"></div>', unsafe_allow_html=True)
    if st.button('✨ 创建策略', use_container_width=True, type='primary'):
        st.success('策略创建成功！')

st.divider()

# 策略对比
section_header('chart-histogram', '收益对比', '近30日各策略表现')

df = pd.DataFrame({
    '策略': ['动量突破', '均值回归', '趋势跟踪', '套利策略A'],
    '7日收益': ['+2.1%', '+1.8%', '+3.2%', '+0.8%'],
    '30日收益': ['+8.5%', '+6.3%', '+10.2%', '+3.1%'],
    '夏普比率': [1.85, 2.12, 1.68, 1.23],
    '最大回撤': ['-5.2%', '-3.8%', '-8.5%', '-2.1%'],
})

st.dataframe(df, use_container_width=True, hide_index=True)

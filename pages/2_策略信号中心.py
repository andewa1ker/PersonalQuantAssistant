"""
📡 策略信号中心
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, pill_badge, data_table

inject_css()

st.title('📡 策略信号中心')
st.caption('实时监控交易信号 · AI智能分析')

st.divider()

# 信号概览
section_header('beacon', '实时信号', '最新交易机会')

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f'<div style="color:{TOKENS["text_weak"]}">策略名称</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="color:{TOKENS["text_weak"]}">信号强度</div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div style="color:{TOKENS["text_weak"]}">操作建议</div>', unsafe_allow_html=True)

# 信号列表
signals = [
    {'strategy': '动量突破', 'symbol': '000001.SH', 'strength': 85, 'action': '买入', 'tone': 'success'},
    {'strategy': '均值回归', 'symbol': '600519.SH', 'strength': 72, 'action': '持有', 'tone': 'info'},
    {'strategy': '趋势跟踪', 'symbol': '000858.SZ', 'strength': 68, 'action': '观察', 'tone': 'neutral'},
    {'strategy': '反转策略', 'symbol': '601318.SH', 'strength': 45, 'action': '卖出', 'tone': 'danger'},
]

for sig in signals:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'''<div style="padding:0.75rem 0">
        <span style="font-weight:600">{sig['strategy']}</span>
        <span style="color:{TOKENS['text_weak']};margin-left:0.5rem">{sig['symbol']}</span>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.progress(sig['strength'] / 100)
        st.caption(f"{sig['strength']}%")
    with col3:
        st.markdown(pill_badge(sig['action'], sig['tone']), unsafe_allow_html=True)

st.divider()

# 历史信号
section_header('history', '历史回测', '信号胜率统计')

df = pd.DataFrame({
    '策略': ['动量突破', '均值回归', '趋势跟踪', '反转策略'],
    '信号数': [156, 203, 178, 134],
    '胜率': ['68.5%', '72.3%', '65.2%', '58.7%'],
    '平均收益': ['+3.2%', '+2.8%', '+4.1%', '+1.9%'],
    '最大回撤': ['-8.5%', '-6.2%', '-12.3%', '-15.7%'],
})

data_table(df)

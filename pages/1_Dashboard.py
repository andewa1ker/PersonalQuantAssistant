"""
📊 主控面板
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from design_system import inject_css
from ds_icons import icon
from ds_components import section_header, kpi_card, line_area_chart, tx_list

inject_css()

st.title('📊 量化投资主控面板')
st.caption('实时监控 · 智能决策 · 风险可控')

st.divider()

# KPI指标
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card('总资产', '¥1,265,480', '+8.2%', 'up')
with col2:
    kpi_card('今日收益', '¥+3,240', '+0.26%', 'up')
with col3:
    kpi_card('月度收益', '¥+52,800', '+4.36%', 'up')
with col4:
    kpi_card('年化收益', '18.5%', '+2.1%', 'up')

st.divider()

# 趋势图表
col1, col2 = st.columns([2, 1])

with col1:
    section_header('activity', '资产趋势', '近30日净值变化')
    dates = [(datetime.now() - timedelta(days=30-i)).strftime('%m-%d') for i in range(30)]
    values = [1200000 + i*2000 + (i%3)*500 for i in range(30)]
    line_area_chart(dates, values)

with col2:
    section_header('wallet', '最近交易', '实时资金动向')
    tx_list([
        {'icon': 'trending-up', 'title': '策略A买入', 'tag': '沪深300', 'amount': -50000, 'time': '10:15'},
        {'icon': 'trending-down', 'title': '策略B卖出', 'tag': '中证500', 'amount': +32000, 'time': '09:30'},
        {'icon': 'check-circle', 'title': '分红到账', 'tag': '股息', 'amount': +1200, 'time': '昨天'},
    ])

st.divider()

# 持仓分布
section_header('layers', '持仓概览', '按板块分布')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric('科技板块', '35%', '+2%')
with col2:
    st.metric('消费板块', '28%', '-1%')
with col3:
    st.metric('医药板块', '22%', '+3%')

"""
📥 数据导出
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, form_row

inject_css()

st.title('📥 数据导出')
st.caption('历史数据导出 · 报表生成')

st.divider()

# 导出选项
section_header('file-down', '导出数据', '选择时间范围和数据类型')

with st.form('export_form'):
    form_row('数据类型', lambda: st.multiselect('', ['持仓记录', '交易明细', '策略信号', '收益曲线', '风险报告'], default=['持仓记录'], key='data_types', label_visibility='collapsed'))
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('开始日期', value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input('结束日期', value=datetime.now())
    
    form_row('导出格式', lambda: st.radio('', ['Excel (.xlsx)', 'CSV (.csv)', 'JSON (.json)'], key='format', horizontal=True, label_visibility='collapsed'))
    
    submitted = st.form_submit_button('📦 生成导出文件', use_container_width=True, type='primary')
    
    if submitted:
        st.success('✅ 文件生成成功！')
        st.download_button(
            label='⬇️ 下载文件',
            data='示例数据',
            file_name=f'export_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mime='application/vnd.ms-excel',
            use_container_width=True,
        )

st.divider()

# 快速导出
section_header('download', '快速导出', '常用报表模板')

quick_exports = [
    {'name': '今日交易汇总', 'desc': '今日所有交易记录', 'icon': 'calendar'},
    {'name': '月度收益报告', 'desc': '本月收益与持仓分析', 'icon': 'chart-histogram'},
    {'name': '策略表现报告', 'desc': '各策略详细指标', 'icon': 'wand'},
    {'name': '风险评估报告', 'desc': '全面风险分析', 'icon': 'shield-check'},
]

col1, col2 = st.columns(2)

for i, exp in enumerate(quick_exports):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f'''<div style="background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
        border-radius:12px;padding:1.5rem;margin-bottom:1rem;transition:all 0.2s;cursor:pointer"
        onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='{TOKENS['shadow']}'"
        onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem">
        <span class="icon">{icon(exp['icon'], 24, TOKENS['accent'])}</span>
        <span style="font-weight:600;font-size:1.1rem">{exp['name']}</span>
        </div>
        <p style="color:{TOKENS['text_weak']};margin:0 0 1rem">{exp['desc']}</p>
        </div>''', unsafe_allow_html=True)
        
        if st.button(f'📥 导出', key=f'quick_{i}', use_container_width=True):
            st.success(f'✅ {exp["name"]} 导出成功！')

st.divider()

# 历史记录
section_header('history', '导出记录', '最近的导出文件')

df = pd.DataFrame({
    '文件名': ['export_20241127.xlsx', 'report_20241126.csv', 'signals_20241125.json'],
    '类型': ['持仓记录', '收益曲线', '策略信号'],
    '大小': ['2.3 MB', '856 KB', '125 KB'],
    '时间': ['2小时前', '昨天 14:30', '2天前'],
})

st.dataframe(df, use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.button('⬇️ 下载', key='dl_1', use_container_width=True)
with col2:
    st.button('⬇️ 下载', key='dl_2', use_container_width=True)
with col3:
    st.button('⬇️ 下载', key='dl_3', use_container_width=True)

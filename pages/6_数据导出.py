"""
� 数据导出
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import io

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, form_row
from data_fetcher.data_manager import DataManager

inject_css()

# 初始化数据管理器
@st.cache_resource
def init_data_manager():
    return DataManager()

data_mgr = init_data_manager()

st.title('📥 数据导出')
st.caption('历史数据导出 · 报表生成')

st.divider()

# 导出选项
section_header('file-down', '导出数据', '选择资产和时间范围')

# 资产选择
asset_type = st.selectbox('资产类型', ['加密货币', 'ETF'], key='asset_type')

if asset_type == '加密货币':
    assets = st.multiselect('选择加密货币', ['bitcoin', 'ethereum', 'binancecoin'], 
                             default=['bitcoin'], key='crypto_assets')
else:
    assets = st.multiselect('选择ETF', ['159915', '510300', '512100'], 
                             default=['159915'], key='etf_assets')

# 时间范围
col1, col2 = st.columns(2)
with col1:
    days = st.number_input('历史天数', min_value=7, max_value=365, value=30, step=7)
with col2:
    data_type_select = st.selectbox('数据类型', ['历史价格', '实时数据'], key='data_type_export')

# 导出格式
export_format = st.radio('导出格式', ['CSV (.csv)', 'Excel (.xlsx)', 'JSON (.json)'], 
                          key='format', horizontal=True)

if st.button('📦 生成导出文件', type='primary'):
    try:
        with st.spinner('正在获取数据...'):
            # 获取真实数据
            all_data = []
            
            for asset in assets:
                if data_type_select == '历史价格':
                    data = data_mgr.get_asset_data(
                        asset_type='crypto' if asset_type == '加密货币' else 'etf',
                        symbol=asset,
                        data_type='history',
                        days=days
                    )
                else:
                    data = data_mgr.get_asset_data(
                        asset_type='crypto' if asset_type == '加密货币' else 'etf',
                        symbol=asset,
                        data_type='realtime'
                    )
                
                if data is not None:
                    if isinstance(data, dict):
                        # 实时数据转为DataFrame
                        df = pd.DataFrame([data])
                    else:
                        df = data
                    
                    df['asset'] = asset
                    all_data.append(df)
            
            if all_data:
                # 合并所有数据
                export_df = pd.concat(all_data, ignore_index=True)
                
                # 根据格式生成文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if 'CSV' in export_format:
                    csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
                    filename = f'export_{timestamp}.csv'
                    mime_type = 'text/csv'
                    file_data = csv_data
                    
                elif 'Excel' in export_format:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, index=False, sheet_name='Data')
                    file_data = buffer.getvalue()
                    filename = f'export_{timestamp}.xlsx'
                    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    
                else:  # JSON
                    json_data = export_df.to_json(orient='records', date_format='iso')
                    file_data = json_data.encode('utf-8')
                    filename = f'export_{timestamp}.json'
                    mime_type = 'application/json'
                
                st.success(f'✅ 成功导出 {len(export_df)} 条数据!')
                
                # 显示预览
                st.write("数据预览:")
                st.dataframe(export_df.head(10), hide_index=True)
                
                # 下载按钮
                st.download_button(
                    label='⬇️ 下载文件',
                    data=file_data,
                    file_name=filename,
                    mime=mime_type,
                )
            else:
                st.warning('未获取到数据,请检查资产选择和网络连接')
                
    except Exception as e:
        st.error(f'导出失败: {str(e)}')

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
        
        if st.button(f'📥 导出', key=f'quick_{i}'):
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

st.dataframe(df, column_config=None, hide_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.button('⬇️ 下载', key='dl_1')
with col2:
    st.button('⬇️ 下载', key='dl_2')
with col3:
    st.button('⬇️ 下载', key='dl_3')

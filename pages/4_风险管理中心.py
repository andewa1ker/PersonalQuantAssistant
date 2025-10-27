"""
🛡️ 风险管理中心
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, kpi_card, pill_badge
from data_fetcher.data_manager import DataManager
from risk_management.risk_monitor import RiskMonitor
from risk_management.risk_measurement import RiskMeasurement

inject_css()

# 初始化
@st.cache_resource
def init_managers():
    data_mgr = DataManager()
    risk_monitor = RiskMonitor()
    risk_measurement = RiskMeasurement()
    return data_mgr, risk_monitor, risk_measurement

data_mgr, risk_monitor, risk_measurement = init_managers()

st.title('🛡️ 风险管理中心')
st.caption('实时风控监控 · 智能预警系统')

st.divider()

# 资产选择
asset_options = {
    'BTC': ('crypto', 'bitcoin'),
    'ETH': ('crypto', 'ethereum'),
    'BNB': ('crypto', 'binancecoin')
}

selected_asset = st.selectbox('选择资产', list(asset_options.keys()), key='risk_asset')
asset_type, asset_symbol = asset_options[selected_asset]

# 获取历史数据并计算风险指标
with st.spinner('计算风险指标...'):
    try:
        # 获取历史数据
        data = data_mgr.get_asset_data(
            asset_type=asset_type,
            symbol=asset_symbol,
            data_type='history',
            days=90
        )
        
        if data is not None and len(data) > 0:
            # 计算风险指标
            metrics = risk_measurement.calculate_metrics(data, asset_symbol=selected_asset)
            
            # 监控风险并获取告警
            _, alerts = risk_monitor.monitor_asset_risk(data, asset_symbol=selected_asset)
            
            # 显示核心风险指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                risk_score = metrics.risk_score if metrics.risk_score else 0
                kpi_card('风险评分', f'{risk_score:.0f}/100', metrics.risk_level, None)
            
            with col2:
                max_dd = metrics.max_drawdown if metrics.max_drawdown else 0
                kpi_card('最大回撤', f'{max_dd:.2%}', 
                        '安全' if max_dd > -0.10 else '警告', None)
            
            with col3:
                sharpe = metrics.sharpe_ratio if metrics.sharpe_ratio else 0
                kpi_card('夏普比率', f'{sharpe:.2f}', 
                        '优秀' if sharpe > 1.5 else '良好', None)
            
            with col4:
                vol = metrics.volatility if metrics.volatility else 0
                kpi_card('波动率', f'{vol:.2%}', 
                        '低' if vol < 0.20 else '中', None)
            
        else:
            st.warning('无法获取数据，请检查网络连接')
            metrics = None
            alerts = []
            
    except Exception as e:
        st.error(f'风险计算失败: {str(e)}')
        metrics = None
        alerts = []

st.divider()

# 风险分布
section_header('shield-check', '风险分析', '各维度风险评估')

if metrics:
    col1, col2 = st.columns(2)
    
    with col1:
        # 风险维度雷达图 - 基于真实指标计算
        categories = ['收益风险', '波动风险', '回撤风险', '流动性风险', '综合风险']
        
        # 根据实际指标计算各维度得分 (0-100, 越高越好)
        return_score = min(100, max(0, (metrics.annualized_return + 0.5) * 100)) if metrics.annualized_return else 50
        volatility_score = min(100, max(0, (1 - metrics.volatility) * 100)) if metrics.volatility else 50
        drawdown_score = min(100, max(0, (1 + metrics.max_drawdown) * 100)) if metrics.max_drawdown else 50
        liquidity_score = 85  # 加密货币流动性较好，固定值
        comprehensive_score = metrics.risk_score if metrics.risk_score else 70
        
        values = [return_score, volatility_score, drawdown_score, liquidity_score, comprehensive_score]
        
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
        
        st.plotly_chart(fig, config={'displayModeBar': False})
    
    with col2:
        st.markdown(f'<div style="padding:1rem 0"></div>', unsafe_allow_html=True)
        
        for cat, val in zip(categories, values):
            tone = 'success' if val >= 80 else 'warning' if val >= 60 else 'danger'
            color = '#4CAF50' if val >= 80 else '#FFA726' if val >= 60 else '#EF5350'
            
            st.markdown(f'''<div style="margin-bottom:1.5rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
            <span style="color:{TOKENS['text']};font-weight:500">{cat}</span>
            <span style="color:{color};font-weight:600">{val:.0f}分</span>
            </div>
            <div style="height:8px;background:{TOKENS['panel']};border-radius:4px;overflow:hidden">
            <div style="height:100%;background:{color};width:{val}%;transition:all 0.3s"></div>
            </div></div>''', unsafe_allow_html=True)
        
        # 显示详细风险指标
        st.markdown("---")
        st.markdown("**详细指标**")
        
        detail_metrics = {
            'VaR (95%)': f'{metrics.var_95:.2%}' if metrics.var_95 else 'N/A',
            'CVaR (95%)': f'{metrics.cvar_95:.2%}' if metrics.cvar_95 else 'N/A',
            '索提诺比率': f'{metrics.sortino_ratio:.2f}' if metrics.sortino_ratio else 'N/A',
            '卡玛比率': f'{metrics.calmar_ratio:.2f}' if metrics.calmar_ratio else 'N/A',
        }
        
        for key, value in detail_metrics.items():
            st.markdown(f'**{key}**: {value}')
else:
    st.info('等待数据加载...')

st.divider()

# 预警列表
section_header('alert-triangle', '风险预警', '需要关注的风险事件')

if alerts and len(alerts) > 0:
    for alert in alerts:
        # 映射告警级别到显示样式
        severity_map = {
            'high': {'label': '高', 'tone': 'danger'},
            'medium': {'label': '中', 'tone': 'warning'},
            'low': {'label': '低', 'tone': 'info'}
        }
        
        severity_info = severity_map.get(alert.severity, {'label': '中', 'tone': 'warning'})
        
        col1, col2, col3 = st.columns([1, 4, 2])
        with col1:
            st.markdown(pill_badge(severity_info['label'], severity_info['tone']), unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="padding:0.5rem 0">{alert.message}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div style="color:{TOKENS["text_weak"]};padding:0.5rem 0;text-align:right">{alert.timestamp}</div>', unsafe_allow_html=True)
else:
    st.success('✅ 当前无风险预警，系统运行正常')

# 添加历史告警记录
with st.expander('📜 查看历史预警记录'):
    if metrics:
        st.markdown(f"""
        **最近90天风险概况**:
        - 平均波动率: {metrics.volatility:.2%} if metrics.volatility else 'N/A'
        - 最大单日回撤: {metrics.max_drawdown:.2%} if metrics.max_drawdown else 'N/A'
        - 年化收益率: {metrics.annualized_return:.2%} if metrics.annualized_return else 'N/A'
        - 风险调整后收益 (夏普): {metrics.sharpe_ratio:.2f} if metrics.sharpe_ratio else 'N/A'
        """)
    else:
        st.info('暂无历史记录')

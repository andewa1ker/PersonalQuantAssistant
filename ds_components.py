"""
UI组件库 - 可复用组件
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ds_icons import icon
from design_system import TOKENS

def section_header(icon_name: str, title: str, subtitle: str = None):
    """页面区块标题"""
    sub = f'<p style="color:{TOKENS["text_weak"]};margin:0.5rem 0 0">{subtitle}</p>' if subtitle else ''
    st.markdown(f'''<div class="slide-in" style="margin-bottom:1.5rem">
    <h2 style="display:flex;align-items:center;gap:12px;margin:0;font-size:1.75rem">
    <span class="icon">{icon(icon_name, 24, TOKENS["accent"])}</span>{title}</h2>
    {sub}</div>''', unsafe_allow_html=True)

def kpi_card(title: str, value: str, delta: str = None, trend: str = None):
    """KPI指标卡"""
    delta_html = ''
    if delta:
        color = '#4CAF50' if trend == 'up' else '#EF5350' if trend == 'down' else TOKENS['text_weak']
        icon_name = 'trending-up' if trend == 'up' else 'trending-down' if trend == 'down' else 'activity'
        delta_html = f'<div class="kpi-delta" style="color:{color}"><span class="icon">{icon(icon_name,16,color)}</span> {delta}</div>'
    
    st.markdown(f'''<div class="kpi-card">
    <div class="kpi-label">{title}</div>
    <div class="kpi-value">{value}</div>
    {delta_html}</div>''', unsafe_allow_html=True)

def pill_badge(text: str, tone: str = 'neutral'):
    """徽章"""
    return f'<span class="pill-badge pill-{tone}">{text}</span>'

def line_area_chart(dates: list, values: list, title: str = '', color: str = None):
    """折线面积图"""
    if not color:
        color = TOKENS['accent']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode='lines',
        name='',
        line=dict(color=color, width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=f'rgba(255,122,41,0.15)',
        hovertemplate='%{x}<br>¥%{y:,.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=title if title else None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TOKENS['text_weak'], family='Inter'),
        xaxis=dict(
            showgrid=True, gridcolor='rgba(255,255,255,0.05)',
            showline=False, zeroline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor='rgba(255,255,255,0.05)',
            showline=False, zeroline=False,
        ),
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def tx_list(items: list):
    """交易列表"""
    for tx in items:
        amount_color = '#4CAF50' if tx['amount'] > 0 else '#EF5350'
        amount_sign = '+' if tx['amount'] > 0 else ''
        
        st.markdown(f'''<div style="display:flex;align-items:center;gap:1rem;padding:1rem;border-radius:12px;
        margin-bottom:0.5rem;transition:all 0.2s;cursor:pointer;border:1px solid {TOKENS['panel_border']}"
        onmouseover="this.style.background='rgba(255,255,255,0.05)';this.style.transform='translateY(-2px)'"
        onmouseout="this.style.background='transparent';this.style.transform='translateY(0)'">
        <div style="width:40px;height:40px;border-radius:12px;background:{TOKENS['panel']};
        display:flex;align-items:center;justify-content:center">
        <span class="icon">{icon(tx.get('icon', 'wallet'), 20, TOKENS['accent'])}</span></div>
        <div style="flex:1">
        <div style="font-weight:600;color:{TOKENS['text']}">{tx['title']}</div>
        <div style="font-size:0.85rem;color:{TOKENS['text_weak']}">{tx.get('tag', '')}</div>
        </div>
        <div style="text-align:right">
        <div style="font-weight:700;font-size:1.1rem;color:{amount_color}">{amount_sign}¥{abs(tx['amount']):,.2f}</div>
        <div style="font-size:0.8rem;color:{TOKENS['text_weak']}">{tx['time']}</div>
        </div></div>''', unsafe_allow_html=True)

def data_table(df: pd.DataFrame, zebra: bool = True, compact: bool = True):
    """数据表格"""
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=None if not compact else 400,
    )

def form_row(label: str, control):
    """表单行"""
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div style="padding-top:0.5rem;color:{TOKENS["text_weak"]};font-weight:500">{label}</div>', unsafe_allow_html=True)
    with col2:
        control()

def toast(message: str, tone: str = 'success'):
    """Toast通知"""
    colors = {
        'success': '#4CAF50',
        'info': '#42A5F5',
        'warning': '#FFA726',
        'error': '#EF5350',
    }
    color = colors.get(tone, colors['info'])
    
    st.markdown(f'''<div class="fade-in" style="position:fixed;top:20px;right:20px;
    background:{TOKENS['panel']};border:1px solid {TOKENS['panel_border']};
    border-left:4px solid {color};border-radius:12px;padding:1rem 1.5rem;
    box-shadow:{TOKENS['shadow']};z-index:9999;display:flex;align-items:center;gap:0.75rem">
    <span style="color:{color};font-weight:600">{message}</span>
    </div>''', unsafe_allow_html=True)

def empty_lottie(kind: str = 'loading'):
    """空态/加载动画"""
    try:
        from streamlit_lottie import st_lottie
        import requests
        
        urls = {
            'loading': 'https://assets10.lottiefiles.com/packages/lf20_hxart6lz.json',
            'empty': 'https://assets4.lottiefiles.com/packages/lf20_uu3p3ahq.json',
        }
        
        r = requests.get(urls.get(kind, urls['loading']))
        if r.status_code == 200:
            st_lottie(r.json(), height=200, key=f'lottie_{kind}')
        else:
            st.info(f"{kind}...")
    except:
        st.info(f"{kind}...")

def segmented_tabs(items: list, key: str):
    """分段标签"""
    return st.selectbox('', items, key=key, label_visibility='collapsed')

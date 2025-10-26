"""
Premium组件库 - 深色金融风格UI组件
包含账户卡、收益曲线、交易列表、统计环形图等
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from icons import icon, get_icon_group
from styles_premium import DESIGN_TOKENS


# ==================== 账户总览卡 ====================
def render_balance_card(balance: dict, user: dict = None):
    """
    渲染账户总览卡
    
    参数:
        balance: {"total": 27802.05, "change_pct": 0.15, "change_amount": 412.50}
        user: {"name": "Ghulam"}
    """
    total = balance.get('total', 0)
    change_pct = balance.get('change_pct', 0)
    change_amount = balance.get('change_amount', 0)
    
    # 涨跌徽章颜色
    badge_class = "badge-success" if change_pct >= 0 else "badge-error"
    arrow_icon = icon('trending_up', 16) if change_pct >= 0 else icon('trending_down', 16)
    sign = "+" if change_pct >= 0 else ""
    
    html = f"""
    <div class="premium-card fade-in" style="position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
            <div>
                <div style="color: {DESIGN_TOKENS['text_secondary']}; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    {icon('wallet', 18, DESIGN_TOKENS['text_secondary'])}
                    <span style="margin-left: 0.5rem;">您的余额</span>
                </div>
                <div style="font-size: 3rem; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1.2;">
                    ¥{total:,.2f}
                </div>
            </div>
            <div class="badge {badge_class}" style="margin-top: 0.5rem;">
                {arrow_icon}
                <span>{sign}{change_pct*100:.2f}%</span>
            </div>
        </div>
        
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
            <div style="color: {DESIGN_TOKENS['text_secondary']}; font-size: 0.9rem;">
                今日变动:
            </div>
            <div style="color: {'#4CAF50' if change_amount >= 0 else '#EF5350'}; font-weight: 600; font-variant-numeric: tabular-nums;">
                {sign}¥{abs(change_amount):,.2f}
            </div>
        </div>
        
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid {DESIGN_TOKENS['border']};">
            <button class="secondary-button" style="flex: 1; padding: 0.75rem; border-radius: 12px; background: {DESIGN_TOKENS['bg_elevated']}; border: 1px solid {DESIGN_TOKENS['border']}; color: {DESIGN_TOKENS['text_secondary']}; cursor: pointer; transition: all 0.2s;">
                {icon('upload', 18)}
                <span style="margin-left: 0.5rem;">导入数据</span>
            </button>
            <button style="flex: 1; padding: 0.75rem; border-radius: 12px; background: linear-gradient(135deg, #FF6A00, #FFA54C); border: none; color: white; font-weight: 600; cursor: pointer; box-shadow: 0 4px 16px rgba(255, 106, 0, 0.3); transition: all 0.25s;">
                {icon('refresh', 18, 'white')}
                <span style="margin-left: 0.5rem;">同步交易</span>
            </button>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


# ==================== 收益曲线图 ====================
def render_profit_chart(chart_data: dict, title: str = "收益走势"):
    """
    渲染收益曲线图
    
    参数:
        chart_data: {"dates": [...], "values": [...]}
        title: 图表标题
    """
    dates = chart_data.get('dates', [])
    values = chart_data.get('values', [])
    
    fig = go.Figure()
    
    # 添加面积填充
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name='收益',
        line=dict(
            color='#FF7A29',
            width=3,
            shape='spline',
        ),
        fill='tozeroy',
        fillcolor='rgba(255, 122, 41, 0.15)',
        hovertemplate='<b>%{x}</b><br>收益: ¥%{y:,.2f}<extra></extra>',
    ))
    
    # 添加圆点标记
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='markers',
        name='数据点',
        marker=dict(
            color='#FF7A29',
            size=8,
            line=dict(color='white', width=2)
        ),
        hoverinfo='skip',
    ))
    
    # 布局设置
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b>',
            font=dict(size=18, color=DESIGN_TOKENS['text_primary']),
            x=0,
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family=DESIGN_TOKENS['font_family'],
            color=DESIGN_TOKENS['text_secondary'],
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            showline=False,
            zeroline=False,
            tickprefix='¥',
        ),
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ==================== 最近交易列表 ====================
def render_transaction_list(transactions: list, title: str = "最近交易"):
    """
    渲染交易列表
    
    参数:
        transactions: [
            {"title": "Salary", "tag": "Belong Interactive", "amount": 2010, "time": "Today 14:02", "icon": "wallet"},
            ...
        ]
    """
    st.markdown(f"""
    <div class="premium-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h3 style="margin: 0; font-size: 1.2rem; color: {DESIGN_TOKENS['text_primary']};">
                {icon('activity', 20, DESIGN_TOKENS['primary_solid'])}
                <span style="margin-left: 0.5rem;">{title}</span>
            </h3>
            <button style="background: transparent; border: none; color: {DESIGN_TOKENS['text_secondary']}; cursor: pointer;">
                {icon('more_horizontal', 20)}
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    for i, tx in enumerate(transactions):
        tx_icon = tx.get('icon', 'credit_card')
        amount = tx['amount']
        amount_color = DESIGN_TOKENS['success'] if amount > 0 else DESIGN_TOKENS['error']
        amount_sign = '+' if amount > 0 else ''
        
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 0.5rem;
            transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
            cursor: pointer;
        " onmouseover="this.style.background='{DESIGN_TOKENS['bg_card_hover']}'; this.style.transform='translateY(-2px)';" onmouseout="this.style.background='transparent'; this.style.transform='translateY(0)';">
            <div style="
                width: 48px;
                height: 48px;
                border-radius: 12px;
                background: {DESIGN_TOKENS['bg_elevated']};
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                {icon(tx_icon, 24, DESIGN_TOKENS['primary_solid'])}
            </div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: {DESIGN_TOKENS['text_primary']}; margin-bottom: 0.25rem;">
                    {tx['title']}
                </div>
                <div style="font-size: 0.85rem; color: {DESIGN_TOKENS['text_tertiary']};">
                    {tx.get('tag', '')}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 700; font-size: 1.1rem; color: {amount_color}; font-variant-numeric: tabular-nums;">
                    {amount_sign}¥{abs(amount):,.2f}
                </div>
                <div style="font-size: 0.8rem; color: {DESIGN_TOKENS['text_tertiary']};">
                    {tx['time']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== KPI统计卡 ====================
def render_kpi_card(label: str, value: str, change: str = None, icon_name: str = 'trending_up'):
    """
    渲染KPI统计卡
    
    参数:
        label: 标签
        value: 数值
        change: 变化（可选）
        icon_name: 图标名称
    """
    change_html = ""
    if change:
        change_class = "positive" if "+" in change else "negative" if "-" in change else "neutral"
        change_html = f'<div class="kpi-change {change_class}">{change}</div>'
    
    html = f"""
    <div class="kpi-card hover-float">
        <div style="margin-bottom: 1rem; opacity: 0.8;">
            {icon(icon_name, 32, DESIGN_TOKENS['primary_solid'])}
        </div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {change_html}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


# ==================== 环形进度图 ====================
def render_donut_chart(value: float, label: str, color: str = '#FF7A29'):
    """
    渲染环形进度图
    
    参数:
        value: 0-1之间的值
        label: 标签
        color: 颜色
    """
    percentage = int(value * 100)
    
    fig = go.Figure(data=[go.Pie(
        values=[value, 1-value],
        hole=0.7,
        marker=dict(colors=[color, 'rgba(255,255,255,0.1)']),
        textinfo='none',
        hoverinfo='skip',
    )])
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        annotations=[dict(
            text=f'<b>{percentage}%</b>',
            x=0.5, y=0.5,
            font=dict(size=24, color=DESIGN_TOKENS['text_primary']),
            showarrow=False,
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f"<div style='text-align: center; color: {DESIGN_TOKENS['text_secondary']}; font-size: 0.9rem; margin-top: -1rem;'>{label}</div>", unsafe_allow_html=True)


# ==================== 策略信号表格 ====================
def render_signal_table(signals: pd.DataFrame):
    """
    渲染策略信号表格
    
    参数:
        signals: DataFrame with columns ['资产', '信号', '价格', '时间']
    """
    st.markdown(f"""
    <div class="premium-card">
        <h3 style="margin: 0 0 1.5rem 0; font-size: 1.2rem;">
            {icon('target', 20, DESIGN_TOKENS['primary_solid'])}
            <span style="margin-left: 0.5rem;">策略信号</span>
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用Streamlit的dataframe展示
    st.dataframe(
        signals,
        use_container_width=True,
        hide_index=True,
        column_config={
            "信号": st.column_config.TextColumn(
                "信号",
                help="交易信号",
            ),
            "价格": st.column_config.NumberColumn(
                "价格",
                format="¥%.2f",
            ),
        }
    )


# ==================== Upcoming待办卡 ====================
def render_upcoming_card(upcoming: list):
    """
    渲染Upcoming待办卡
    
    参数:
        upcoming: [
            {"name": "Payment for Domain", "amount": 120},
            {"name": "Tour Plan", "amount": 2500}
        ]
    """
    st.markdown(f"""
    <div class="premium-card">
        <h3 style="margin: 0 0 1.5rem 0; font-size: 1.2rem;">
            {icon('calendar', 20, DESIGN_TOKENS['primary_solid'])}
            <span style="margin-left: 0.5rem;">即将到期</span>
        </h3>
    """, unsafe_allow_html=True)
    
    for item in upcoming:
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: {DESIGN_TOKENS['bg_elevated']};
            border-radius: 12px;
            margin-bottom: 0.75rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #FF6A00, #FFA54C);
                "></div>
                <span style="color: {DESIGN_TOKENS['text_primary']}; font-weight: 500;">
                    {item['name']}
                </span>
            </div>
            <div style="font-weight: 700; color: {DESIGN_TOKENS['text_primary']}; font-variant-numeric: tabular-nums;">
                ¥{item['amount']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== 时间段选择器 ====================
def render_time_period_selector():
    """渲染时间段选择器（Today/7D/1M/1Y）"""
    periods = [
        ('今天', 'today'),
        ('7天', '7d'),
        ('1月', '1m'),
        ('1年', '1y'),
    ]
    
    cols = st.columns(len(periods))
    selected = None
    
    for i, (label, value) in enumerate(periods):
        with cols[i]:
            if st.button(label, key=f"period_{value}", use_container_width=True):
                selected = value
    
    return selected or '7d'


# ==================== Toast通知 ====================
def show_toast(message: str, type: str = 'success'):
    """
    显示Toast通知
    
    参数:
        message: 消息内容
        type: success/warning/error/info
    """
    colors = {
        'success': DESIGN_TOKENS['success'],
        'warning': DESIGN_TOKENS['warning'],
        'error': DESIGN_TOKENS['error'],
        'info': DESIGN_TOKENS['info'],
    }
    
    icons_map = {
        'success': 'check_circle',
        'warning': 'alert_triangle',
        'error': 'alert_triangle',
        'info': 'info',
    }
    
    color = colors.get(type, colors['info'])
    icon_name = icons_map.get(type, 'info')
    
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: {DESIGN_TOKENS['bg_elevated']};
        border: 1px solid {DESIGN_TOKENS['border']};
        border-left: 4px solid {color};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: {DESIGN_TOKENS['shadow_elevated']};
        z-index: 9999;
        animation: slideInRight 0.3s cubic-bezier(0.22, 1, 0.36, 1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        {icon(icon_name, 20, color)}
        <span style="color: {DESIGN_TOKENS['text_primary']}; font-weight: 500;">{message}</span>
    </div>
    """, unsafe_allow_html=True)

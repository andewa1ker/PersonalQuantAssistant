"""
Google Finance 组件库 - 100%还原
包含卡片、按钮、标签等核心组件
"""
import streamlit as st
from design_system_google import GOOGLE_COLORS, SPACING, RADIUS, SHADOWS, TYPOGRAPHY


def gf_card(title: str = None, subtitle: str = None, show_menu: bool = False):
    """
    Google Finance 风格卡片
    
    参数:
        title: 卡片标题
        subtitle: 副标题（浅色）
        show_menu: 是否显示右上角菜单
    """
    html = f"""
    <div style="
        background: {GOOGLE_COLORS['bg_primary']};
        border: 1px solid {GOOGLE_COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: {SPACING['5']};
        margin: {SPACING['4']} 0;
        transition: box-shadow 150ms cubic-bezier(0.4, 0, 0.2, 1);
    ">
    """
    
    if title or show_menu:
        html += f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: {SPACING['2']};
        ">
        """
        
        if title:
            html += f"""
            <div>
                <h3 style="
                    font-size: {TYPOGRAPHY['size_xl']};
                    font-weight: {TYPOGRAPHY['weight_regular']};
                    color: {GOOGLE_COLORS['text_primary']};
                    margin: 0 0 {SPACING['1']} 0;
                ">{title}</h3>
            """
            if subtitle:
                html += f"""
                <div style="
                    font-size: {TYPOGRAPHY['size_sm']};
                    color: {GOOGLE_COLORS['text_secondary']};
                ">{subtitle}</div>
                """
            html += "</div>"
        
        if show_menu:
            html += f"""
            <button style="
                background: none;
                border: none;
                cursor: pointer;
                padding: {SPACING['2']};
                color: {GOOGLE_COLORS['text_secondary']};
                font-size: 20px;
            ">⋮</button>
            """
        
        html += "</div>"
    
    html += "</div>"
    
    st.markdown(html, unsafe_allow_html=True)


def gf_kpi_metric(label: str, value: str, change: str = None, change_type: str = None):
    """
    Google Finance KPI 指标卡片
    
    参数:
        label: 指标名称
        value: 指标值
        change: 变化值（如 +1.87%）
        change_type: 'up' 或 'down'
    """
    change_color = GOOGLE_COLORS['green'] if change_type == 'up' else GOOGLE_COLORS['red']
    change_bg = GOOGLE_COLORS['green_bg'] if change_type == 'up' else GOOGLE_COLORS['red_bg']
    
    html = f"""
    <div style="
        background: {GOOGLE_COLORS['bg_primary']};
        border: 1px solid {GOOGLE_COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: {SPACING['5']};
        text-align: left;
    ">
        <div style="
            font-size: {TYPOGRAPHY['size_sm']};
            color: {GOOGLE_COLORS['text_secondary']};
            margin-bottom: {SPACING['2']};
        ">{label}</div>
        
        <div style="
            font-size: {TYPOGRAPHY['size_3xl']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: {GOOGLE_COLORS['text_primary']};
            letter-spacing: -0.5px;
            margin-bottom: {SPACING['1']};
        ">{value}</div>
    """
    
    if change:
        html += f"""
        <div style="
            display: inline-block;
            background: {change_bg};
            color: {change_color};
            padding: {SPACING['1']} {SPACING['2']};
            border-radius: {RADIUS['sm']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_medium']};
        ">{change}</div>
        """
    
    html += "</div>"
    
    st.markdown(html, unsafe_allow_html=True)


def gf_badge(text: str, type: str = 'neutral'):
    """
    Google Finance 标签徽章
    
    参数:
        text: 标签文字
        type: 'up' (涨), 'down' (跌), 'status' (状态), 'neutral' (中性)
    """
    colors = {
        'up': {'bg': GOOGLE_COLORS['green_bg'], 'text': GOOGLE_COLORS['green_dark']},
        'down': {'bg': GOOGLE_COLORS['red_bg'], 'text': GOOGLE_COLORS['red_dark']},
        'status': {'bg': GOOGLE_COLORS['blue_bg'], 'text': GOOGLE_COLORS['blue']},
        'neutral': {'bg': GOOGLE_COLORS['bg_secondary'], 'text': GOOGLE_COLORS['text_secondary']},
    }
    
    color = colors.get(type, colors['neutral'])
    
    return f"""
    <span style="
        display: inline-block;
        background: {color['bg']};
        color: {color['text']};
        padding: {SPACING['1']} {SPACING['2']};
        border-radius: {RADIUS['sm']};
        font-size: {TYPOGRAPHY['size_sm']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        font-variant-numeric: tabular-nums;
    ">{text}</span>
    """


def gf_data_row(label: str, value: str, label_width: str = "50%"):
    """
    数据行（键值对显示）
    用于详细信息展示
    """
    return f"""
    <div style="
        display: flex;
        justify-content: space-between;
        padding: {SPACING['2']} 0;
        border-bottom: 1px solid {GOOGLE_COLORS['bg_secondary']};
    ">
        <span style="
            color: {GOOGLE_COLORS['text_secondary']};
            font-size: {TYPOGRAPHY['size_sm']};
            width: {label_width};
        ">{label}</span>
        <span style="
            color: {GOOGLE_COLORS['text_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            text-align: right;
        ">{value}</span>
    </div>
    """


def gf_section_header(title: str, icon: str = None):
    """
    区域标题头
    """
    html = f"""
    <div style="
        margin: {SPACING['8']} 0 {SPACING['4']} 0;
    ">
    """
    
    if icon:
        html += f'<span style="margin-right: {SPACING["2"]};">{icon}</span>'
    
    html += f"""
        <span style="
            font-size: {TYPOGRAPHY['size_xl']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: {GOOGLE_COLORS['text_primary']};
        ">{title}</span>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def gf_button_group(buttons: list, selected: int = 0):
    """
    按钮组（用于时间范围选择等）
    
    参数:
        buttons: 按钮文字列表 ['1D', '5D', '1M', ...]
        selected: 选中的索引
    
    返回:
        点击的按钮索引
    """
    cols = st.columns(len(buttons))
    
    for i, (col, btn_text) in enumerate(zip(cols, buttons)):
        with col:
            is_selected = (i == selected)
            bg = GOOGLE_COLORS['blue_bg'] if is_selected else 'transparent'
            color = GOOGLE_COLORS['blue'] if is_selected else GOOGLE_COLORS['text_secondary']
            
            if st.button(
                btn_text,
                key=f'btn_{i}_{btn_text}',
                use_container_width=True,
            ):
                return i
    
    return selected


def gf_empty_state(icon: str, title: str, description: str = None, action_text: str = None):
    """
    空状态提示
    """
    html = f"""
    <div style="
        text-align: center;
        padding: {SPACING['12']} {SPACING['6']};
    ">
        <div style="
            font-size: 48px;
            color: {GOOGLE_COLORS['border']};
            margin-bottom: {SPACING['4']};
        ">{icon}</div>
        
        <div style="
            font-size: {TYPOGRAPHY['size_md']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            color: {GOOGLE_COLORS['text_primary']};
            margin-bottom: {SPACING['2']};
        ">{title}</div>
    """
    
    if description:
        html += f"""
        <div style="
            font-size: {TYPOGRAPHY['size_base']};
            color: {GOOGLE_COLORS['text_secondary']};
            margin-bottom: {SPACING['4']};
        ">{description}</div>
        """
    
    html += "</div>"
    
    st.markdown(html, unsafe_allow_html=True)
    
    if action_text:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.button(action_text, type='primary', use_container_width=True)


def gf_table_style():
    """
    返回 DataFrame 的 Google Finance 样式配置
    """
    return {
        'text-align': 'left',
        'font-size': f'{TYPOGRAPHY["size_base"]}',
        'color': GOOGLE_COLORS['text_primary'],
    }


def gf_loading():
    """显示 Google 风格的加载状态"""
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        padding: {SPACING['12']} 0;
    ">
        <div style="
            border: 3px solid {GOOGLE_COLORS['bg_secondary']};
            border-top: 3px solid {GOOGLE_COLORS['blue']};
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        "></div>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

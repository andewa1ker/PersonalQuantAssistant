"""
Google Finance 设计系统 - 100%还原
严格遵循 GOOGLE_FINANCE_UI_SPEC.md 规范
"""
import streamlit as st

# ========== 精确配色系统 ==========
GOOGLE_COLORS = {
    # 背景色
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F1F3F4',
    'bg_hover': '#F8F9FA',
    'bg_divider': '#E8EAED',
    
    # 文字色
    'text_primary': '#202124',      # 87% opacity
    'text_secondary': '#5F6368',    # 60% opacity
    'text_disabled': '#80868B',     # 38% opacity
    
    # 功能色 - Google 蓝
    'blue': '#1A73E8',
    'blue_hover': '#1765CC',
    'blue_active': '#1557B0',
    'blue_bg': '#E8F0FE',
    
    # 涨跌色 - Google 绿/红
    'green': '#0F9D58',
    'green_dark': '#0D8043',
    'green_bg': '#E6F4EA',
    'red': '#D93025',
    'red_dark': '#B31412',
    'red_bg': '#FCE8E6',
    
    # 警告色 - Google 黄
    'yellow': '#F9AB00',
    'yellow_bg': '#FEF7E0',
    
    # 边框
    'border': '#DADCE0',
    'border_light': '#E8EAED',
    
    # 图表
    'chart_grid': '#F1F3F4',
    'chart_line': '#1A73E8',
    'chart_area': 'rgba(26,115,232,0.08)',
}

# ========== 间距系统 (4px 基准) ==========
SPACING = {
    '1': '4px',
    '2': '8px',
    '3': '12px',
    '4': '16px',
    '5': '20px',
    '6': '24px',
    '8': '32px',
    '10': '40px',
    '12': '48px',
}

# ========== 圆角系统 ==========
RADIUS = {
    'none': '0px',
    'sm': '4px',
    'md': '8px',
    'lg': '16px',
    'full': '9999px',
}

# ========== 阴影系统 ==========
SHADOWS = {
    'none': 'none',
    'sm': '0 1px 2px 0 rgba(60,64,67,0.3)',
    'md': '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
    'lg': '0 4px 6px rgba(60,64,67,0.15)',
}

# ========== 字体系统 ==========
TYPOGRAPHY = {
    'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Google Sans", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif',
    'family_mono': 'Roboto Mono, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace',
    
    # 字号
    'size_xs': '11px',
    'size_sm': '12px',
    'size_base': '14px',
    'size_md': '16px',
    'size_lg': '20px',
    'size_xl': '22px',
    'size_2xl': '28px',
    'size_3xl': '32px',
    
    # 字重
    'weight_regular': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
    
    # 行高
    'leading_tight': '1.2',
    'leading_normal': '1.5',
    'leading_relaxed': '1.75',
}

# ========== 动画系统 ==========
TRANSITIONS = {
    'duration_fast': '150ms',
    'duration_base': '200ms',
    'duration_slow': '300ms',
    'easing_standard': 'cubic-bezier(0.4, 0, 0.2, 1)',
    'easing_decelerate': 'cubic-bezier(0, 0, 0.2, 1)',
    'easing_accelerate': 'cubic-bezier(0.4, 0, 1, 1)',
}


def inject_google_css():
    """注入 Google Finance 风格的 CSS"""
    
    css = f"""
    <style>
    /* ========== 全局样式 ========== */
    * {{
        font-variant-numeric: tabular-nums;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    
    :root {{
        /* 颜色变量 */
        --gf-bg-primary: {GOOGLE_COLORS['bg_primary']};
        --gf-bg-secondary: {GOOGLE_COLORS['bg_secondary']};
        --gf-text-primary: {GOOGLE_COLORS['text_primary']};
        --gf-text-secondary: {GOOGLE_COLORS['text_secondary']};
        --gf-blue: {GOOGLE_COLORS['blue']};
        --gf-green: {GOOGLE_COLORS['green']};
        --gf-red: {GOOGLE_COLORS['red']};
        --gf-border: {GOOGLE_COLORS['border']};
    }}
    
    /* ========== Streamlit 覆盖 ========== */
    .stApp {{
        background: {GOOGLE_COLORS['bg_primary']};
        font-family: {TYPOGRAPHY['family']};
    }}
    
    .main {{
        background: {GOOGLE_COLORS['bg_primary']};
        padding: {SPACING['6']};
    }}
    
    .block-container {{
        max-width: 1440px;
        padding: {SPACING['6']} {SPACING['4']};
    }}
    
    /* ========== 侧边栏 ========== */
    [data-testid="stSidebar"] {{
        background: {GOOGLE_COLORS['bg_primary']};
        border-right: 1px solid {GOOGLE_COLORS['border_light']};
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding: {SPACING['6']} {SPACING['4']};
    }}
    
    /* ========== 标题样式 ========== */
    h1 {{
        font-size: {TYPOGRAPHY['size_2xl']};
        font-weight: {TYPOGRAPHY['weight_regular']};
        color: {GOOGLE_COLORS['text_primary']};
        margin: 0 0 {SPACING['2']} 0;
        line-height: {TYPOGRAPHY['leading_tight']};
    }}
    
    h2 {{
        font-size: {TYPOGRAPHY['size_xl']};
        font-weight: {TYPOGRAPHY['weight_regular']};
        color: {GOOGLE_COLORS['text_primary']};
        margin: {SPACING['6']} 0 {SPACING['3']} 0;
    }}
    
    h3 {{
        font-size: {TYPOGRAPHY['size_md']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        color: {GOOGLE_COLORS['text_primary']};
        margin: {SPACING['4']} 0 {SPACING['2']} 0;
    }}
    
    /* ========== 按钮系统 ========== */
    .stButton > button {{
        background: {GOOGLE_COLORS['blue']};
        color: #FFFFFF;
        border: none;
        border-radius: {RADIUS['sm']};
        padding: 10px 24px;
        font-size: {TYPOGRAPHY['size_base']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        transition: background {TRANSITIONS['duration_fast']} {TRANSITIONS['easing_standard']},
                    box-shadow {TRANSITIONS['duration_fast']} {TRANSITIONS['easing_standard']};
    }}
    
    .stButton > button:hover {{
        background: {GOOGLE_COLORS['blue_hover']};
        box-shadow: {SHADOWS['sm']};
    }}
    
    .stButton > button:active {{
        background: {GOOGLE_COLORS['blue_active']};
        transform: translateY(1px);
    }}
    
    /* ========== 输入框 ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {{
        background: {GOOGLE_COLORS['bg_primary']};
        border: 1px solid {GOOGLE_COLORS['border']};
        border-radius: {RADIUS['sm']};
        color: {GOOGLE_COLORS['text_primary']};
        font-size: {TYPOGRAPHY['size_base']};
        padding: 10px 12px;
        transition: border-color {TRANSITIONS['duration_fast']};
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {{
        border-color: {GOOGLE_COLORS['blue']};
        box-shadow: 0 0 0 2px {GOOGLE_COLORS['blue_bg']};
        outline: none;
    }}
    
    /* ========== 分割线 ========== */
    hr {{
        border: none;
        border-top: 1px solid {GOOGLE_COLORS['bg_divider']};
        margin: {SPACING['6']} 0;
    }}
    
    /* ========== Metric 卡片 ========== */
    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY['size_3xl']};
        font-weight: {TYPOGRAPHY['weight_regular']};
        color: {GOOGLE_COLORS['text_primary']};
        letter-spacing: -0.5px;
    }}
    
    [data-testid="stMetricDelta"] {{
        font-size: {TYPOGRAPHY['size_md']};
        font-weight: {TYPOGRAPHY['weight_regular']};
    }}
    
    /* ========== 表格样式 ========== */
    .dataframe {{
        border: none !important;
        font-size: {TYPOGRAPHY['size_base']};
    }}
    
    .dataframe thead tr th {{
        background: {GOOGLE_COLORS['bg_primary']} !important;
        color: {GOOGLE_COLORS['text_secondary']} !important;
        font-size: {TYPOGRAPHY['size_xs']} !important;
        font-weight: {TYPOGRAPHY['weight_medium']} !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-bottom: 1px solid {GOOGLE_COLORS['border_light']} !important;
        padding: 12px 16px !important;
    }}
    
    .dataframe tbody tr td {{
        border-bottom: 1px solid {GOOGLE_COLORS['bg_secondary']} !important;
        padding: 16px !important;
        color: {GOOGLE_COLORS['text_primary']};
    }}
    
    .dataframe tbody tr:hover {{
        background: {GOOGLE_COLORS['bg_secondary']} !important;
        cursor: pointer;
    }}
    
    /* ========== Expander ========== */
    .streamlit-expanderHeader {{
        background: {GOOGLE_COLORS['bg_primary']};
        border: 1px solid {GOOGLE_COLORS['border']};
        border-radius: {RADIUS['md']};
        color: {GOOGLE_COLORS['text_primary']};
        font-size: {TYPOGRAPHY['size_base']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}
    
    .streamlit-expanderHeader:hover {{
        background: {GOOGLE_COLORS['bg_hover']};
    }}
    
    /* ========== Tab 标签 ========== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: {SPACING['2']};
        border-bottom: 1px solid {GOOGLE_COLORS['border_light']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border: none;
        color: {GOOGLE_COLORS['text_secondary']};
        font-size: {TYPOGRAPHY['size_base']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        padding: 12px 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {GOOGLE_COLORS['blue_bg']};
        color: {GOOGLE_COLORS['blue']};
        border-radius: {RADIUS['sm']};
    }}
    
    /* ========== Slider ========== */
    .stSlider > div > div > div {{
        background: {GOOGLE_COLORS['blue']};
    }}
    
    /* ========== Radio / Checkbox ========== */
    .stRadio > label,
    .stCheckbox > label {{
        color: {GOOGLE_COLORS['text_primary']};
        font-size: {TYPOGRAPHY['size_base']};
    }}
    
    /* ========== 隐藏 Streamlit 默认元素 ========== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ========== 自定义滚动条 ========== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {GOOGLE_COLORS['bg_secondary']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {GOOGLE_COLORS['border']};
        border-radius: {RADIUS['sm']};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {GOOGLE_COLORS['text_disabled']};
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


# 导出常用组合
TOKENS = {**GOOGLE_COLORS, **SPACING, **RADIUS, **SHADOWS, **TYPOGRAPHY, **TRANSITIONS}

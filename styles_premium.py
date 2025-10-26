"""
全局样式系统 - Premium深色金融风格
包含Design Tokens、全局CSS、动画规范
"""
import streamlit as st


# ==================== Design Tokens ====================
DESIGN_TOKENS = {
    # 背景色
    'bg_primary': '#0B0B0F',
    'bg_secondary': '#14141A',
    'bg_card': '#1E1E26',
    'bg_card_hover': '#23232D',
    'bg_elevated': '#2B2B36',
    
    # 主高光（橙色渐变）
    'primary_start': '#FF6A00',
    'primary_end': '#FFA54C',
    'primary_solid': '#FF7A29',
    
    # 文本色
    'text_primary': '#FFFFFF',
    'text_secondary': 'rgba(255, 255, 255, 0.78)',
    'text_tertiary': 'rgba(255, 255, 255, 0.56)',
    'text_disabled': 'rgba(255, 255, 255, 0.38)',
    
    # 功能色
    'success': '#4CAF50',
    'success_bg': 'rgba(76, 175, 80, 0.12)',
    'error': '#EF5350',
    'error_bg': 'rgba(239, 83, 80, 0.12)',
    'warning': '#FFA726',
    'warning_bg': 'rgba(255, 167, 38, 0.12)',
    'info': '#42A5F5',
    'info_bg': 'rgba(66, 165, 245, 0.12)',
    
    # 边框与分割
    'border': 'rgba(255, 255, 255, 0.08)',
    'border_hover': 'rgba(255, 255, 255, 0.16)',
    'divider': 'rgba(255, 255, 255, 0.06)',
    
    # 阴影与发光
    'shadow_card': '0 8px 40px rgba(0, 0, 0, 0.45)',
    'shadow_elevated': '0 16px 60px rgba(0, 0, 0, 0.55)',
    'glow_primary': '0 0 24px rgba(255, 140, 64, 0.35)',
    'glow_strong': '0 0 40px rgba(255, 122, 41, 0.5)',
    
    # 圆角
    'radius_card': '18px',
    'radius_button': '12px',
    'radius_input': '12px',
    'radius_badge': '999px',
    'radius_small': '8px',
    
    # 间距
    'spacing_xs': '4px',
    'spacing_sm': '8px',
    'spacing_md': '16px',
    'spacing_lg': '24px',
    'spacing_xl': '32px',
    'spacing_2xl': '48px',
    
    # 字体
    'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "Microsoft YaHei", sans-serif',
    'font_family_mono': '"SF Mono", "Consolas", "Monaco", monospace',
}


def inject_premium_styles():
    """注入Premium深色金融样式"""
    
    css = f"""
    <style>
    /* ==================== 全局变量 ==================== */
    :root {{
        --bg-primary: {DESIGN_TOKENS['bg_primary']};
        --bg-secondary: {DESIGN_TOKENS['bg_secondary']};
        --bg-card: {DESIGN_TOKENS['bg_card']};
        --bg-card-hover: {DESIGN_TOKENS['bg_card_hover']};
        --bg-elevated: {DESIGN_TOKENS['bg_elevated']};
        
        --primary-start: {DESIGN_TOKENS['primary_start']};
        --primary-end: {DESIGN_TOKENS['primary_end']};
        --primary-solid: {DESIGN_TOKENS['primary_solid']};
        
        --text-primary: {DESIGN_TOKENS['text_primary']};
        --text-secondary: {DESIGN_TOKENS['text_secondary']};
        --text-tertiary: {DESIGN_TOKENS['text_tertiary']};
        
        --border: {DESIGN_TOKENS['border']};
        --border-hover: {DESIGN_TOKENS['border_hover']};
        
        --shadow-card: {DESIGN_TOKENS['shadow_card']};
        --glow-primary: {DESIGN_TOKENS['glow_primary']};
        
        --radius-card: {DESIGN_TOKENS['radius_card']};
        --radius-button: {DESIGN_TOKENS['radius_button']};
        --radius-badge: {DESIGN_TOKENS['radius_badge']};
        
        --transition-smooth: cubic-bezier(0.22, 1, 0.36, 1);
    }}
    
    /* ==================== 全局基础样式 ==================== */
    body {{
        font-family: {DESIGN_TOKENS['font_family']};
        background: linear-gradient(135deg, #0B0B0F 0%, #14141A 100%);
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
    }}
    
    /* Streamlit 容器调整 */
    .main {{
        background: transparent;
        padding: 2rem 3rem;
    }}
    
    .block-container {{
        max-width: 1400px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}
    
    /* ==================== 侧边栏样式 ==================== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #14141A 0%, #0B0B0F 100%);
        border-right: 1px solid var(--border);
    }}
    
    [data-testid="stSidebar"] .block-container {{
        padding: 2rem 1rem;
    }}
    
    /* 侧边栏导航项 */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        transition: all 0.2s var(--transition-smooth);
    }}
    
    /* 当前选中项橙色指示 */
    [data-testid="stSidebar"] .element-container:has(> div > div > p:first-child)::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 0;
        background: linear-gradient(180deg, var(--primary-start), var(--primary-end));
        border-radius: 0 4px 4px 0;
        transition: height 0.3s var(--transition-smooth);
    }}
    
    /* ==================== 卡片样式 ==================== */
    .premium-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        box-shadow: var(--shadow-card);
        transition: all 0.25s var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }}
    
    .premium-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 122, 41, 0.3), 
            transparent
        );
        opacity: 0;
        transition: opacity 0.3s var(--transition-smooth);
    }}
    
    .premium-card:hover {{
        background: var(--bg-card-hover);
        border-color: var(--border-hover);
        transform: translateY(-3px);
        box-shadow: var(--shadow-card), var(--glow-primary);
    }}
    
    .premium-card:hover::before {{
        opacity: 1;
    }}
    
    /* 玻璃质感卡片 */
    .glass-card {{
        background: rgba(30, 30, 38, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
    }}
    
    /* ==================== 按钮样式 ==================== */
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary-start), var(--primary-end));
        color: white;
        border: none;
        border-radius: var(--radius-button);
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.25s var(--transition-smooth);
        box-shadow: 0 4px 16px rgba(255, 106, 0, 0.3);
        cursor: pointer;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(255, 106, 0, 0.4), var(--glow-primary);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* 次要按钮 */
    .secondary-button {{
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none !important;
    }}
    
    .secondary-button:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
    }}
    
    /* ==================== 输入框样式 ==================== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {{
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-input);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        transition: all 0.2s var(--transition-smooth);
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary-solid);
        box-shadow: 0 0 0 2px rgba(255, 122, 41, 0.2);
        outline: none;
    }}
    
    /* ==================== 标签与徽章 ==================== */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.35rem 0.75rem;
        border-radius: var(--radius-badge);
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    
    .badge-success {{
        background: {DESIGN_TOKENS['success_bg']};
        color: {DESIGN_TOKENS['success']};
    }}
    
    .badge-error {{
        background: {DESIGN_TOKENS['error_bg']};
        color: {DESIGN_TOKENS['error']};
    }}
    
    .badge-warning {{
        background: {DESIGN_TOKENS['warning_bg']};
        color: {DESIGN_TOKENS['warning']};
    }}
    
    .badge-primary {{
        background: linear-gradient(135deg, var(--primary-start), var(--primary-end));
        color: white;
    }}
    
    /* ==================== 表格样式 ==================== */
    .dataframe {{
        background: var(--bg-card);
        border-radius: var(--radius-card);
        overflow: hidden;
        border: 1px solid var(--border);
    }}
    
    .dataframe thead tr {{
        background: var(--bg-elevated);
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .dataframe tbody tr {{
        border-bottom: 1px solid var(--border);
        transition: background 0.2s var(--transition-smooth);
    }}
    
    .dataframe tbody tr:hover {{
        background: var(--bg-card-hover);
        transform: translateY(-1px);
    }}
    
    .dataframe td, .dataframe th {{
        padding: 1rem;
        text-align: left;
    }}
    
    /* ==================== Metric卡片 ==================== */
    [data-testid="stMetric"] {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        transition: all 0.25s var(--transition-smooth);
    }}
    
    [data-testid="stMetric"]:hover {{
        background: var(--bg-card-hover);
        transform: translateY(-3px);
        box-shadow: var(--shadow-card);
    }}
    
    [data-testid="stMetric"] label {{
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }}
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        font-size: 0.9rem;
        font-weight: 600;
    }}
    
    /* ==================== Tab样式 ==================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background: transparent;
        border-bottom: 1px solid var(--border);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: var(--text-secondary);
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s var(--transition-smooth);
        position: relative;
    }}
    
    .stTabs [data-baseweb="tab"]::after {{
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-start), var(--primary-end));
        transform: scaleX(0);
        transition: transform 0.3s var(--transition-smooth);
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text-primary);
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: var(--primary-solid);
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after {{
        transform: scaleX(1);
    }}
    
    /* ==================== 动画定义 ==================== */
    @keyframes floatIn {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
        }}
        to {{
            opacity: 1;
        }}
    }}
    
    @keyframes pulseGlow {{
        0%, 100% {{
            box-shadow: 0 0 20px rgba(255, 122, 41, 0.3);
        }}
        50% {{
            box-shadow: 0 0 40px rgba(255, 122, 41, 0.6);
        }}
    }}
    
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes shimmer {{
        0% {{
            background-position: -1000px 0;
        }}
        100% {{
            background-position: 1000px 0;
        }}
    }}
    
    /* ==================== 动画类 ==================== */
    .fade-in {{
        animation: fadeIn 0.4s var(--transition-smooth);
    }}
    
    .float-in {{
        animation: floatIn 0.5s var(--transition-smooth);
    }}
    
    .slide-in-right {{
        animation: slideInRight 0.4s var(--transition-smooth);
    }}
    
    .glow {{
        animation: pulseGlow 2s ease-in-out infinite;
    }}
    
    .hover-float:hover {{
        transform: translateY(-3px);
        transition: transform 0.25s var(--transition-smooth);
    }}
    
    /* ==================== 数字动画 ==================== */
    .animated-number {{
        font-variant-numeric: tabular-nums;
        transition: all 0.8s var(--transition-smooth);
    }}
    
    /* ==================== 加载骨架屏 ==================== */
    .skeleton {{
        background: linear-gradient(
            90deg,
            var(--bg-card) 0%,
            var(--bg-card-hover) 50%,
            var(--bg-card) 100%
        );
        background-size: 1000px 100%;
        animation: shimmer 2s infinite linear;
        border-radius: var(--radius-button);
    }}
    
    /* ==================== 响应式 ==================== */
    @media (max-width: 768px) {{
        .block-container {{
            padding: 1rem;
        }}
        
        .main {{
            padding: 1rem;
        }}
        
        .premium-card {{
            padding: 1rem;
        }}
    }}
    
    /* ==================== Tooltip样式 ==================== */
    [data-testid="stTooltipHoverTarget"] {{
        cursor: help;
    }}
    
    /* ==================== 滚动条样式 ==================== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--bg-elevated);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary-solid);
    }}
    
    /* ==================== 焦点可访问性 ==================== */
    *:focus-visible {{
        outline: 2px solid var(--primary-solid);
        outline-offset: 2px;
    }}
    
    /* ==================== Plotly图表深色主题 ==================== */
    .js-plotly-plot {{
        background: transparent !important;
    }}
    
    .plotly {{
        background: transparent !important;
    }}
    
    /* ==================== 隐藏Streamlit默认元素 ==================== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ==================== 自定义组件类 ==================== */
    .kpi-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.25s var(--transition-smooth);
    }}
    
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-card);
    }}
    
    .kpi-label {{
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-value {{
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        line-height: 1.2;
    }}
    
    .kpi-change {{
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }}
    
    .positive {{
        color: {DESIGN_TOKENS['success']};
    }}
    
    .negative {{
        color: {DESIGN_TOKENS['error']};
    }}
    
    .neutral {{
        color: var(--text-secondary);
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_gradient_text(text: str, gradient: str = "linear-gradient(135deg, #FF6A00, #FFA54C)") -> str:
    """创建渐变文字效果"""
    return f"""
    <span style="
        background: {gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    ">{text}</span>
    """


def create_divider(height: str = "1px", gradient: bool = True):
    """创建分割线"""
    if gradient:
        bg = "linear-gradient(90deg, transparent, rgba(255, 122, 41, 0.3), transparent)"
    else:
        bg = DESIGN_TOKENS['divider']
    
    st.markdown(f'<div style="height: {height}; background: {bg}; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

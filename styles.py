"""
Premium Finance UI - 全局样式系统
====================================
深色金融风格 + 橙色高光 + 玻璃质感 + 平滑动效
"""


def get_global_styles() -> str:
    """
    返回完整的全局 CSS 样式
    通过 st.markdown(get_global_styles(), unsafe_allow_html=True) 注入
    """
    return """
    <style>
    /* ========================================
       Design Tokens - 设计令牌
       ======================================== */
    :root {
        /* 背景色 */
        --bg-primary: #0B0B0F;
        --bg-secondary: #14141A;
        --bg-card: #1E1E26;
        --bg-card-hover: #23232D;
        --bg-elevated: #2B2B36;
        
        /* 主色调 - 琥珀橙渐变 */
        --primary-orange: #FF6A00;
        --primary-orange-light: #FFA54C;
        --primary-orange-rgb: 255, 106, 0;
        
        /* 文本颜色 */
        --text-primary: #FFFFFF;
        --text-secondary: rgba(255, 255, 255, 0.78);
        --text-tertiary: rgba(255, 255, 255, 0.56);
        --text-disabled: rgba(255, 255, 255, 0.38);
        
        /* 边框与分割线 */
        --border-color: rgba(255, 255, 255, 0.08);
        --divider-color: rgba(255, 255, 255, 0.06);
        
        /* 阴影 */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.35);
        --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.45);
        --shadow-glow: 0 0 24px rgba(255, 140, 64, 0.35);
        
        /* 圆角 */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 18px;
        --radius-xl: 24px;
        --radius-full: 999px;
        
        /* 间距 */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        
        /* 过渡动画 */
        --transition-fast: 150ms cubic-bezier(0.22, 1, 0.36, 1);
        --transition-base: 200ms cubic-bezier(0.22, 1, 0.36, 1);
        --transition-slow: 300ms cubic-bezier(0.22, 1, 0.36, 1);
        
        /* Z-index 层级 */
        --z-dropdown: 1000;
        --z-sticky: 1020;
        --z-fixed: 1030;
        --z-modal: 1040;
        --z-tooltip: 1050;
    }
    
    /* ========================================
       全局基础样式
       ======================================== */
    
    /* 页面背景渐变 */
    .stApp {
        background: radial-gradient(ellipse at top right, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        font-variant-numeric: tabular-nums;
    }
    
    /* 移除默认的 Streamlit 边距 */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        max-width: 1600px !important;
    }
    
    /* 隐藏 Streamlit 水印 */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* ========================================
       侧边栏样式
       ======================================== */
    
    /* 侧边栏容器 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-primary) 100%);
        border-right: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* 侧边栏导航项 */
    [data-testid="stSidebar"] .element-container {
        transition: all var(--transition-base);
    }
    
    /* 侧边栏按钮 */
    [data-testid="stSidebar"] button {
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-secondary) !important;
        transition: all var(--transition-base) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--primary-orange) !important;
        color: var(--primary-orange) !important;
        transform: translateX(4px);
        box-shadow: var(--shadow-sm);
    }
    
    /* ========================================
       卡片与容器
       ======================================== */
    
    /* 通用卡片样式 */
    .card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 255, 255, 0.1) 50%, 
            transparent 100%
        );
    }
    
    .card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(var(--primary-orange-rgb), 0.3);
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }
    
    /* 玻璃质感卡片 */
    .glass-card {
        background: rgba(30, 30, 38, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-lg);
    }
    
    /* 渐变卡片 */
    .gradient-card {
        background: linear-gradient(135deg, 
            var(--bg-card) 0%, 
            var(--bg-elevated) 100%
        );
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
    }
    
    /* ========================================
       按钮样式
       ======================================== */
    
    /* 主按钮 - 橙色渐变 */
    .stButton > button[kind="primary"],
    .primary-button {
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--primary-orange-light) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--transition-base) !important;
        cursor: pointer;
    }
    
    .stButton > button[kind="primary"]:hover,
    .primary-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
    }
    
    .stButton > button[kind="primary"]:active,
    .primary-button:active {
        transform: translateY(0) !important;
    }
    
    /* 次要按钮 */
    .stButton > button[kind="secondary"],
    .secondary-button {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all var(--transition-base) !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .secondary-button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--primary-orange) !important;
        color: var(--primary-orange) !important;
    }
    
    /* 图标按钮 */
    .icon-button {
        background: transparent;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        width: 40px;
        height: 40px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all var(--transition-base);
        color: var(--text-secondary);
    }
    
    .icon-button:hover {
        background: var(--bg-card-hover);
        border-color: var(--primary-orange);
        color: var(--primary-orange);
        transform: translateY(-2px);
    }
    
    /* ========================================
       徽章与标签
       ======================================== */
    
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: var(--radius-full);
        font-size: 13px;
        font-weight: 600;
        line-height: 1;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
    }
    
    .badge-orange {
        background: rgba(var(--primary-orange-rgb), 0.15);
        color: var(--primary-orange);
    }
    
    .badge-neutral {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-secondary);
    }
    
    /* ========================================
       输入框与表单
       ======================================== */
    
    /* 文本输入框 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
        transition: all var(--transition-base) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-orange) !important;
        box-shadow: 0 0 0 3px rgba(var(--primary-orange-rgb), 0.15) !important;
        outline: none !important;
    }
    
    /* 下拉选择框 */
    .stSelectbox > div > div > div {
        background: var(--bg-card) !important;
    }
    
    /* 日期选择器 */
    .stDateInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    
    /* ========================================
       标签页 (Tabs)
       ======================================== */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        padding: 12px 24px;
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        font-weight: 500;
        transition: all var(--transition-base);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card);
        color: var(--text-primary);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--bg-card);
        color: var(--primary-orange);
        border-bottom: 2px solid var(--primary-orange);
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: var(--spacing-lg);
    }
    
    /* ========================================
       表格样式
       ======================================== */
    
    /* DataFrame 表格 */
    .dataframe {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-bottom: 2px solid var(--border-color) !important;
        text-align: left !important;
    }
    
    .dataframe tbody tr {
        transition: all var(--transition-fast);
    }
    
    .dataframe tbody tr:hover {
        background: var(--bg-card-hover) !important;
        transform: translateY(-1px);
    }
    
    .dataframe tbody tr td {
        padding: 12px 16px !important;
        border-bottom: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
    }
    
    /* 正负数颜色 */
    .positive-value {
        color: var(--primary-orange) !important;
        font-weight: 600;
    }
    
    .negative-value {
        color: #6B7280 !important;
        font-weight: 600;
    }
    
    /* ========================================
       指标卡片 (Metrics)
       ======================================== */
    
    .stMetric {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        transition: all var(--transition-base);
    }
    
    .stMetric:hover {
        background: var(--bg-card-hover);
        border-color: rgba(var(--primary-orange-rgb), 0.3);
        transform: translateY(-2px);
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        font-variant-numeric: tabular-nums;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* ========================================
       图表样式
       ======================================== */
    
    /* Plotly 图表容器 */
    .js-plotly-plot {
        border-radius: var(--radius-lg);
        overflow: hidden;
    }
    
    /* ========================================
       进度条
       ======================================== */
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-orange) 0%, var(--primary-orange-light) 100%);
        border-radius: var(--radius-full);
    }
    
    .stProgress > div > div {
        background: var(--bg-elevated);
        border-radius: var(--radius-full);
    }
    
    /* ========================================
       滑块
       ======================================== */
    
    .stSlider > div > div > div > div {
        background: var(--primary-orange) !important;
    }
    
    /* ========================================
       复选框与单选框
       ======================================== */
    
    .stCheckbox > label > div[data-testid="stWidgetLabel"] {
        color: var(--text-secondary);
    }
    
    /* ========================================
       提示信息 (Alert)
       ======================================== */
    
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
    }
    
    /* ========================================
       加载动画
       ======================================== */
    
    .stSpinner > div {
        border-top-color: var(--primary-orange) !important;
    }
    
    /* ========================================
       自定义动画
       ======================================== */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes floatIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(var(--primary-orange-rgb), 0.3);
        }
        50% {
            box-shadow: 0 0 30px rgba(var(--primary-orange-rgb), 0.5);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    /* 动画类 */
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    .float-in {
        animation: floatIn 0.4s ease-out;
    }
    
    .hover-float:hover {
        transform: translateY(-3px);
        transition: transform var(--transition-base);
    }
    
    .glow {
        animation: pulseGlow 2s ease-in-out infinite;
    }
    
    /* ========================================
       响应式设计
       ======================================== */
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .card {
            padding: var(--spacing-md);
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
    
    /* ========================================
       辅助类
       ======================================== */
    
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .text-left { text-align: left; }
    
    .font-weight-normal { font-weight: 400; }
    .font-weight-medium { font-weight: 500; }
    .font-weight-semibold { font-weight: 600; }
    .font-weight-bold { font-weight: 700; }
    
    .text-primary { color: var(--text-primary); }
    .text-secondary { color: var(--text-secondary); }
    .text-tertiary { color: var(--text-tertiary); }
    .text-orange { color: var(--primary-orange); }
    
    .mb-1 { margin-bottom: var(--spacing-xs); }
    .mb-2 { margin-bottom: var(--spacing-sm); }
    .mb-3 { margin-bottom: var(--spacing-md); }
    .mb-4 { margin-bottom: var(--spacing-lg); }
    
    .mt-1 { margin-top: var(--spacing-xs); }
    .mt-2 { margin-top: var(--spacing-sm); }
    .mt-3 { margin-top: var(--spacing-md); }
    .mt-4 { margin-top: var(--spacing-lg); }
    
    /* ========================================
       自定义滚动条
       ======================================== */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-elevated);
        border-radius: var(--radius-full);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(var(--primary-orange-rgb), 0.5);
    }
    
    /* ========================================
       焦点可访问性
       ======================================== */
    
    *:focus-visible {
        outline: 2px solid var(--primary-orange) !important;
        outline-offset: 2px;
    }
    
    </style>
    """


def inject_styles():
    """便捷函数：注入全局样式"""
    import streamlit as st
    st.markdown(get_global_styles(), unsafe_allow_html=True)

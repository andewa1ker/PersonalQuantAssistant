"""
现代化UI主题系统
Apple风格设计：简洁、优雅、流畅
"""
import streamlit as st
import streamlit.components.v1 as components


class ModernTheme:
    """现代化主题配置"""
    
    # 颜色系统 - Apple官网级别
    COLORS = {
        # 主色调
        'primary': '#0071E3',  # Apple智能蓝
        'secondary': '#5856D6',  # Apple紫
        'success': '#30D158',  # Apple信赖绿
        'warning': '#FF9F0A',  # Apple警示橙
        'danger': '#FF3B30',  # Apple风险红
        'info': '#64D2FF',  # Apple信息青
        
        # 中性色 - 纯粹的黑白灰系统
        'background': '#000000',  # 纯黑背景
        'surface': '#1D1D1F',  # 表面灰（更接近Apple官网）
        'card': 'rgba(255, 255, 255, 0.05)',  # 半透明卡片
        'card_hover': 'rgba(255, 255, 255, 0.08)',  # 悬停状态
        'border': 'rgba(255, 255, 255, 0.15)',  # 精细边框
        
        # 文字颜色 - Apple的层次系统
        'text_primary': '#F5F5F7',  # 主文字（高级灰白）
        'text_secondary': '#86868B',  # 次文字（Apple中灰）
        'text_tertiary': '#6E6E73',  # 三级文字
        
        # 渐变色
        'gradient_start': '#0071E3',
        'gradient_end': '#00C7BE',  # 更柔和的渐变
        
        # 涨跌颜色
        'up': '#30D158',
        'down': '#FF453A',
        
        # 玻璃态
        'glass_bg': 'rgba(255, 255, 255, 0.72)',  # 白色玻璃
        'glass_dark': 'rgba(0, 0, 0, 0.8)',  # 黑色玻璃
    }
    
    # 字体系统 - SF Pro Display优先
    FONTS = {
        'primary': '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif',
        'mono': '"SF Mono", "Monaco", "Cascadia Code", "Consolas", "Courier New", monospace',
        'display': '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
    }
    
    # 尺寸系统 - Apple的完美比例
    SIZES = {
        'border_radius': '18px',  # 大圆角
        'border_radius_sm': '12px',  # 中圆角
        'border_radius_lg': '24px',  # 超大圆角
        'border_radius_full': '980px',  # 完全圆角（按钮）
        'spacing_xs': '8px',
        'spacing_sm': '16px',
        'spacing_md': '24px',
        'spacing_lg': '32px',
        'spacing_xl': '48px',
        'spacing_xxl': '64px',
    }
    
    # 阴影系统 - 精致的层次
    SHADOWS = {
        'xs': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
        'sm': '0 3px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12)',
        'md': '0 10px 20px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.10)',
        'lg': '0 15px 25px rgba(0, 0, 0, 0.15), 0 5px 10px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 40px rgba(0, 0, 0, 0.2)',
        'glow': '0 0 20px rgba(0, 113, 227, 0.4)',
        'glow_success': '0 0 20px rgba(48, 209, 88, 0.4)',
        'inner': 'inset 0 0 0 0.5px rgba(255, 255, 255, 0.1)',
    }
    
    # 动画时长 - Apple的精准timing
    TRANSITIONS = {
        'instant': '0.1s',
        'fast': '0.2s',
        'normal': '0.3s',
        'slow': '0.4s',
        'slower': '0.6s',
    }
    
    # 缓动函数 - Apple的自然曲线
    EASINGS = {
        'ease_out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'ease_in': 'cubic-bezier(0.4, 0, 1, 1)',
        'ease_in_out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',  # 弹性效果
        'smooth': 'cubic-bezier(0.23, 1, 0.32, 1)',  # 平滑过渡
    }
    
    @staticmethod
    def get_custom_css():
        """获取Apple级别的自定义CSS样式"""
        return f"""
        <style>
        /* ===== CSS变量系统 ===== */
        :root {{
            --primary: {ModernTheme.COLORS['primary']};
            --secondary: {ModernTheme.COLORS['secondary']};
            --success: {ModernTheme.COLORS['success']};
            --warning: {ModernTheme.COLORS['warning']};
            --danger: {ModernTheme.COLORS['danger']};
            --info: {ModernTheme.COLORS['info']};
            
            --background: {ModernTheme.COLORS['background']};
            --surface: {ModernTheme.COLORS['surface']};
            --card: {ModernTheme.COLORS['card']};
            --card-hover: {ModernTheme.COLORS['card_hover']};
            --border: {ModernTheme.COLORS['border']};
            
            --text-primary: {ModernTheme.COLORS['text_primary']};
            --text-secondary: {ModernTheme.COLORS['text_secondary']};
            --text-tertiary: {ModernTheme.COLORS['text_tertiary']};
            
            --shadow-sm: {ModernTheme.SHADOWS['sm']};
            --shadow-md: {ModernTheme.SHADOWS['md']};
            --shadow-lg: {ModernTheme.SHADOWS['lg']};
            
            --ease-out: {ModernTheme.EASINGS['ease_out']};
            --ease-spring: {ModernTheme.EASINGS['spring']};
            --ease-smooth: {ModernTheme.EASINGS['smooth']};
        }}
        
        /* ===== 全局重置与基础样式 ===== */
        * {{
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }}
        
        .stApp {{
            background: linear-gradient(180deg, #000000 0%, #0A0A0A 50%, #000000 100%);
            font-family: {ModernTheme.FONTS['primary']};
            color: var(--text-primary);
            overflow-x: hidden;
        }}
        
        /* ===== Apple玻璃态导航栏 ===== */
        [data-testid="stSidebar"] {{
            background: var(--glass-dark);
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
            border-right: 0.5px solid var(--border);
            transition: all {ModernTheme.TRANSITIONS['normal']} var(--ease-smooth);
        }}
        
        /* 导航项 - Apple风格 */
        [data-testid="stSidebar"] .stRadio > label {{
            color: var(--text-primary);
            font-size: 15px;
            font-weight: 500;
            letter-spacing: -0.022em;
            padding: 12px 16px;
            border-radius: {ModernTheme.SIZES['border_radius_sm']};
            transition: all {ModernTheme.TRANSITIONS['fast']} var(--ease-out);
            margin: 4px 0;
            display: block;
            cursor: pointer;
        }}
        
        [data-testid="stSidebar"] .stRadio > label:hover {{
            background: var(--card-hover);
            transform: translateX(4px);
        }}
        
        [data-testid="stSidebar"] .stRadio > label:active {{
            transform: translateX(2px) scale(0.98);
        }}
        
        /* ===== Apple风格卡片 ===== */
        .modern-card {{
            background: var(--card);
            border-radius: {ModernTheme.SIZES['border_radius']};
            padding: {ModernTheme.SIZES['spacing_md']};
            border: 0.5px solid var(--border);
            box-shadow: 
                var(--shadow-md),
                {ModernTheme.SHADOWS['inner']};
            backdrop-filter: blur(40px) saturate(180%);
            -webkit-backdrop-filter: blur(40px) saturate(180%);
            transition: all {ModernTheme.TRANSITIONS['slow']} var(--ease-smooth);
            position: relative;
            overflow: hidden;
            transform-style: preserve-3d;
            will-change: transform;
        }}
        
        .modern-card::before {{
            content: '';
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: radial-gradient(
                600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                rgba(0, 113, 227, 0.08),
                transparent 40%
            );
            opacity: 0;
            transition: opacity {ModernTheme.TRANSITIONS['normal']};
            pointer-events: none;
        }}
        
        .modern-card:hover {{
            transform: perspective(1000px) translateY(-8px) scale(1.02);
            box-shadow: 
                var(--shadow-lg),
                0 0 40px rgba(0, 113, 227, 0.15),
                {ModernTheme.SHADOWS['inner']};
            border-color: rgba(0, 113, 227, 0.3);
        }}
        
        .modern-card:hover::before {{
            opacity: 1;
        }}
        
        /* ===== 玻璃态卡片 ===== */
        .glass-card {{
            background: rgba(29, 29, 31, 0.7);
            backdrop-filter: blur(40px) saturate(180%);
            -webkit-backdrop-filter: blur(40px) saturate(180%);
            border: 0.5px solid rgba(255, 255, 255, 0.18);
            border-radius: {ModernTheme.SIZES['border_radius_lg']};
            padding: {ModernTheme.SIZES['spacing_lg']};
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 0 0 0.5px rgba(255, 255, 255, 0.1);
            transition: all {ModernTheme.TRANSITIONS['slow']} var(--ease-smooth);
        }}
        
        .glass-card:hover {{
            border-color: rgba(255, 255, 255, 0.25);
            box-shadow: 
                0 12px 48px rgba(0, 0, 0, 0.5),
                inset 0 0 0 0.5px rgba(255, 255, 255, 0.15);
        }}
        
        /* ===== 渐变标题 - 改进版 ===== */
        .gradient-title {{
            background: linear-gradient(
                135deg,
                {ModernTheme.COLORS['gradient_start']} 0%,
                {ModernTheme.COLORS['gradient_end']} 100%
            );
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 64px;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin-bottom: {ModernTheme.SIZES['spacing_md']};
            animation: gradientShift 6s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        /* ===== 数字显示 - SF Mono风格 ===== */
        .stat-number {{
            font-size: 56px;
            font-weight: 700;
            font-family: {ModernTheme.FONTS['mono']};
            letter-spacing: -0.04em;
            color: var(--text-primary);
            line-height: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
            font-variant-numeric: tabular-nums;
        }}
        
        .stat-label {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 8px;
        }}
        
        /* ===== Apple风格按钮 ===== */
        .stButton > button {{
            background: var(--primary);
            color: white;
            border: none;
            border-radius: {ModernTheme.SIZES['border_radius_full']};
            padding: 14px 28px;
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.022em;
            transition: all {ModernTheme.TRANSITIONS['normal']} var(--ease-out);
            box-shadow: 
                0 4px 14px rgba(0, 113, 227, 0.4),
                inset 0 -2px 0 rgba(0, 0, 0, 0.1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button::after {{
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            opacity: 0;
            transform: scale(0);
            transition: all {ModernTheme.TRANSITIONS['slow']} ease-out;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 
                0 8px 24px rgba(0, 113, 227, 0.5),
                inset 0 -2px 0 rgba(0, 0, 0, 0.15);
            background: #0077ED;
        }}
        
        .stButton > button:active {{
            transform: translateY(0) scale(0.98);
            box-shadow: 
                0 2px 8px rgba(0, 113, 227, 0.3),
                inset 0 2px 0 rgba(0, 0, 0, 0.1);
        }}
        
        .stButton > button:active::after {{
            opacity: 1;
            transform: scale(1.5);
            transition-duration: 0s;
        }}
        
        /* ===== Metric组件优化 ===== */
        [data-testid="stMetricValue"] {{
            font-size: 36px;
            font-weight: 700;
            font-family: {ModernTheme.FONTS['mono']};
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
        }}
        
        [data-testid="stMetricDelta"] {{
            font-size: 14px;
            font-weight: 600;
            font-family: {ModernTheme.FONTS['mono']};
        }}
        
        /* ===== 图表容器 ===== */
        .stPlotlyChart {{
            background: var(--card);
            border-radius: {ModernTheme.SIZES['border_radius']};
            padding: {ModernTheme.SIZES['spacing_md']};
            border: 0.5px solid var(--border);
            backdrop-filter: blur(40px);
        }}
        
        /* ===== 动画定义 ===== */
        
        /* 淡入 */
        .fade-in {{
            animation: fadeIn 0.6s var(--ease-out) forwards;
        }}
        
        @keyframes fadeIn {{
            from {{ 
                opacity: 0; 
                transform: translateY(30px); 
            }}
            to {{ 
                opacity: 1; 
                transform: translateY(0); 
            }}
        }}
        
        /* 滑入 */
        .slide-in {{
            animation: slideIn 0.5s var(--ease-smooth) forwards;
        }}
        
        @keyframes slideIn {{
            from {{ 
                transform: translateX(-100px); 
                opacity: 0; 
            }}
            to {{ 
                transform: translateX(0); 
                opacity: 1; 
            }}
        }}
        
        /* 脉搏 */
        .pulse {{
            animation: pulse 2s var(--ease-smooth) infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        /* 发光 */
        .glow {{
            animation: glow 2s ease-in-out infinite;
        }}
        
        @keyframes glow {{
            0%, 100% {{ 
                box-shadow: 0 0 20px rgba(0, 113, 227, 0.5),
                            0 0 40px rgba(0, 113, 227, 0.3);
            }}
            50% {{ 
                box-shadow: 0 0 40px rgba(0, 113, 227, 0.8),
                            0 0 60px rgba(0, 113, 227, 0.5);
            }}
        }}
        
        /* ===== 滚动条 - 精致化 ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            transition: background {ModernTheme.TRANSITIONS['fast']};
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        /* ===== 隐藏Streamlit默认元素 ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* ===== 响应式设计 ===== */
        @media (max-width: 1068px) {{
            .gradient-title {{
                font-size: 48px;
            }}
            
            .stat-number {{
                font-size: 42px;
            }}
        }}
        
        @media (max-width: 734px) {{
            .gradient-title {{
                font-size: 36px;
            }}
            
            .stat-number {{
                font-size: 32px;
            }}
            
            .modern-card {{
                padding: {ModernTheme.SIZES['spacing_sm']};
            }}
            
            /* 移动端禁用3D效果 */
            .modern-card:hover {{
                transform: translateY(-4px) scale(1.01) !important;
            }}
        }}
        </style>
        """
    
    @staticmethod
    def apply_theme():
        """应用主题到Streamlit应用，包含Apple动画系统"""
        # 应用CSS样式
        st.markdown(ModernTheme.get_custom_css(), unsafe_allow_html=True)
        
        # 加载Apple动画JS库
        ModernTheme.load_apple_animations()
    
    @staticmethod
    def load_apple_animations():
        """加载Apple级别动画JS库"""
        import os
        
        # 读取JS文件
        js_path = os.path.join(os.path.dirname(__file__), 'apple_animations.js')
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_code = f.read()
            
            # 注入JS到页面
            st.markdown(f"""
            <script>
            {js_code}
            </script>
            """, unsafe_allow_html=True)
        except FileNotFoundError:
            pass  # 如果文件不存在，静默失败
    
    @staticmethod
    def create_hero_section(title: str, subtitle: str = None):
        """
        创建Apple级别Hero区域 - 带逐字符显示动画
        """
        import random
        import streamlit.components.v1 as components
        
        hero_id = f"hero-title-{random.randint(1000, 9999)}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        .hero-section {{
            text-align: center; 
            padding: {ModernTheme.SIZES['spacing_xxl']} 0 {ModernTheme.SIZES['spacing_xl']} 0;
            position: relative;
            overflow: hidden;
        }}
        
        .gradient-title {{
            background: linear-gradient(
                135deg,
                {ModernTheme.COLORS['gradient_start']} 0%,
                {ModernTheme.COLORS['gradient_end']} 100%
            );
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 72px;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.1;
            margin-bottom: 24px;
            position: relative;
            z-index: 1;
            animation: gradientShift 6s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        @keyframes pulseGlow {{
            0%, 100% {{ 
                opacity: 0.5; 
                transform: translateX(-50%) scale(1); 
            }}
            50% {{ 
                opacity: 0.8; 
                transform: translateX(-50%) scale(1.1); 
            }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        </style>
        </head>
        <body style="margin: 0; background: transparent;">
        <div class="hero-section">
            <div style="
                position: absolute;
                top: -50%;
                left: 50%;
                transform: translateX(-50%);
                width: 150%;
                height: 200%;
                background: radial-gradient(ellipse at center, rgba(0, 113, 227, 0.15), transparent 60%);
                pointer-events: none;
                animation: pulseGlow 8s ease-in-out infinite;
            "></div>
            
            <h1 id="{hero_id}" class="gradient-title hero-title">{title}</h1>
        """
        
        if subtitle:
            html += f"""
            <p style="
                font-size: 21px; 
                font-weight: 400;
                color: #86868B; 
                max-width: 640px; 
                margin: 0 auto;
                line-height: 1.5;
                letter-spacing: -0.01em;
                position: relative;
                z-index: 1;
                animation: fadeIn 1s cubic-bezier(0.23, 1, 0.32, 1) 0.3s forwards;
                opacity: 0;
            ">{subtitle}</p>
            """
        
        html += """
        </div>
        </body>
        </html>
        """
        
        # 使用components.html替代st.markdown
        components.html(html, height=250)
    
    @staticmethod
    def create_stat_card(label: str, value: str, change: str = None, change_positive: bool = True):
        """创建统计卡片"""
        change_color = 'up' if change_positive else 'down'
        change_symbol = '▲' if change_positive else '▼'
        
        html = f"""
        <div class="modern-card fade-in">
            <div class="stat-label">{label}</div>
            <div class="stat-number">{value}</div>
        """
        
        if change:
            html += f"""
            <div style="margin-top: 12px; font-size: 16px; font-weight: 600;" class="{change_color}-color">
                {change_symbol} {change}
            </div>
            """
        
        html += "</div>"
        components.html(html, height=150, scrolling=False)
    
    @staticmethod
    def create_glass_card(content: str):
        """创建玻璃态卡片"""
        html = f"""
        <div class="glass-card slide-in">
            {content}
        </div>
        """
        components.html(html, height=200, scrolling=False)
    
    @staticmethod
    def create_divider():
        """创建分隔线"""
        st.markdown(
            f"""
            <div style="height: 1px; background: linear-gradient(90deg, 
                transparent, var(--border), transparent); 
                margin: {ModernTheme.SIZES['spacing_lg']} 0;">
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def create_badge(text: str, color: str = 'primary'):
        """创建徽章"""
        return f"""
        <span style="background: var(--{color}); color: white; 
            padding: 4px 12px; border-radius: 16px; font-size: 12px; 
            font-weight: 600; display: inline-block;">
            {text}
        </span>
        """
    
    @staticmethod
    def create_progress_ring(percentage: float, label: str):
        """创建进度环"""
        # SVG进度环
        radius = 40
        circumference = 2 * 3.14159 * radius
        offset = circumference - (percentage / 100) * circumference
        
        html = f"""
        <div style="text-align: center;">
            <svg width="120" height="120" class="pulse">
                <circle cx="60" cy="60" r="{radius}" 
                    stroke="var(--border)" stroke-width="8" fill="none"/>
                <circle cx="60" cy="60" r="{radius}"
                    stroke="var(--primary)" stroke-width="8" fill="none"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    transform="rotate(-90 60 60)"
                    style="transition: stroke-dashoffset 1s ease;"/>
                <text x="60" y="60" text-anchor="middle" dy="7"
                    style="font-size: 20px; font-weight: 700; fill: var(--text-primary);">
                    {percentage:.0f}%
                </text>
            </svg>
            <div style="margin-top: 8px; color: var(--text-secondary); font-size: 14px;">
                {label}
            </div>
        </div>
        """
        components.html(html, height=180, scrolling=False)


# 使用示例
if __name__ == "__main__":
    st.set_page_config(
        page_title="Modern Theme Demo",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用主题
    ModernTheme.apply_theme()
    
    # Hero区域
    ModernTheme.create_hero_section(
        "现代化UI主题",
        "Apple风格设计：简洁、优雅、流畅"
    )
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ModernTheme.create_stat_card("总资产", "$1,234,567", "+12.5%", True)
    
    with col2:
        ModernTheme.create_stat_card("今日收益", "$5,678", "+2.3%", True)
    
    with col3:
        ModernTheme.create_stat_card("持仓币种", "12", None)
    
    with col4:
        ModernTheme.create_stat_card("风险等级", "中", "-5%", False)
    
    ModernTheme.create_divider()
    
    # 玻璃态卡片
    col1, col2 = st.columns(2)
    
    with col1:
        ModernTheme.create_glass_card("<h3>市场概览</h3><p>这是一个玻璃态卡片效果</p>")
    
    with col2:
        ModernTheme.create_progress_ring(75, "完成度")

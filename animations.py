"""
Premium Finance UI - 动画系统
====================================
Lottie 动画集成 + 数字滚动动画
"""

import streamlit as st
import streamlit.components.v1 as components


# Lottie 动画 JSON URL 资源库
LOTTIE_ANIMATIONS = {
    "loading": "https://assets10.lottiefiles.com/packages/lf20_p8bfn5to.json",  # 加载动画
    "empty": "https://assets4.lottiefiles.com/packages/lf20_uu0x8lqv.json",     # 空状态
    "success": "https://assets9.lottiefiles.com/packages/lf20_w51pcehl.json",   # 成功
    "error": "https://assets9.lottiefiles.com/packages/lf20_tl52xzvn.json",     # 错误
    "chart": "https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json",     # 图表动画
    "money": "https://assets8.lottiefiles.com/packages/lf20_06u6ijdg.json",     # 金钱动画
}


def render_lottie(animation_url: str, height: int = 300, key: str = None):
    """
    渲染 Lottie 动画
    
    参数:
        animation_url: Lottie JSON 文件 URL
        height: 动画高度（像素）
        key: Streamlit 组件 key
    """
    try:
        from streamlit_lottie import st_lottie
        import requests
        
        # 获取动画数据
        response = requests.get(animation_url)
        animation_json = response.json() if response.status_code == 200 else None
        
        if animation_json:
            st_lottie(
                animation_json,
                height=height,
                key=key,
                quality="high",
                speed=1
            )
        else:
            st.warning("无法加载动画")
    except ImportError:
        st.info("请安装 streamlit-lottie: `pip install streamlit-lottie`")
    except Exception as e:
        st.error(f"动画加载失败: {e}")


def render_loading_animation(height: int = 200, key: str = None):
    """渲染加载动画"""
    render_lottie(LOTTIE_ANIMATIONS["loading"], height, key)


def render_empty_state(height: int = 250, key: str = None):
    """渲染空状态动画"""
    render_lottie(LOTTIE_ANIMATIONS["empty"], height, key)


def render_success_animation(height: int = 150, key: str = None):
    """渲染成功动画"""
    render_lottie(LOTTIE_ANIMATIONS["success"], height, key)


def animate_number(
    target_value: float,
    start_value: float = 0,
    duration: int = 800,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 2,
    container_id: str = "animated-number"
) -> str:
    """
    生成数字滚动动画的 HTML/JS 代码
    
    参数:
        target_value: 目标数值
        start_value: 起始数值
        duration: 动画时长（毫秒）
        prefix: 前缀（如 "$"）
        suffix: 后缀（如 "%"）
        decimals: 小数位数
        container_id: 容器 ID
    
    返回:
        HTML 字符串，可通过 st.markdown 或 components.html 渲染
    """
    
    html_code = f"""
    <div id="{container_id}" style="
        font-size: 48px;
        font-weight: 700;
        color: #FFFFFF;
        font-variant-numeric: tabular-nums;
        text-align: center;
        padding: 20px;
    ">
        {prefix}0{suffix}
    </div>
    
    <script>
    (function() {{
        const target = {target_value};
        const start = {start_value};
        const duration = {duration};
        const decimals = {decimals};
        const prefix = "{prefix}";
        const suffix = "{suffix}";
        const element = document.getElementById("{container_id}");
        
        const startTime = performance.now();
        
        function easeOutCubic(t) {{
            return 1 - Math.pow(1 - t, 3);
        }}
        
        function animate(currentTime) {{
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeOutCubic(progress);
            
            const currentValue = start + (target - start) * easedProgress;
            element.textContent = prefix + currentValue.toFixed(decimals) + suffix;
            
            if (progress < 1) {{
                requestAnimationFrame(animate);
            }}
        }}
        
        requestAnimationFrame(animate);
    }})();
    </script>
    """
    
    return html_code


def create_counter_component(value: float, label: str = "", prefix: str = "", suffix: str = "", color: str = "#FF7A29"):
    """
    创建带动画的计数器组件
    
    参数:
        value: 数值
        label: 标签
        prefix: 前缀
        suffix: 后缀
        color: 颜色
    """
    
    html = f"""
    <div style="
        background: rgba(30, 30, 38, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    " class="counter-card">
        <div style="
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            font-weight: 500;
        ">{label}</div>
        <div style="
            font-size: 42px;
            font-weight: 700;
            color: {color};
            font-variant-numeric: tabular-nums;
        " class="counter-value">{prefix}{value}{suffix}</div>
    </div>
    
    <style>
    .counter-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.45), 0 0 24px rgba(255, 122, 41, 0.25);
        border-color: rgba(255, 122, 41, 0.3);
    }}
    </style>
    """
    
    components.html(html, height=140)


def create_progress_ring(percentage: float, size: int = 120, stroke_width: int = 8, color: str = "#FF7A29"):
    """
    创建环形进度条
    
    参数:
        percentage: 百分比 (0-100)
        size: 尺寸
        stroke_width: 线条宽度
        color: 颜色
    """
    
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100 * circumference)
    
    html = f"""
    <div style="display: flex; justify-content: center; align-items: center; position: relative;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <!-- 背景圆环 -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="rgba(255, 255, 255, 0.1)"
                stroke-width="{stroke_width}"
            />
            <!-- 进度圆环 -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="{color}"
                stroke-width="{stroke_width}"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                style="
                    transition: stroke-dashoffset 0.8s cubic-bezier(0.22, 1, 0.36, 1);
                    filter: drop-shadow(0 0 8px {color}66);
                "
            />
        </svg>
        <div style="
            position: absolute;
            font-size: 24px;
            font-weight: 700;
            color: {color};
            font-variant-numeric: tabular-nums;
        ">
            {percentage:.0f}%
        </div>
    </div>
    """
    
    components.html(html, height=size + 20)


def create_sparkline(values: list, width: int = 200, height: int = 50, color: str = "#FF7A29"):
    """
    创建迷你趋势图（Sparkline）
    
    参数:
        values: 数据点列表
        width: 宽度
        height: 高度
        color: 颜色
    """
    
    if not values or len(values) < 2:
        return
    
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val != min_val else 1
    
    # 生成 SVG 路径
    points = []
    x_step = width / (len(values) - 1)
    
    for i, val in enumerate(values):
        x = i * x_step
        y = height - ((val - min_val) / range_val * height)
        points.append(f"{x},{y}")
    
    path = "M " + " L ".join(points)
    
    html = f"""
    <svg width="{width}" height="{height}" style="display: block;">
        <!-- 渐变定义 -->
        <defs>
            <linearGradient id="sparkline-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.4" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.05" />
            </linearGradient>
        </defs>
        
        <!-- 填充区域 -->
        <path
            d="{path} L {width},{height} L 0,{height} Z"
            fill="url(#sparkline-gradient)"
        />
        
        <!-- 线条 -->
        <path
            d="{path}"
            fill="none"
            stroke="{color}"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
        />
        
        <!-- 最后一个点 -->
        <circle
            cx="{width}"
            cy="{height - ((values[-1] - min_val) / range_val * height)}"
            r="3"
            fill="{color}"
            style="filter: drop-shadow(0 0 4px {color})"
        />
    </svg>
    """
    
    components.html(html, height=height + 10)


def create_toast_notification(message: str, type: str = "success", duration: int = 2400):
    """
    创建 Toast 通知
    
    参数:
        message: 通知消息
        type: 类型 ('success', 'error', 'warning', 'info')
        duration: 显示时长（毫秒）
    """
    
    colors = {
        "success": "#10B981",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6"
    }
    
    color = colors.get(type, colors["info"])
    
    html = f"""
    <div id="toast-notification" style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(30, 30, 38, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid {color};
        border-radius: 12px;
        padding: 16px 24px;
        color: white;
        font-weight: 500;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        z-index: 9999;
        animation: slideInRight 0.3s ease-out, slideOutRight 0.2s ease-in {duration/1000}s forwards;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {color};
            box-shadow: 0 0 8px {color};
        "></div>
        <span>{message}</span>
    </div>
    
    <style>
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(100px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes slideOutRight {{
        from {{
            opacity: 1;
            transform: translateX(0);
        }}
        to {{
            opacity: 0;
            transform: translateX(100px);
        }}
    }}
    </style>
    
    <script>
    setTimeout(() => {{
        const toast = document.getElementById('toast-notification');
        if (toast) toast.remove();
    }}, {duration + 200});
    </script>
    """
    
    components.html(html, height=0)

"""
Apple级别专业仪表板
参考Meevis Solar Panel设计: 3D视觉 + 卡片布局 + 玻璃态效果
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, List, Optional
import random


class AppleDashboard:
    """Apple级别仪表板组件"""
    
    # Apple色彩系统
    COLORS = {
        'primary': '#0A84FF',      # Apple Blue
        'success': '#32D74B',      # Apple Green  
        'warning': '#FF9F0A',      # Apple Orange
        'danger': '#FF453A',       # Apple Red
        'purple': '#BF5AF2',       # Apple Purple
        'teal': '#64D2FF',         # Apple Teal
        
        'bg_card': 'rgba(28, 28, 30, 0.92)',       # 深色卡片背景
        'bg_elevated': 'rgba(44, 44, 46, 0.95)',   # 提升层背景
        'border': 'rgba(255, 255, 255, 0.12)',     # 边框
        
        'text_primary': '#F5F5F7',     # 主文字
        'text_secondary': '#86868B',   # 次要文字
        'text_tertiary': '#48484A',    # 三级文字
    }
    
    @staticmethod
    def create_hero_banner(title: str, subtitle: str = None):
        """
        创建Hero Banner - 参考Apple官网
        带3D背景元素和渐变标题
        """
        hero_id = f"hero-{random.randint(1000, 9999)}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: #000; 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            overflow: hidden;
        }}
        .hero-container {{
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px 20px;
            overflow: hidden;
        }}
        
        /* 3D背景网格 */
        .grid-3d {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            perspective: 1000px;
            transform-style: preserve-3d;
        }}
        .grid-lines {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 200%;
            height: 200%;
            transform: translateX(-50%) translateY(-30%) rotateX(60deg);
            background-image: 
                linear-gradient(0deg, transparent 24%, rgba(0, 132, 255, 0.05) 25%, rgba(0, 132, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 132, 255, 0.05) 75%, rgba(0, 132, 255, 0.05) 76%, transparent 77%, transparent),
                linear-gradient(90deg, transparent 24%, rgba(0, 132, 255, 0.05) 25%, rgba(0, 132, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 132, 255, 0.05) 75%, rgba(0, 132, 255, 0.05) 76%, transparent 77%, transparent);
            background-size: 80px 80px;
            animation: gridMove 20s linear infinite;
        }}
        
        @keyframes gridMove {{
            0% {{ transform: translateX(-50%) translateY(-30%) rotateX(60deg) translateZ(0); }}
            100% {{ transform: translateX(-50%) translateY(-30%) rotateX(60deg) translateZ(80px); }}
        }}
        
        /* 光晕效果 */
        .glow {{
            position: absolute;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 132, 255, 0.15) 0%, transparent 70%);
            filter: blur(60px);
            animation: pulse 4s ease-in-out infinite;
        }}
        .glow-1 {{ top: -200px; left: -100px; }}
        .glow-2 {{ bottom: -200px; right: -100px; background: radial-gradient(circle, rgba(191, 90, 242, 0.12) 0%, transparent 70%); animation-delay: 2s; }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.6; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}
        
        /* 标题样式 */
        .hero-title {{
            position: relative;
            z-index: 10;
            font-size: 72px;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.05;
            text-align: center;
            background: linear-gradient(135deg, #0A84FF 0%, #64D2FF 50%, #BF5AF2 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientFlow 8s ease infinite, titleFadeIn 1s ease-out;
            margin-bottom: 20px;
        }}
        
        @keyframes gradientFlow {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        @keyframes titleFadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .hero-subtitle {{
            position: relative;
            z-index: 10;
            font-size: 24px;
            font-weight: 400;
            color: #86868B;
            text-align: center;
            letter-spacing: -0.01em;
            line-height: 1.4;
            animation: subtitleFadeIn 1s ease-out 0.3s both;
        }}
        
        @keyframes subtitleFadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        </style>
        </head>
        <body>
        <div class="hero-container">
            <div class="grid-3d">
                <div class="grid-lines"></div>
            </div>
            <div class="glow glow-1"></div>
            <div class="glow glow-2"></div>
            
            <h1 class="hero-title" id="{hero_id}">{title}</h1>
            {f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        </body>
        </html>
        """
        
        components.html(html, height=300)
    
    @staticmethod
    def create_metric_card(
        label: str,
        value: str,
        unit: str = "",
        sublabel: str = None,
        subvalue: str = None,
        trend: str = None,  # 'up', 'down', 'neutral'
        progress: float = None,  # 0-100
        chart_data: List[float] = None,
        color: str = 'primary'
    ):
        """
        创建指标卡片 - 参考图三的Solar Panel卡片
        
        Args:
            label: 主标签 (如 "Current Power")
            value: 主数值 (如 "5.48")
            unit: 单位 (如 "kW")
            sublabel: 次级标签
            subvalue: 次级数值
            trend: 趋势 ('up', 'down', 'neutral')
            progress: 进度百分比 (0-100)
            chart_data: 迷你图表数据
            color: 主题色
        """
        card_id = f"card-{random.randint(1000, 9999)}"
        color_hex = AppleDashboard.COLORS.get(color, AppleDashboard.COLORS['primary'])
        
        # 趋势箭头
        trend_html = ""
        if trend:
            trend_icons = {
                'up': '↗',
                'down': '↘', 
                'neutral': '→'
            }
            trend_colors = {
                'up': AppleDashboard.COLORS['success'],
                'down': AppleDashboard.COLORS['danger'],
                'neutral': AppleDashboard.COLORS['text_secondary']
            }
            trend_html = f'''
            <div style="
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 24px;
                color: {trend_colors[trend]};
                animation: trendFloat 2s ease-in-out infinite;
            ">{trend_icons[trend]}</div>
            '''
        
        # 进度条
        progress_html = ""
        if progress is not None:
            progress_html = f'''
            <div style="margin-top: 20px;">
                <div style="
                    height: 4px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                    overflow: hidden;
                ">
                    <div style="
                        height: 100%;
                        width: {progress}%;
                        background: linear-gradient(90deg, {color_hex}, {color_hex}80);
                        border-radius: 2px;
                        transition: width 1.5s cubic-bezier(0.23, 1, 0.32, 1);
                        box-shadow: 0 0 10px {color_hex}60;
                    "></div>
                </div>
                <div style="
                    display: flex;
                    justify-content: space-between;
                    margin-top: 8px;
                    font-size: 12px;
                    color: {AppleDashboard.COLORS['text_tertiary']};
                ">
                    <span>0</span>
                    <span>50</span>
                    <span>100</span>
                </div>
            </div>
            '''
        
        # 迷你图表
        chart_html = ""
        if chart_data:
            max_val = max(chart_data)
            min_val = min(chart_data)
            range_val = max_val - min_val if max_val != min_val else 1
            
            points = []
            for i, val in enumerate(chart_data):
                x = (i / (len(chart_data) - 1)) * 100
                y = 100 - ((val - min_val) / range_val) * 100
                points.append(f"{x},{y}")
            
            polyline = " ".join(points)
            
            chart_html = f'''
            <svg viewBox="0 0 100 40" style="
                width: 100%;
                height: 60px;
                margin-top: 16px;
            ">
                <polyline
                    points="{polyline}"
                    fill="none"
                    stroke="{color_hex}"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    style="
                        filter: drop-shadow(0 0 6px {color_hex}60);
                        animation: drawLine 2s ease-out;
                    "
                />
            </svg>
            <style>
            @keyframes drawLine {{
                from {{ stroke-dasharray: 1000; stroke-dashoffset: 1000; }}
                to {{ stroke-dasharray: 1000; stroke-dashoffset: 0; }}
            }}
            </style>
            '''
        
        # 次级信息
        sub_info_html = ""
        if sublabel and subvalue:
            sub_info_html = f'''
            <div style="
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid {AppleDashboard.COLORS['border']};
            ">
                <span style="font-size: 13px; color: {AppleDashboard.COLORS['text_secondary']};">{sublabel}</span>
                <span style="font-size: 13px; font-weight: 600; color: {AppleDashboard.COLORS['text_primary']}; 
                    font-family: 'SF Mono', monospace;">{subvalue}</span>
            </div>
            '''
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            padding: 4px;
        }}
        .metric-card {{
            position: relative;
            background: {AppleDashboard.COLORS['bg_card']};
            backdrop-filter: blur(40px) saturate(180%);
            border: 1px solid {AppleDashboard.COLORS['border']};
            border-radius: 20px;
            padding: 28px;
            transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            cursor: pointer;
            box-shadow: 
                0 4px 24px rgba(0, 0, 0, 0.3),
                0 8px 40px rgba(0, 0, 0, 0.2);
        }}
        .metric-card:hover {{
            transform: translateY(-4px) scale(1.01);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                0 12px 60px rgba(0, 0, 0, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.15);
        }}
        
        .label {{
            font-size: 13px;
            font-weight: 600;
            color: {AppleDashboard.COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 16px;
        }}
        
        .value-container {{
            display: flex;
            align-items: baseline;
            gap: 6px;
        }}
        
        .value {{
            font-size: 56px;
            font-weight: 700;
            color: {AppleDashboard.COLORS['text_primary']};
            letter-spacing: -0.04em;
            line-height: 1;
            font-variant-numeric: tabular-nums;
            animation: countUp 1.5s cubic-bezier(0.23, 1, 0.32, 1);
        }}
        
        .unit {{
            font-size: 20px;
            font-weight: 500;
            color: {AppleDashboard.COLORS['text_secondary']};
            align-self: flex-end;
            padding-bottom: 8px;
        }}
        
        @keyframes countUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes trendFloat {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-4px); }}
        }}
        </style>
        </head>
        <body>
        <div class="metric-card" id="{card_id}">
            {trend_html}
            <div class="label">{label}</div>
            <div class="value-container">
                <div class="value">{value}</div>
                {f'<div class="unit">{unit}</div>' if unit else ''}
            </div>
            {progress_html}
            {chart_html}
            {sub_info_html}
        </div>
        </body>
        </html>
        """
        
        components.html(html, height=280, scrolling=False)
    
    @staticmethod
    def create_signal_panel(
        signal: str,
        confidence: float,
        indicators: Dict[str, Any] = None
    ):
        """
        创建交易信号面板 - 玻璃态设计
        
        Args:
            signal: 信号类型 ('买入', '卖出', '持有', '观望')
            confidence: 信心度 (0-100)
            indicators: 技术指标详情
        """
        signal_config = {
            '买入': {'color': AppleDashboard.COLORS['success'], 'icon': '●', 'label': 'BUY'},
            '卖出': {'color': AppleDashboard.COLORS['danger'], 'icon': '●', 'label': 'SELL'},
            '持有': {'color': AppleDashboard.COLORS['primary'], 'icon': '●', 'label': 'HOLD'},
            '观望': {'color': AppleDashboard.COLORS['warning'], 'icon': '●', 'label': 'WAIT'},
        }
        
        config = signal_config.get(signal, signal_config['观望'])
        
        indicators_html = ""
        if indicators:
            rows = []
            for key, val in indicators.items():
                rows.append(f'''
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 12px 0;
                    border-bottom: 1px solid {AppleDashboard.COLORS['border']};
                ">
                    <span style="color: {AppleDashboard.COLORS['text_secondary']};">{key}</span>
                    <span style="
                        font-weight: 600;
                        color: {AppleDashboard.COLORS['text_primary']};
                        font-family: 'SF Mono', monospace;
                    ">{val}</span>
                </div>
                ''')
            indicators_html = f'''
            <div style="margin-top: 24px;">
                <div style="
                    font-size: 12px;
                    font-weight: 600;
                    color: {AppleDashboard.COLORS['text_secondary']};
                    text-transform: uppercase;
                    letter-spacing: 0.06em;
                    margin-bottom: 12px;
                ">技术指标</div>
                {''.join(rows)}
            </div>
            '''
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            padding: 4px;
        }}
        .signal-panel {{
            background: {AppleDashboard.COLORS['bg_elevated']};
            backdrop-filter: blur(60px) saturate(200%);
            border: 1px solid {AppleDashboard.COLORS['border']};
            border-radius: 24px;
            padding: 32px;
            position: relative;
            overflow: hidden;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                0 16px 72px rgba(0, 0, 0, 0.3);
        }}
        
        .signal-top-bar {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {config['color']}, {config['color']}60);
            box-shadow: 0 0 20px {config['color']}80;
        }}
        
        .signal-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 32px;
        }}
        
        .signal-icon {{
            font-size: 80px;
            color: {config['color']};
            line-height: 1;
            animation: pulse 2s ease-in-out infinite;
            filter: drop-shadow(0 0 20px {config['color']}60);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.9; }}
            50% {{ transform: scale(1.1); opacity: 1; }}
        }}
        
        .signal-content {{
            flex: 1;
        }}
        
        .signal-label {{
            font-size: 12px;
            font-weight: 700;
            color: {AppleDashboard.COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }}
        
        .signal-text {{
            font-size: 48px;
            font-weight: 700;
            color: {AppleDashboard.COLORS['text_primary']};
            letter-spacing: -0.03em;
            line-height: 1;
        }}
        
        .confidence-section {{
            margin-top: 24px;
        }}
        
        .confidence-label {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 12px;
        }}
        
        .confidence-bar {{
            height: 8px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}
        
        .confidence-fill {{
            height: 100%;
            width: {confidence}%;
            background: linear-gradient(90deg, {config['color']}, {config['color']}80);
            border-radius: 4px;
            box-shadow: 0 0 16px {config['color']}60;
            animation: fillBar 1.5s cubic-bezier(0.23, 1, 0.32, 1);
        }}
        
        @keyframes fillBar {{
            from {{ width: 0%; }}
            to {{ width: {confidence}%; }}
        }}
        </style>
        </head>
        <body>
        <div class="signal-panel">
            <div class="signal-top-bar"></div>
            
            <div class="signal-header">
                <div class="signal-icon">{config['icon']}</div>
                <div class="signal-content">
                    <div class="signal-label">{config['label']} SIGNAL</div>
                    <div class="signal-text">{signal}</div>
                </div>
            </div>
            
            <div class="confidence-section">
                <div class="confidence-label">
                    <span style="color: {AppleDashboard.COLORS['text_secondary']};">信心度</span>
                    <span style="
                        font-weight: 700;
                        color: {config['color']};
                        font-family: 'SF Mono', monospace;
                    ">{confidence:.0f}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill"></div>
                </div>
            </div>
            
            {indicators_html}
        </div>
        </body>
        </html>
        """
        
        components.html(html, height=380 if indicators else 280, scrolling=False)

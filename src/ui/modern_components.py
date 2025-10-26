"""
现代化UI组件库
提供可复用的高级UI组件
"""
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional


class ModernComponents:
    """现代化组件库"""
    
    @staticmethod
    def price_card(
        symbol: str,
        name: str,
        price: float,
        change_24h: float,
        volume_24h: float = None,
        market_cap: float = None,
        icon: str = "💎"
    ):
        """
        Apple级别价格卡片组件 - 带3D磁性悬浮效果
        
        Args:
            symbol: 交易符号
            name: 名称
            price: 当前价格
            change_24h: 24小时涨跌幅
            volume_24h: 24小时成交量
            market_cap: 市值
            icon: 图标
        """
        is_positive = change_24h >= 0
        color = "#30D158" if is_positive else "#FF453A"  # Apple绿/红
        arrow = "▲" if is_positive else "▼"
        
        # 生成唯一ID用于JS交互
        import random
        card_id = f"price-card-{random.randint(1000, 9999)}"
        
        html = f"""
        <div id="{card_id}" class="modern-card" 
             style="position: relative; overflow: hidden; cursor: pointer; 
                    transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);">
            
            <div class="card-glow" style="
                position: absolute; 
                inset: 0; 
                pointer-events: none; 
                opacity: 0;
                background: radial-gradient(
                    600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                    {color}20,
                    transparent 40%
                );
                transition: opacity 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            "></div>
            
            <div style="position: relative; z-index: 1;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 36px; line-height: 1; margin-bottom: 8px;">{icon}</div>
                        <div style="font-size: 24px; font-weight: 700; letter-spacing: -0.022em; 
                            color: #F5F5F7; margin-bottom: 2px;">{symbol}</div>
                        <div style="font-size: 13px; font-weight: 500; color: var(--text-secondary); 
                            letter-spacing: 0.01em;">{name}</div>
                    </div>
                    <div style="text-align: right; padding: 8px 14px; background: {color}15; 
                        border-radius: 980px; border: 0.5px solid {color}30;">
                        <div style="font-size: 17px; font-weight: 700; color: {color}; 
                            letter-spacing: -0.022em;">
                            {arrow} {abs(change_24h):.2f}%
                        </div>
                    </div>
                </div>
                
                <div class="price-number" style="
                    font-size: 48px; 
                    font-weight: 700; 
                    font-family: 'SF Mono', 'Menlo', 'Consolas', monospace; 
                    letter-spacing: -0.04em;
                    color: #F5F5F7; 
                    margin-bottom: 24px;
                    line-height: 1;
                    font-variant-numeric: tabular-nums;
                ">
                    ${price:,.2f}
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
        """
        
        if volume_24h:
            html += f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 12px; 
                        border-radius: 12px; border: 0.5px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 11px; font-weight: 600; color: var(--text-secondary); 
                            text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                            24H VOLUME
                        </div>
                        <div style="font-size: 16px; font-weight: 700; color: #F5F5F7; 
                            font-family: 'SF Mono', monospace; font-variant-numeric: tabular-nums;">
                            ${volume_24h/1e9:.2f}B
                        </div>
                    </div>
            """
        
        if market_cap:
            html += f"""
                    <div style="background: rgba(255,255,255,0.03); padding: 12px; 
                        border-radius: 12px; border: 0.5px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 11px; font-weight: 600; color: var(--text-secondary); 
                            text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                            MARKET CAP
                        </div>
                        <div style="font-size: 16px; font-weight: 700; color: #F5F5F7; 
                            font-family: 'SF Mono', monospace; font-variant-numeric: tabular-nums;">
                            ${market_cap/1e9:.2f}B
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </div>
        
        <script>
        (function() {
            const card = document.getElementById('""" + card_id + """');
            if (!card) return;
            
            const glow = card.querySelector('.card-glow');
            let rafId = null;
            
            // Apple磁性3D效果
            card.addEventListener('mousemove', (e) => {
                if (rafId) cancelAnimationFrame(rafId);
                
                rafId = requestAnimationFrame(() => {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    // 计算3D旋转角度
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    const rotateX = ((y - centerY) / centerY) * -5;
                    const rotateY = ((x - centerX) / centerX) * 5;
                    
                    // 应用3D变换
                    card.style.transform = `
                        perspective(1000px) 
                        rotateX(${rotateX}deg) 
                        rotateY(${rotateY}deg) 
                        translateY(-8px) 
                        scale(1.02)
                    `;
                    
                    // 更新光晕位置
                    glow.style.setProperty('--mouse-x', `${x}px`);
                    glow.style.setProperty('--mouse-y', `${y}px`);
                    glow.style.opacity = '1';
                });
            });
            
            card.addEventListener('mouseleave', () => {
                if (rafId) cancelAnimationFrame(rafId);
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
                glow.style.opacity = '0';
            });
        })();
        </script>
        """
        
        components.html(html, height=300, scrolling=False)
    
    @staticmethod
    def signal_indicator(
        signal: str,
        confidence: float,
        signals_detail: Dict[str, Any] = None
    ):
        """
        Apple级别信号指示器组件 - 玻璃态设计
        
        Args:
            signal: 信号类型 ('买入', '卖出', '持有', '观望')
            confidence: 信心度 (0-100)
            signals_detail: 详细信号数据
        """
        # 信号配置 - Apple色彩
        signal_config = {
            '买入': {'color': '#30D158', 'icon': '●', 'label': 'BUY SIGNAL'},
            '卖出': {'color': '#FF453A', 'icon': '●', 'label': 'SELL SIGNAL'},
            '持有': {'color': '#0A84FF', 'icon': '●', 'label': 'HOLD SIGNAL'},
            '观望': {'color': '#FF9F0A', 'icon': '●', 'label': 'WAIT SIGNAL'},
        }
        
        config = signal_config.get(signal, signal_config['观望'])
        
        html = f"""
        <div class="glass-card" style="
            background: rgba(29, 29, 31, 0.7); 
            backdrop-filter: blur(40px) saturate(180%);
            border: 0.5px solid rgba(255, 255, 255, 0.18);
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; 
                background: linear-gradient(90deg, {config['color']}, {config['color']}80);
                box-shadow: 0 0 20px {config['color']}60;">
            </div>
            
            <div style="padding-top: 8px;">
                <div style="
                    font-size: 11px; 
                    font-weight: 700; 
                    color: var(--text-secondary); 
                    text-transform: uppercase; 
                    letter-spacing: 0.08em;
                    margin-bottom: 12px;
                ">{config['label']}</div>
                
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                    <div style="
                        font-size: 64px; 
                        color: {config['color']}; 
                        line-height: 1;
                        text-shadow: 0 0 30px {config['color']}50;
                    ">{config['icon']}</div>
                    <div style="flex: 1;">
                        <div style="
                            font-size: 42px; 
                            font-weight: 700; 
                            color: #F5F5F7;
                            letter-spacing: -0.03em;
                            line-height: 1;
                            text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
                        ">{signal}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px;">
                        <span style="
                            font-size: 12px; 
                            font-weight: 600; 
                            color: var(--text-secondary);
                            text-transform: uppercase;
                            letter-spacing: 0.06em;
                        ">Confidence</span>
                        <span style="
                            font-size: 24px; 
                            font-weight: 700; 
                            color: {config['color']};
                            font-family: 'SF Mono', monospace;
                            letter-spacing: -0.02em;
                        ">{confidence:.0f}%</span>
                    </div>
                    
                    <div style="
                        background: rgba(255, 255, 255, 0.06); 
                        border-radius: 980px; 
                        height: 8px; 
                        overflow: hidden;
                        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
                    ">
                        <div style="
                            background: linear-gradient(90deg, {config['color']}, {config['color']}CC); 
                            width: {confidence}%; 
                            height: 100%; 
                            border-radius: 980px;
                            transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
                            box-shadow: 0 0 10px {config['color']}80;
                        "></div>
                    </div>
                </div>
        """
        
        # 详细信号网格
        if signals_detail:
            html += f"""
                <div style="
                    height: 0.5px; 
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                    margin: 20px 0;
                "></div>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
            """
            
            for key, value in signals_detail.items():
                html += f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03); 
                    padding: 12px; 
                    border-radius: 12px;
                    border: 0.5px solid rgba(255, 255, 255, 0.06);
                ">
                    <div style="
                        font-size: 11px; 
                        font-weight: 600; 
                        color: var(--text-secondary); 
                        text-transform: uppercase; 
                        letter-spacing: 0.06em;
                        margin-bottom: 6px;
                    ">{key}</div>
                    <div style="
                        font-size: 16px; 
                        font-weight: 700; 
                        color: #F5F5F7;
                        font-family: 'SF Mono', monospace;
                        letter-spacing: -0.01em;
                    ">{value}</div>
                </div>
                """
            
            html += """
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        components.html(html, height=400, scrolling=False)
    
    @staticmethod
    def create_modern_chart(
        data: Dict[str, List],
        chart_type: str = 'line',
        title: str = None,
        height: int = 400
    ):
        """
        创建现代化图表
        
        Args:
            data: 图表数据
            chart_type: 图表类型 ('line', 'candlestick', 'bar', 'area')
            title: 图表标题
            height: 图表高度
        """
        fig = go.Figure()
        
        # 深色主题配置
        layout = dict(
            template='plotly_dark',
            paper_bgcolor='rgba(28, 28, 30, 0.5)',
            plot_bgcolor='rgba(28, 28, 30, 0.5)',
            font=dict(family='-apple-system, BlinkMacSystemFont, sans-serif', color='#FFFFFF'),
            title=dict(text=title, font=dict(size=20, weight=700), x=0.5, xanchor='center'),
            height=height,
            margin=dict(l=60, r=40, t=80, b=60),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='rgba(28, 28, 30, 0.95)',
                font_size=13,
                font_family='-apple-system',
                bordercolor='#38383A'
            ),
            xaxis=dict(
                gridcolor='#38383A',
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor='#38383A'
            ),
            yaxis=dict(
                gridcolor='#38383A',
                showgrid=True,
                zeroline=False,
                showline=True,
                linecolor='#38383A'
            )
        )
        
        # 根据图表类型添加trace
        if chart_type == 'line':
            fig.add_trace(go.Scatter(
                x=data.get('x', []),
                y=data.get('y', []),
                mode='lines',
                name=data.get('name', ''),
                line=dict(color='#007AFF', width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 122, 255, 0.1)'
            ))
        
        elif chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=data.get('x', []),
                open=data.get('open', []),
                high=data.get('high', []),
                low=data.get('low', []),
                close=data.get('close', []),
                increasing_line_color='#34C759',
                decreasing_line_color='#FF3B30',
                name='K线'
            ))
        
        elif chart_type == 'bar':
            fig.add_trace(go.Bar(
                x=data.get('x', []),
                y=data.get('y', []),
                marker=dict(
                    color=data.get('y', []),
                    colorscale=[[0, '#FF3B30'], [0.5, '#FF9500'], [1, '#34C759']],
                    line=dict(width=0)
                )
            ))
        
        elif chart_type == 'area':
            fig.add_trace(go.Scatter(
                x=data.get('x', []),
                y=data.get('y', []),
                mode='lines',
                fill='tonexty',
                line=dict(color='#007AFF', width=2),
                fillcolor='rgba(0, 122, 255, 0.2)'
            ))
        
        fig.update_layout(**layout)
        
        return fig
    
    @staticmethod
    def metric_grid(metrics: List[Dict[str, Any]], columns: int = 4):
        """
        Apple级别指标网格组件 - 数字计数动画
        
        Args:
            metrics: 指标列表 [{'label': '', 'value': '', 'change': '', 'icon': ''}]
            columns: 列数
        """
        cols = st.columns(columns)
        
        for idx, metric in enumerate(metrics):
            with cols[idx % columns]:
                label = metric.get('label', '')
                value = metric.get('value', '')
                change = metric.get('change', None)
                icon = metric.get('icon', '📊')
                
                is_positive = True
                if change:
                    is_positive = not str(change).startswith('-')
                
                color = '#30D158' if is_positive else '#FF453A'  # Apple绿/红
                arrow = '▲' if is_positive else '▼'
                
                # 生成唯一ID
                import random
                metric_id = f"metric-{random.randint(1000, 9999)}"
                
                html = f"""
                <div class="modern-card" style="
                    text-align: center; 
                    padding: 24px 20px;
                    background: rgba(255, 255, 255, 0.04);
                    transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
                ">
                    <div style="
                        font-size: 40px; 
                        line-height: 1;
                        margin-bottom: 16px;
                        filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
                    ">{icon}</div>
                    
                    <div style="
                        font-size: 11px; 
                        font-weight: 600;
                        color: var(--text-secondary); 
                        text-transform: uppercase; 
                        letter-spacing: 0.08em; 
                        margin-bottom: 12px;
                    ">{label}</div>
                    
                    <div id="{metric_id}" class="metric-value" style="
                        font-size: 36px; 
                        font-weight: 700; 
                        color: #F5F5F7; 
                        margin-bottom: 10px; 
                        font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
                        letter-spacing: -0.03em;
                        line-height: 1;
                        font-variant-numeric: tabular-nums;
                    " data-target="{value}">{value}</div>
                """
                
                if change:
                    html += f"""
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 4px;
                        padding: 4px 12px;
                        background: {color}15;
                        border: 0.5px solid {color}30;
                        border-radius: 980px;
                    ">
                        <span style="font-size: 14px; color: {color};">{arrow}</span>
                        <span style="font-size: 14px; font-weight: 700; color: {color}; 
                            font-family: 'SF Mono', monospace;">
                            {change}
                        </span>
                    </div>
                    """
                
                html += """
                </div>
                """
                components.html(html, height=200, scrolling=False)
    
    @staticmethod
    def timeline_item(
        time: str,
        title: str,
        description: str,
        type: str = 'info'
    ):
        """
        时间线项目组件
        
        Args:
            time: 时间
            title: 标题
            description: 描述
            type: 类型 ('success', 'warning', 'danger', 'info')
        """
        colors = {
            'success': '#34C759',
            'warning': '#FF9500',
            'danger': '#FF3B30',
            'info': '#007AFF'
        }
        
        color = colors.get(type, colors['info'])
        
        html = f"""
        <div style="display: flex; gap: 16px; margin-bottom: 24px;" class="fade-in">
            <div style="flex-shrink: 0; width: 12px; height: 12px; border-radius: 50%; 
                background: {color}; margin-top: 6px; box-shadow: 0 0 0 4px {color}33;">
            </div>
            
            <div style="flex: 1;">
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">
                    {time}
                </div>
                <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">
                    {title}
                </div>
                <div style="font-size: 14px; color: var(--text-secondary);">
                    {description}
                </div>
            </div>
        </div>
        """
        
        components.html(html, height=120, scrolling=False)
    
    @staticmethod
    def apple_button(
        text: str,
        button_type: str = 'primary',
        icon: str = None,
        onclick: str = None
    ):
        """
        Apple级别按钮组件 - 980px药丸形状 + Ripple效果
        
        Args:
            text: 按钮文字
            button_type: 按钮类型 ('primary', 'secondary', 'success', 'danger')
            icon: 图标(可选)
            onclick: 点击事件JS代码(可选)
        """
        import random
        btn_id = f"apple-btn-{random.randint(1000, 9999)}"
        
        # 按钮配置
        btn_config = {
            'primary': {'bg': '#0071E3', 'hover': '#0077ED', 'shadow': 'rgba(0, 113, 227, 0.4)'},
            'secondary': {'bg': '#5856D6', 'hover': '#6C6AE8', 'shadow': 'rgba(88, 86, 214, 0.4)'},
            'success': {'bg': '#30D158', 'hover': '#32D65C', 'shadow': 'rgba(48, 209, 88, 0.4)'},
            'danger': {'bg': '#FF453A', 'hover': '#FF4F44', 'shadow': 'rgba(255, 69, 58, 0.4)'},
        }
        
        config = btn_config.get(button_type, btn_config['primary'])
        
        html = f"""
        <button id="{btn_id}" class="apple-button" style="
            background: {config['bg']};
            color: white;
            border: none;
            border-radius: 980px;
            padding: 14px 32px;
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.022em;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 
                0 4px 14px {config['shadow']},
                inset 0 -2px 0 rgba(0, 0, 0, 0.1);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        ">
            <span class="ripple-container" style="
                position: absolute;
                inset: 0;
                overflow: hidden;
                pointer-events: none;
                border-radius: 980px;
            "></span>
            
            <span style="position: relative; z-index: 1; display: flex; align-items: center; gap: 8px;">
        """
        
        if icon:
            html += f'<span style="font-size: 20px;">{icon}</span>'
        
        html += f"""
                <span>{text}</span>
            </span>
        </button>
        
        <style>
        .apple-button:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 
                0 8px 24px {config['shadow']},
                inset 0 -2px 0 rgba(0, 0, 0, 0.15);
            background: {config['hover']};
        }}
        
        .apple-button:active {{
            transform: translateY(0) scale(0.98);
            box-shadow: 
                0 2px 8px {config['shadow']},
                inset 0 2px 0 rgba(0, 0, 0, 0.1);
        }}
        
        /* Ripple波纹动画 */
        .ripple {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            transform: scale(0);
            animation: rippleEffect 0.6s ease-out;
            pointer-events: none;
        }}
        
        @keyframes rippleEffect {{
            to {{
                transform: scale(4);
                opacity: 0;
            }}
        }}
        </style>
        
        <script>
        (function() {{
            const button = document.getElementById('{btn_id}');
            if (!button) return;
            
            button.addEventListener('click', function(e) {{
                // Ripple效果
                const rippleContainer = this.querySelector('.ripple-container');
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                rippleContainer.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
                
                // 自定义点击事件
                {onclick if onclick else ''}
            }});
        }})();
        </script>
        """
        
        components.html(html, height=70, scrolling=False)
    
    @staticmethod
    def alert_box(
        message: str,
        type: str = 'info',
        dismissible: bool = False
    ):
        """
        警告框组件
        
        Args:
            message: 消息内容
            type: 类型 ('success', 'warning', 'danger', 'info')
            dismissible: 是否可关闭
        """
        config = {
            'success': {'icon': '✅', 'color': '#34C759', 'bg': 'rgba(52, 199, 89, 0.1)'},
            'warning': {'icon': '⚠️', 'color': '#FF9500', 'bg': 'rgba(255, 149, 0, 0.1)'},
            'danger': {'icon': '❌', 'color': '#FF3B30', 'bg': 'rgba(255, 59, 48, 0.1)'},
            'info': {'icon': 'ℹ️', 'color': '#007AFF', 'bg': 'rgba(0, 122, 255, 0.1)'}
        }
        
        cfg = config.get(type, config['info'])
        
        html = f"""
        <div class="modern-card" style="background: {cfg['bg']}; border-left: 4px solid {cfg['color']};">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">{cfg['icon']}</div>
                <div style="flex: 1; font-size: 14px; color: var(--text-primary);">
                    {message}
                </div>
            </div>
        </div>
        """
        
        components.html(html, height=80, scrolling=False)


# 使用示例
if __name__ == "__main__":
    st.set_page_config(page_title="Modern Components", layout="wide")
    
    from modern_theme import ModernTheme
    ModernTheme.apply_theme()
    
    ModernTheme.create_hero_section("现代化组件库", "高级可复用UI组件")
    
    # 价格卡片示例
    st.subheader("价格卡片")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ModernComponents.price_card(
            "BTC", "Bitcoin", 113655.00, 2.5, 
            volume_24h=45000000000, market_cap=2200000000000, icon="₿"
        )
    
    with col2:
        ModernComponents.price_card(
            "ETH", "Ethereum", 4073.53, -1.2,
            volume_24h=20000000000, market_cap=490000000000, icon="Ξ"
        )
    
    with col3:
        ModernComponents.signal_indicator(
            "买入", 85,
            {'MA信号': '买入', 'MACD': '金叉', 'RSI': '46.3', 'KDJ': '中性'}
        )

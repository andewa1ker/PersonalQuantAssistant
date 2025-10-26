"""
简约线性图标系统
参考Phosphor Icons / Lucide Icons风格
"""


class MinimalIcons:
    """简约线性图标库"""
    
    # 使用Unicode符号创建简约图标
    ICONS = {
        # 加密货币
        'bitcoin': '₿',
        'ethereum': 'Ξ',
        'crypto': '◈',
        'coin': '○',
        
        # 金融
        'chart_up': '↗',
        'chart_down': '↘',
        'chart_line': '─',
        'trending_up': '⟋',
        'trending_down': '⟍',
        'percent': '%',
        'dollar': '$',
        
        # 交易信号
        'buy': '⬆',
        'sell': '⬇',
        'hold': '⊡',
        'wait': '⊙',
        'signal': '◉',
        
        # 指标
        'target': '◎',
        'gauge': '◐',
        'meter': '◑',
        'pulse': '〰',
        
        # 导航
        'home': '⌂',
        'dashboard': '▦',
        'grid': '⊞',
        'list': '≡',
        'menu': '☰',
        
        # 功能
        'settings': '⚙',
        'filter': '⊙',
        'search': '⌕',
        'bell': '◎',
        'star': '☆',
        'check': '✓',
        'cross': '✕',
        'info': 'ⓘ',
        'warning': '⚠',
        'alert': '⚡',
        
        # 时间
        'clock': '◷',
        'calendar': '☷',
        'history': '◴',
        
        # 数据
        'database': '⊞',
        'server': '⊟',
        'cloud': '☁',
        
        # 用户
        'user': '◯',
        'users': '◎',
        'profile': '⊙',
        
        # 方向
        'arrow_up': '↑',
        'arrow_down': '↓',
        'arrow_right': '→',
        'arrow_left': '←',
        'caret_up': '▴',
        'caret_down': '▾',
        
        # 形状
        'circle': '○',
        'circle_filled': '●',
        'square': '□',
        'square_filled': '■',
        'diamond': '◇',
        'diamond_filled': '◆',
        
        # AI/机器人
        'robot': '⚛',
        'ai': '⚡',
        'brain': '◉',
        
        # 组合
        'portfolio': '▦',
        'wallet': '▭',
        'money': '◈',
    }
    
    @staticmethod
    def get(name: str, fallback: str = '○') -> str:
        """
        获取图标
        
        Args:
            name: 图标名称
            fallback: 备用图标
        
        Returns:
            图标字符
        """
        return MinimalIcons.ICONS.get(name, fallback)
    
    @staticmethod
    def with_style(icon_name: str, size: int = 24, color: str = '#F5F5F7') -> str:
        """
        返回带样式的图标HTML
        
        Args:
            icon_name: 图标名称
            size: 图标大小(px)
            color: 图标颜色
        
        Returns:
            HTML字符串
        """
        icon = MinimalIcons.get(icon_name)
        return f'''
        <span style="
            font-size: {size}px;
            color: {color};
            line-height: 1;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            display: inline-block;
            vertical-align: middle;
        ">{icon}</span>
        '''
    
    @staticmethod
    def animated(icon_name: str, animation: str = 'pulse') -> str:
        """
        返回带动画的图标HTML
        
        Args:
            icon_name: 图标名称
            animation: 动画类型 ('pulse', 'spin', 'bounce')
        
        Returns:
            HTML字符串
        """
        icon = MinimalIcons.get(icon_name)
        
        animations = {
            'pulse': '''
            @keyframes iconPulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.1); }
            }
            ''',
            'spin': '''
            @keyframes iconSpin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            ''',
            'bounce': '''
            @keyframes iconBounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-4px); }
            }
            '''
        }
        
        return f'''
        <style>{animations.get(animation, '')}</style>
        <span style="
            display: inline-block;
            animation: icon{animation.capitalize()} 2s ease-in-out infinite;
        ">{icon}</span>
        '''


# SVG图标库 - 用于更复杂的图标需求
class SVGIcons:
    """SVG线性图标"""
    
    @staticmethod
    def chart_line(width=24, height=24, color='currentColor'):
        """折线图图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 17 9 11 13 15 21 7"></polyline>
            <polyline points="14 7 21 7 21 14"></polyline>
        </svg>
        '''
    
    @staticmethod
    def trending_up(width=24, height=24, color='currentColor'):
        """上升趋势图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
        '''
    
    @staticmethod
    def activity(width=24, height=24, color='currentColor'):
        """活动/波动图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        '''
    
    @staticmethod
    def circle_signal(width=24, height=24, color='currentColor'):
        """圆形信号图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <circle cx="12" cy="12" r="6" fill="{color}" opacity="0.3"></circle>
            <circle cx="12" cy="12" r="2" fill="{color}"></circle>
        </svg>
        '''
    
    @staticmethod
    def wallet(width=24, height=24, color='currentColor'):
        """钱包图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
            <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
            <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path>
        </svg>
        '''
    
    @staticmethod
    def brain(width=24, height=24, color='currentColor'):
        """AI大脑图标"""
        return f'''
        <svg width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path>
            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path>
        </svg>
        '''


if __name__ == "__main__":
    # 测试图标
    print("=== 简约图标系统 ===")
    print(f"Bitcoin: {MinimalIcons.get('bitcoin')}")
    print(f"Trending Up: {MinimalIcons.get('trending_up')}")
    print(f"Signal: {MinimalIcons.get('signal')}")
    print(f"Dashboard: {MinimalIcons.get('dashboard')}")
    print(f"AI: {MinimalIcons.get('ai')}")

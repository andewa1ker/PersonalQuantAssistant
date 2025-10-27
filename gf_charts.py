"""
Google Finance 图表配置
提供 Plotly 图表的 Google 风格预设
"""
import plotly.graph_objects as go
from design_system_google import GOOGLE_COLORS, TYPOGRAPHY


def get_google_chart_layout(title: str = None, height: int = 400):
    """
    获取 Google Finance 风格的 Plotly 布局配置
    
    特点:
    - 无边框
    - 白色背景
    - 浅灰网格线 (#F1F3F4)
    - Roboto 字体
    - 极简设计
    """
    layout = {
        'plot_bgcolor': GOOGLE_COLORS['bg_primary'],
        'paper_bgcolor': GOOGLE_COLORS['bg_primary'],
        'height': height,
        'margin': {'l': 60, 'r': 20, 't': 40 if title else 20, 'b': 40},
        'font': {
            'family': TYPOGRAPHY['family'],
            'size': 12,
            'color': GOOGLE_COLORS['text_primary']
        },
        'hoverlabel': {
            'bgcolor': GOOGLE_COLORS['bg_primary'],
            'bordercolor': GOOGLE_COLORS['border'],
            'font': {
                'family': TYPOGRAPHY['family'],
                'size': 12,
                'color': GOOGLE_COLORS['text_primary']
            }
        },
        'xaxis': {
            'gridcolor': GOOGLE_COLORS['bg_secondary'],
            'linecolor': GOOGLE_COLORS['border'],
            'linewidth': 1,
            'showgrid': True,
            'zeroline': False,
            'tickfont': {
                'size': 11,
                'color': GOOGLE_COLORS['text_secondary']
            }
        },
        'yaxis': {
            'gridcolor': GOOGLE_COLORS['bg_secondary'],
            'linecolor': GOOGLE_COLORS['border'],
            'linewidth': 1,
            'showgrid': True,
            'zeroline': False,
            'tickfont': {
                'size': 11,
                'color': GOOGLE_COLORS['text_secondary']
            }
        }
    }
    
    if title:
        layout['title'] = {
            'text': title,
            'font': {
                'size': 16,
                'color': GOOGLE_COLORS['text_primary'],
                'family': TYPOGRAPHY['family']
            },
            'x': 0,
            'xanchor': 'left'
        }
    
    return layout


def create_line_chart(x, y, color=None, fill=False, title=None, height=400):
    """
    创建 Google Finance 风格折线图
    
    参数:
        x: X轴数据
        y: Y轴数据
        color: 线条颜色 (默认蓝色)
        fill: 是否填充区域
        title: 图表标题
        height: 高度
    """
    if color is None:
        color = GOOGLE_COLORS['blue']
    
    fig = go.Figure()
    
    trace_args = {
        'x': x,
        'y': y,
        'mode': 'lines',
        'line': {
            'color': color,
            'width': 2
        },
        'hovertemplate': '<b>%{y:.2f}</b><br>%{x}<extra></extra>'
    }
    
    if fill:
        trace_args['fill'] = 'tozeroy'
        trace_args['fillcolor'] = f'rgba{_hex_to_rgba(color, 0.1)}'
    
    fig.add_trace(go.Scatter(**trace_args))
    
    fig.update_layout(**get_google_chart_layout(title, height))
    
    return fig


def create_candlestick_chart(df, title=None, height=400):
    """
    创建 K线图 (Google Finance 风格)
    
    参数:
        df: 包含 open, high, low, close 列的 DataFrame
        title: 图表标题
        height: 高度
    """
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color=GOOGLE_COLORS['green'],
            decreasing_line_color=GOOGLE_COLORS['red'],
            increasing_fillcolor=GOOGLE_COLORS['green'],
            decreasing_fillcolor=GOOGLE_COLORS['red'],
            hovertemplate='<b>%{x}</b><br>' +
                          'Open: %{open:.2f}<br>' +
                          'High: %{high:.2f}<br>' +
                          'Low: %{low:.2f}<br>' +
                          'Close: %{close:.2f}<extra></extra>'
        )
    ])
    
    layout = get_google_chart_layout(title, height)
    # K线图不显示网格线
    layout['xaxis']['showgrid'] = False
    layout['yaxis']['showgrid'] = True
    
    fig.update_layout(**layout)
    
    return fig


def create_bar_chart(x, y, color=None, horizontal=False, title=None, height=400):
    """
    创建柱状图 (Google Finance 风格)
    
    参数:
        x: X轴数据
        y: Y轴数据
        color: 柱子颜色 (默认蓝色)
        horizontal: 是否水平显示
        title: 图表标题
        height: 高度
    """
    if color is None:
        color = GOOGLE_COLORS['blue']
    
    fig = go.Figure()
    
    if horizontal:
        fig.add_trace(go.Bar(
            y=x,
            x=y,
            orientation='h',
            marker_color=color,
            hovertemplate='<b>%{y}</b>: %{x:.2f}<extra></extra>'
        ))
    else:
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            marker_color=color,
            hovertemplate='<b>%{x}</b>: %{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(**get_google_chart_layout(title, height))
    
    return fig


def create_pie_chart(labels, values, colors=None, title=None, height=400):
    """
    创建饼图 (Google Finance 风格)
    
    参数:
        labels: 标签列表
        values: 数值列表
        colors: 颜色列表 (默认使用 Google 配色)
        title: 图表标题
        height: 高度
    """
    if colors is None:
        colors = [
            GOOGLE_COLORS['blue'],
            GOOGLE_COLORS['green'],
            GOOGLE_COLORS['orange'],
            GOOGLE_COLORS['red'],
            GOOGLE_COLORS['purple'],
            GOOGLE_COLORS['teal'],
        ]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker={'colors': colors},
            textfont={'size': 12, 'family': TYPOGRAPHY['family']},
            hovertemplate='<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>',
            hole=0.3  # 甜甜圈效果
        )
    ])
    
    layout = get_google_chart_layout(title, height)
    layout['showlegend'] = True
    layout['legend'] = {
        'orientation': 'v',
        'x': 1.02,
        'y': 0.5,
        'font': {
            'size': 12,
            'color': GOOGLE_COLORS['text_secondary']
        }
    }
    
    fig.update_layout(**layout)
    
    return fig


def create_scatter_chart(x, y, size=None, color=None, title=None, height=400):
    """
    创建散点图 (Google Finance 风格)
    
    参数:
        x: X轴数据
        y: Y轴数据
        size: 点大小 (可选)
        color: 点颜色 (默认蓝色)
        title: 图表标题
        height: 高度
    """
    if color is None:
        color = GOOGLE_COLORS['blue']
    
    fig = go.Figure()
    
    trace_args = {
        'x': x,
        'y': y,
        'mode': 'markers',
        'marker': {
            'color': color,
            'size': size if size is not None else 8,
            'opacity': 0.7,
            'line': {'width': 0}
        },
        'hovertemplate': '<b>X: %{x:.2f}</b><br>Y: %{y:.2f}<extra></extra>'
    }
    
    fig.add_trace(go.Scatter(**trace_args))
    
    fig.update_layout(**get_google_chart_layout(title, height))
    
    return fig


def create_area_chart(x, y_data_dict, title=None, height=400):
    """
    创建堆叠面积图 (Google Finance 风格)
    
    参数:
        x: X轴数据
        y_data_dict: {'系列1': y1, '系列2': y2, ...}
        title: 图表标题
        height: 高度
    """
    fig = go.Figure()
    
    colors = [
        GOOGLE_COLORS['blue'],
        GOOGLE_COLORS['green'],
        GOOGLE_COLORS['orange'],
        GOOGLE_COLORS['red'],
        GOOGLE_COLORS['purple'],
    ]
    
    for i, (name, y) in enumerate(y_data_dict.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=name,
            stackgroup='one',
            line={'width': 0},
            fillcolor=f'rgba{_hex_to_rgba(color, 0.5)}',
            hovertemplate=f'<b>{name}</b><br>%{{y:.2f}}<extra></extra>'
        ))
    
    layout = get_google_chart_layout(title, height)
    layout['showlegend'] = True
    layout['legend'] = {
        'orientation': 'h',
        'x': 0,
        'y': 1.1,
        'font': {'size': 12, 'color': GOOGLE_COLORS['text_secondary']}
    }
    
    fig.update_layout(**layout)
    
    
    return fig


def create_heatmap(z, x=None, y=None, colorscale=None, title=None, height=400):
    """
    创建热力图 (Google Finance 风格)
    
    参数:
        z: 二维数据
        x: X轴标签
        y: Y轴标签
        colorscale: 颜色映射
        title: 图表标题
        height: 高度
    """
    if colorscale is None:
        # 蓝白红配色
        colorscale = [
            [0, GOOGLE_COLORS['red']],
            [0.5, '#FFFFFF'],
            [1, GOOGLE_COLORS['blue']]
        ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=colorscale,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Value: %{z:.2f}<extra></extra>'
    ))
    
    layout = get_google_chart_layout(title, height)
    layout['xaxis']['showgrid'] = False
    layout['yaxis']['showgrid'] = False
    
    fig.update_layout(**layout)
    
    return fig


def _hex_to_rgba(hex_color, alpha):
    """将 hex 颜色转为 rgba 元组字符串"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"({r}, {g}, {b}, {alpha})"


# 常用颜色预设
CHART_COLORS = {
    'positive': GOOGLE_COLORS['green'],
    'negative': GOOGLE_COLORS['red'],
    'neutral': GOOGLE_COLORS['blue'],
    'warning': GOOGLE_COLORS['orange'],
}

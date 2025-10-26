"""
策略可视化增强模块
添加策略对比图表、回测结果可视化、收益曲线
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from loguru import logger


def show_strategy_comparison(strategies_results):
    """显示策略对比图表"""
    st.markdown("### 📊 策略对比分析")
    
    if not strategies_results or len(strategies_results) < 2:
        st.info("💡 需要至少2个策略结果才能进行对比")
        return
    
    # 提取策略指标
    strategy_names = [s['name'] for s in strategies_results]
    total_returns = [s['total_return'] for s in strategies_results]
    sharpe_ratios = [s.get('sharpe_ratio', 0) for s in strategies_results]
    max_drawdowns = [abs(s.get('max_drawdown', 0)) for s in strategies_results]
    win_rates = [s.get('win_rate', 0) * 100 for s in strategies_results]
    
    # 创建对比图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 总收益率对比
        fig = go.Figure(data=[
            go.Bar(
                x=strategy_names,
                y=[r * 100 for r in total_returns],
                text=[f"{r*100:.2f}%" for r in total_returns],
                textposition='outside',
                marker_color=['green' if r > 0 else 'red' for r in total_returns]
            )
        ])
        
        fig.update_layout(
            title="总收益率对比",
            xaxis_title="策略",
            yaxis_title="收益率(%)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 夏普比率对比
        fig = go.Figure(data=[
            go.Bar(
                x=strategy_names,
                y=sharpe_ratios,
                text=[f"{sr:.2f}" for sr in sharpe_ratios],
                textposition='outside',
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title="夏普比率对比",
            xaxis_title="策略",
            yaxis_title="夏普比率",
            height=300
        )
        
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="良好水平")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 雷达图对比
    st.markdown("#### 📡 综合表现雷达图")
    
    # 归一化指标（0-100）
    categories = ['收益率', '夏普比率', '胜率', '最大回撤(反向)']
    
    fig = go.Figure()
    
    for i, strategy in enumerate(strategies_results[:5]):  # 最多5个策略
        # 归一化处理
        normalized_return = min(max((strategy['total_return'] + 0.5) * 100, 0), 100)
        normalized_sharpe = min(max(strategy.get('sharpe_ratio', 0) * 50, 0), 100)
        normalized_winrate = strategy.get('win_rate', 0) * 100
        normalized_drawdown = min(max(100 - abs(strategy.get('max_drawdown', 0)) * 200, 0), 100)
        
        values = [
            normalized_return,
            normalized_sharpe,
            normalized_winrate,
            normalized_drawdown
        ]
        values.append(values[0])  # 闭合
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=strategy['name']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_backtest_visualization(backtest_result):
    """显示回测结果可视化"""
    st.markdown("### 📈 回测结果可视化")
    
    if not backtest_result or 'equity_curve' not in backtest_result:
        st.info("💡 暂无回测数据")
        return
    
    equity_curve = backtest_result['equity_curve']
    trades = backtest_result.get('trades', [])
    benchmark = backtest_result.get('benchmark', None)
    
    # 创建子图
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('权益曲线', '回撤曲线', '每日收益分布'),
        vertical_spacing=0.08
    )
    
    # 1. 权益曲线
    fig.add_trace(
        go.Scatter(
            x=equity_curve.index,
            y=equity_curve['equity'],
            name='策略权益',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # 基准对比
    if benchmark is not None:
        fig.add_trace(
            go.Scatter(
                x=benchmark.index,
                y=benchmark['equity'],
                name='基准',
                line=dict(color='gray', width=1, dash='dash')
            ),
            row=1, col=1
        )
    
    # 标记买卖点
    if trades:
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        if buy_trades:
            fig.add_trace(
                go.Scatter(
                    x=[t['date'] for t in buy_trades],
                    y=[t['equity'] for t in buy_trades],
                    mode='markers',
                    name='买入',
                    marker=dict(color='green', size=8, symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        if sell_trades:
            fig.add_trace(
                go.Scatter(
                    x=[t['date'] for t in sell_trades],
                    y=[t['equity'] for t in sell_trades],
                    mode='markers',
                    name='卖出',
                    marker=dict(color='red', size=8, symbol='triangle-down')
                ),
                row=1, col=1
            )
    
    # 2. 回撤曲线
    drawdown = calculate_drawdown(equity_curve['equity'])
    
    fig.add_trace(
        go.Scatter(
            x=equity_curve.index,
            y=drawdown * 100,
            name='回撤',
            fill='tozeroy',
            line=dict(color='red')
        ),
        row=2, col=1
    )
    
    # 3. 每日收益分布
    if len(equity_curve) > 1:
        daily_returns = equity_curve['equity'].pct_change().dropna() * 100
        
        fig.add_trace(
            go.Histogram(
                x=daily_returns,
                name='每日收益',
                nbinsx=50,
                marker_color='lightblue'
            ),
            row=3, col=1
        )
    
    # 更新布局
    fig.update_layout(
        height=900,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="时间", row=3, col=1)
    fig.update_yaxes(title_text="权益", row=1, col=1)
    fig.update_yaxes(title_text="回撤(%)", row=2, col=1)
    fig.update_yaxes(title_text="频数", row=3, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 回测统计指标
    show_backtest_statistics(backtest_result)


def show_backtest_statistics(backtest_result):
    """显示回测统计指标"""
    st.markdown("#### 📊 回测统计")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_return = backtest_result.get('total_return', 0) * 100
        st.metric("总收益率", f"{total_return:.2f}%")
        
        annual_return = backtest_result.get('annual_return', 0) * 100
        st.metric("年化收益", f"{annual_return:.2f}%")
    
    with col2:
        sharpe = backtest_result.get('sharpe_ratio', 0)
        st.metric("夏普比率", f"{sharpe:.2f}")
        
        sortino = backtest_result.get('sortino_ratio', 0)
        st.metric("索提诺比率", f"{sortino:.2f}")
    
    with col3:
        max_dd = backtest_result.get('max_drawdown', 0) * 100
        st.metric("最大回撤", f"{abs(max_dd):.2f}%", delta_color="inverse")
        
        calmar = backtest_result.get('calmar_ratio', 0)
        st.metric("卡玛比率", f"{calmar:.2f}")
    
    with col4:
        win_rate = backtest_result.get('win_rate', 0) * 100
        st.metric("胜率", f"{win_rate:.1f}%")
        
        profit_factor = backtest_result.get('profit_factor', 0)
        st.metric("盈亏比", f"{profit_factor:.2f}")


def show_returns_curve(equity_curve, strategy_name="策略"):
    """显示收益曲线"""
    st.markdown(f"### 📈 {strategy_name} 收益曲线")
    
    if equity_curve is None or len(equity_curve) == 0:
        st.info("💡 暂无收益数据")
        return
    
    # 计算累计收益率
    initial_equity = equity_curve['equity'].iloc[0]
    cumulative_returns = (equity_curve['equity'] / initial_equity - 1) * 100
    
    # 创建图表
    fig = go.Figure()
    
    # 收益曲线
    fig.add_trace(go.Scatter(
        x=equity_curve.index,
        y=cumulative_returns,
        name='累计收益',
        fill='tozeroy',
        line=dict(color='blue', width=2)
    ))
    
    # 添加零线
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # 标注关键点
    max_return = cumulative_returns.max()
    max_return_date = cumulative_returns.idxmax()
    
    fig.add_annotation(
        x=max_return_date,
        y=max_return,
        text=f"最高: {max_return:.2f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        ax=0,
        ay=-40
    )
    
    if cumulative_returns.min() < 0:
        min_return = cumulative_returns.min()
        min_return_date = cumulative_returns.idxmin()
        
        fig.add_annotation(
            x=min_return_date,
            y=min_return,
            text=f"最低: {min_return:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            ax=0,
            ay=40
        )
    
    fig.update_layout(
        title=f"{strategy_name} 累计收益率",
        xaxis_title="时间",
        yaxis_title="收益率(%)",
        height=400,
        hovermode='x'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 收益统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("起始", f"{cumulative_returns.iloc[0]:.2f}%")
    
    with col2:
        st.metric("当前", f"{cumulative_returns.iloc[-1]:.2f}%")
    
    with col3:
        st.metric("最高", f"{max_return:.2f}%")
    
    with col4:
        st.metric("最低", f"{cumulative_returns.min():.2f}%")


def show_monthly_returns_heatmap(equity_curve):
    """显示月度收益热力图"""
    st.markdown("### 🔥 月度收益热力图")
    
    if equity_curve is None or len(equity_curve) == 0:
        st.info("💡 暂无月度数据")
        return
    
    # 计算月度收益
    equity_curve_copy = equity_curve.copy()
    equity_curve_copy['year'] = equity_curve_copy.index.year
    equity_curve_copy['month'] = equity_curve_copy.index.month
    
    monthly_returns = equity_curve_copy.groupby(['year', 'month'])['equity'].apply(
        lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100 if len(x) > 0 else 0
    ).reset_index()
    
    # 创建数据透视表
    pivot_table = monthly_returns.pivot(index='year', columns='month', values='equity')
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=[f"{m}月" for m in pivot_table.columns],
        y=pivot_table.index,
        colorscale='RdYlGn',
        zmid=0,
        text=pivot_table.values.round(2),
        texttemplate='%{text}%',
        textfont={"size": 10},
        colorbar=dict(title="收益率(%)")
    ))
    
    fig.update_layout(
        title="月度收益率热力图",
        xaxis_title="月份",
        yaxis_title="年份",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def calculate_drawdown(equity_series):
    """计算回撤"""
    cummax = equity_series.cummax()
    drawdown = (equity_series - cummax) / cummax
    return drawdown


def generate_mock_equity_curve(days=365, initial_capital=100000, trend='up'):
    """生成模拟权益曲线"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成随机收益
    np.random.seed(42)
    
    if trend == 'up':
        daily_returns = np.random.normal(0.0008, 0.02, days)  # 上升趋势
    elif trend == 'down':
        daily_returns = np.random.normal(-0.0005, 0.02, days)  # 下降趋势
    else:
        daily_returns = np.random.normal(0.0003, 0.015, days)  # 震荡
    
    equity = initial_capital * (1 + daily_returns).cumprod()
    
    df = pd.DataFrame({
        'equity': equity
    }, index=dates)
    
    return df


def show_strategy_performance_matrix(strategies_results):
    """显示策略表现矩阵"""
    st.markdown("### 📊 策略表现矩阵")
    
    if not strategies_results:
        st.info("💡 暂无策略结果")
        return
    
    # 创建表现矩阵数据
    matrix_data = []
    
    for strategy in strategies_results:
        matrix_data.append({
            '策略': strategy['name'],
            '总收益': f"{strategy['total_return']*100:.2f}%",
            '年化收益': f"{strategy.get('annual_return', 0)*100:.2f}%",
            '夏普比率': f"{strategy.get('sharpe_ratio', 0):.2f}",
            '最大回撤': f"{abs(strategy.get('max_drawdown', 0))*100:.2f}%",
            '胜率': f"{strategy.get('win_rate', 0)*100:.1f}%",
            '交易次数': strategy.get('total_trades', 0),
            '评级': rate_strategy(strategy)
        })
    
    df = pd.DataFrame(matrix_data)
    
    # 颜色编码
    def color_rating(val):
        if val == 'A':
            return 'background-color: #d4edda'
        elif val == 'B':
            return 'background-color: #d1ecf1'
        elif val == 'C':
            return 'background-color: #fff3cd'
        elif val == 'D':
            return 'background-color: #f8d7da'
        return ''
    
    styled_df = df.style.applymap(color_rating, subset=['评级'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def rate_strategy(strategy):
    """评级策略"""
    score = 0
    
    # 收益率评分
    if strategy['total_return'] > 0.3:
        score += 4
    elif strategy['total_return'] > 0.15:
        score += 3
    elif strategy['total_return'] > 0.05:
        score += 2
    elif strategy['total_return'] > 0:
        score += 1
    
    # 夏普比率评分
    sharpe = strategy.get('sharpe_ratio', 0)
    if sharpe > 2:
        score += 4
    elif sharpe > 1:
        score += 3
    elif sharpe > 0.5:
        score += 2
    elif sharpe > 0:
        score += 1
    
    # 回撤评分
    max_dd = abs(strategy.get('max_drawdown', 0))
    if max_dd < 0.05:
        score += 3
    elif max_dd < 0.15:
        score += 2
    elif max_dd < 0.25:
        score += 1
    
    # 综合评级
    if score >= 9:
        return 'A'
    elif score >= 6:
        return 'B'
    elif score >= 3:
        return 'C'
    else:
        return 'D'


def show_trade_analysis(trades):
    """显示交易分析"""
    st.markdown("### 📋 交易分析")
    
    if not trades or len(trades) == 0:
        st.info("💡 暂无交易记录")
        return
    
    trades_df = pd.DataFrame(trades)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 盈亏分布
        st.markdown("#### 盈亏分布")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=trades_df['pnl'],
            nbinsx=30,
            marker_color='lightgreen',
            name='盈亏分布'
        ))
        
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        
        fig.update_layout(
            xaxis_title="盈亏",
            yaxis_title="交易次数",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 累计盈亏
        st.markdown("#### 累计盈亏")
        
        cumulative_pnl = trades_df['pnl'].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(cumulative_pnl))),
            y=cumulative_pnl,
            mode='lines+markers',
            line=dict(color='blue'),
            name='累计盈亏'
        ))
        
        fig.update_layout(
            xaxis_title="交易序号",
            yaxis_title="累计盈亏",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

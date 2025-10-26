"""
风险管理增强可视化模块
提供多维度风险分析、蒙特卡洛模拟、历史趋势等专业可视化
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_risk_enhanced(data_manager, config):
    """风险管理增强主入口"""
    st.header("⚠️ 风险管理中心 (专业版)")
    
    # 视图模式选择
    view_mode = st.radio(
        "视图模式",
        ["风险总览", "蒙特卡洛模拟", "历史趋势", "组合风险"],
        horizontal=True,
        key="risk_view_mode"
    )
    
    if view_mode == "风险总览":
        show_risk_overview(data_manager, config)
    elif view_mode == "蒙特卡洛模拟":
        show_monte_carlo_simulation(data_manager, config)
    elif view_mode == "历史趋势":
        show_historical_risk_trends(data_manager, config)
    else:  # 组合风险
        show_portfolio_risk(data_manager, config)


def show_risk_overview(data_manager, config):
    """显示风险总览"""
    st.subheader("📊 风险总览")
    
    # 资产选择
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="risk_asset")
    with col2:
        period = st.selectbox("周期", ["1M", "3M", "6M", "1Y", "3Y"], index=3, key="risk_period")
    with col3:
        confidence = st.selectbox("VaR置信度", [0.90, 0.95, 0.99], index=1, key="risk_confidence")
    
    if st.button("🔍 分析风险", key="analyze_risk_btn"):
        with st.spinner("正在计算风险指标..."):
            # 生成模拟数据
            risk_data = generate_mock_risk_data(asset_code, period)
            
            # 显示风险雷达图
            st.markdown("### 📡 风险雷达图")
            show_risk_radar(risk_data)
            
            # 显示关键指标
            st.markdown("### 📈 关键风险指标")
            show_risk_metrics_cards(risk_data)
            
            # VaR/CVaR分布
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 收益率分布与VaR")
                show_var_distribution(risk_data, confidence)
            
            with col2:
                st.markdown("### 📉 回撤分析")
                show_drawdown_analysis(risk_data)


def show_risk_radar(risk_data: Dict):
    """显示风险雷达图
    
    Args:
        risk_data: 风险数据字典
    """
    # 风险维度和评分
    dimensions = ['波动风险', '流动性风险', '回撤风险', '尾部风险', '集中度风险']
    scores = [
        risk_data.get('volatility_score', 70),
        risk_data.get('liquidity_score', 80),
        risk_data.get('drawdown_score', 65),
        risk_data.get('tail_risk_score', 75),
        risk_data.get('concentration_score', 85)
    ]
    
    # 创建雷达图
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=dimensions,
        fill='toself',
        name='当前风险',
        fillcolor='rgba(255, 99, 71, 0.3)',
        line=dict(color='rgb(255, 99, 71)', width=2)
    ))
    
    # 添加安全基准线
    safe_scores = [50] * len(dimensions)
    fig.add_trace(go.Scatterpolar(
        r=safe_scores,
        theta=dimensions,
        fill='toself',
        name='安全基准',
        fillcolor='rgba(46, 204, 113, 0.1)',
        line=dict(color='rgb(46, 204, 113)', width=1, dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            )
        ),
        showlegend=True,
        title="多维度风险评估 (分数越高风险越大)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 风险评级说明
    avg_score = np.mean(scores)
    if avg_score < 40:
        risk_level = "🟢 低风险"
        risk_color = "green"
    elif avg_score < 60:
        risk_level = "🟡 中等风险"
        risk_color = "orange"
    elif avg_score < 80:
        risk_level = "🟠 高风险"
        risk_color = "darkorange"
    else:
        risk_level = "🔴 极高风险"
        risk_color = "red"
    
    st.markdown(f"**综合风险评级**: :{risk_color}[{risk_level}] (平均分: {avg_score:.1f}/100)")


def show_risk_metrics_cards(risk_data: Dict):
    """显示风险指标卡片"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "波动率 (年化)",
            f"{risk_data.get('volatility', 0.25):.2%}",
            delta=f"{risk_data.get('volatility_change', -0.02):.2%}",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "最大回撤",
            f"{risk_data.get('max_drawdown', -0.18):.2%}",
            delta=f"{risk_data.get('drawdown_change', 0.03):.2%}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "VaR (95%)",
            f"{risk_data.get('var_95', -0.025):.2%}",
            delta=None
        )
    
    with col4:
        st.metric(
            "CVaR (95%)",
            f"{risk_data.get('cvar_95', -0.032):.2%}",
            delta=None
        )
    
    with col5:
        st.metric(
            "夏普比率",
            f"{risk_data.get('sharpe_ratio', 1.2):.2f}",
            delta=f"{risk_data.get('sharpe_change', 0.1):.2f}"
        )


def show_var_distribution(risk_data: Dict, confidence: float):
    """显示VaR分布图
    
    Args:
        risk_data: 风险数据
        confidence: 置信水平
    """
    # 生成收益率分布
    returns = risk_data.get('returns', np.random.normal(0.001, 0.02, 250))
    
    # 计算VaR和CVaR
    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    
    # 创建直方图
    fig = go.Figure()
    
    # 收益率直方图
    fig.add_trace(go.Histogram(
        x=returns * 100,
        nbinsx=50,
        name='收益率分布',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    # 添加VaR线
    fig.add_vline(
        x=var * 100,
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR({confidence:.0%}) = {var:.2%}",
        annotation_position="top"
    )
    
    # 添加CVaR线
    fig.add_vline(
        x=cvar * 100,
        line_dash="dot",
        line_color="darkred",
        annotation_text=f"CVaR = {cvar:.2%}",
        annotation_position="bottom"
    )
    
    # 添加均值线
    mean_return = np.mean(returns)
    fig.add_vline(
        x=mean_return * 100,
        line_dash="dash",
        line_color="green",
        annotation_text=f"均值 = {mean_return:.2%}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title=f"收益率分布与风险指标 (置信度 {confidence:.0%})",
        xaxis_title="日收益率 (%)",
        yaxis_title="频数",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 统计信息
    with st.expander("📊 详细统计"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**均值**: {np.mean(returns):.2%}")
            st.write(f"**标准差**: {np.std(returns):.2%}")
        with col2:
            st.write(f"**偏度**: {pd.Series(returns).skew():.2f}")
            st.write(f"**峰度**: {pd.Series(returns).kurtosis():.2f}")
        with col3:
            st.write(f"**最大值**: {np.max(returns):.2%}")
            st.write(f"**最小值**: {np.min(returns):.2%}")


def show_drawdown_analysis(risk_data: Dict):
    """显示回撤分析
    
    Args:
        risk_data: 风险数据
    """
    # 生成权益曲线和回撤
    equity_curve = risk_data.get('equity_curve', None)
    if equity_curve is None:
        # 生成模拟数据
        dates = pd.date_range(end=datetime.now(), periods=250, freq='D')
        returns = np.random.normal(0.0005, 0.015, 250)
        equity_curve = (1 + pd.Series(returns)).cumprod()
    
    # 计算回撤
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    
    # 创建双轴图
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.6, 0.4],
        subplot_titles=("权益曲线", "回撤曲线"),
        vertical_spacing=0.1
    )
    
    # 权益曲线
    fig.add_trace(
        go.Scatter(
            x=list(range(len(equity_curve))),
            y=equity_curve,
            name='权益',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # 历史最高点
    fig.add_trace(
        go.Scatter(
            x=list(range(len(cummax))),
            y=cummax,
            name='历史最高',
            line=dict(color='green', width=1, dash='dash'),
            opacity=0.5
        ),
        row=1, col=1
    )
    
    # 回撤曲线
    fig.add_trace(
        go.Scatter(
            x=list(range(len(drawdown))),
            y=drawdown * 100,
            name='回撤',
            fill='tozeroy',
            line=dict(color='red', width=1),
            fillcolor='rgba(255, 0, 0, 0.3)'
        ),
        row=2, col=1
    )
    
    # 标记最大回撤点
    max_dd_idx = drawdown.idxmin()
    max_dd_value = drawdown.min()
    
    fig.add_annotation(
        x=max_dd_idx,
        y=max_dd_value * 100,
        text=f"最大回撤: {max_dd_value:.2%}",
        showarrow=True,
        arrowhead=2,
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="交易日", row=2, col=1)
    fig.update_yaxes(title_text="权益", row=1, col=1)
    fig.update_yaxes(title_text="回撤 (%)", row=2, col=1)
    
    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 回撤统计
    with st.expander("📉 回撤详情"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**最大回撤**: {drawdown.min():.2%}")
            st.write(f"**当前回撤**: {drawdown.iloc[-1]:.2%}")
        with col2:
            # 计算回撤持续时间
            dd_duration = calculate_drawdown_duration(drawdown)
            st.write(f"**最长回撤期**: {dd_duration} 天")
            st.write(f"**平均回撤**: {drawdown[drawdown < 0].mean():.2%}")
        with col3:
            # 回撤次数
            dd_count = count_drawdown_periods(drawdown)
            st.write(f"**回撤次数**: {dd_count}")
            st.write(f"**当前状态**: {'创新高' if drawdown.iloc[-1] == 0 else '回撤中'}")


def show_monte_carlo_simulation(data_manager, config):
    """显示蒙特卡洛模拟"""
    st.subheader("🎲 蒙特卡洛模拟")
    
    st.markdown("""
    通过随机模拟预测未来可能的收益路径和风险分布。
    """)
    
    # 参数设置
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        initial_value = st.number_input("初始资金", value=100000, step=10000, key="mc_initial")
    with col2:
        days = st.selectbox("预测天数", [30, 60, 90, 180, 365], index=3, key="mc_days")
    with col3:
        simulations = st.selectbox("模拟次数", [100, 500, 1000, 5000], index=2, key="mc_sims")
    with col4:
        expected_return = st.slider("预期年化收益", -0.2, 0.5, 0.08, 0.01, format="%.2f", key="mc_return")
    
    col1, col2 = st.columns(2)
    with col1:
        volatility = st.slider("年化波动率", 0.05, 0.60, 0.25, 0.05, format="%.2f", key="mc_vol")
    with col2:
        confidence_levels = st.multiselect(
            "置信区间",
            [0.05, 0.25, 0.50, 0.75, 0.95],
            default=[0.05, 0.50, 0.95],
            key="mc_confidence"
        )
    
    if st.button("🎲 运行蒙特卡洛模拟", key="run_mc"):
        with st.spinner(f"正在运行 {simulations} 次模拟..."):
            # 运行蒙特卡洛模拟
            results = run_monte_carlo(
                initial_value=initial_value,
                days=days,
                simulations=simulations,
                expected_return=expected_return,
                volatility=volatility
            )
            
            # 显示模拟路径
            st.markdown("### 📈 模拟路径")
            show_monte_carlo_paths(results, confidence_levels)
            
            # 显示结果分布
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 最终价值分布")
                show_final_value_distribution(results, initial_value)
            
            with col2:
                st.markdown("### 📉 最大回撤分布")
                show_drawdown_distribution(results)
            
            # 统计摘要
            st.markdown("### 📋 模拟结果统计")
            show_monte_carlo_statistics(results, initial_value, confidence_levels)


def run_monte_carlo(initial_value: float, days: int, simulations: int,
                   expected_return: float, volatility: float) -> Dict:
    """运行蒙特卡洛模拟
    
    Args:
        initial_value: 初始资金
        days: 模拟天数
        simulations: 模拟次数
        expected_return: 年化预期收益
        volatility: 年化波动率
        
    Returns:
        模拟结果字典
    """
    # 转换为日收益参数
    daily_return = expected_return / 252
    daily_vol = volatility / np.sqrt(252)
    
    # 生成随机路径
    paths = np.zeros((simulations, days + 1))
    paths[:, 0] = initial_value
    
    for i in range(simulations):
        for t in range(1, days + 1):
            random_shock = np.random.normal(0, 1)
            daily_change = daily_return + daily_vol * random_shock
            paths[i, t] = paths[i, t-1] * (1 + daily_change)
    
    # 计算每条路径的最大回撤
    max_drawdowns = []
    for i in range(simulations):
        cummax = np.maximum.accumulate(paths[i, :])
        drawdown = (paths[i, :] - cummax) / cummax
        max_drawdowns.append(drawdown.min())
    
    return {
        'paths': paths,
        'final_values': paths[:, -1],
        'max_drawdowns': np.array(max_drawdowns),
        'days': days,
        'simulations': simulations
    }


def show_monte_carlo_paths(results: Dict, confidence_levels: List[float]):
    """显示蒙特卡洛路径图
    
    Args:
        results: 模拟结果
        confidence_levels: 置信区间列表
    """
    paths = results['paths']
    days = results['days']
    
    fig = go.Figure()
    
    # 显示部分路径 (避免太多路径导致图表卡顿)
    num_paths_to_show = min(100, paths.shape[0])
    for i in range(num_paths_to_show):
        fig.add_trace(go.Scatter(
            x=list(range(days + 1)),
            y=paths[i, :],
            mode='lines',
            line=dict(width=0.5, color='lightblue'),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 添加置信区间
    colors = ['red', 'orange', 'green', 'orange', 'red']
    for idx, confidence in enumerate(sorted(confidence_levels)):
        percentile_values = np.percentile(paths, confidence * 100, axis=0)
        fig.add_trace(go.Scatter(
            x=list(range(days + 1)),
            y=percentile_values,
            mode='lines',
            name=f'{confidence:.0%} 分位数',
            line=dict(width=2, color=colors[idx % len(colors)]),
        ))
    
    # 添加中位数 (50%)
    median_path = np.percentile(paths, 50, axis=0)
    fig.add_trace(go.Scatter(
        x=list(range(days + 1)),
        y=median_path,
        mode='lines',
        name='中位数',
        line=dict(width=3, color='blue', dash='dash')
    ))
    
    fig.update_layout(
        title=f"蒙特卡洛模拟路径 ({results['simulations']} 次模拟)",
        xaxis_title="天数",
        yaxis_title="资产价值",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_final_value_distribution(results: Dict, initial_value: float):
    """显示最终价值分布
    
    Args:
        results: 模拟结果
        initial_value: 初始资金
    """
    final_values = results['final_values']
    
    fig = go.Figure()
    
    # 直方图
    fig.add_trace(go.Histogram(
        x=final_values,
        nbinsx=50,
        name='分布',
        marker_color='lightgreen',
        opacity=0.7
    ))
    
    # 添加初始值线
    fig.add_vline(
        x=initial_value,
        line_dash="dash",
        line_color="black",
        annotation_text=f"初始: {initial_value:,.0f}",
        annotation_position="top"
    )
    
    # 添加中位数线
    median_value = np.median(final_values)
    fig.add_vline(
        x=median_value,
        line_dash="dash",
        line_color="blue",
        annotation_text=f"中位数: {median_value:,.0f}",
        annotation_position="bottom"
    )
    
    fig.update_layout(
        title="最终资产价值分布",
        xaxis_title="最终价值",
        yaxis_title="频数",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_drawdown_distribution(results: Dict):
    """显示回撤分布
    
    Args:
        results: 模拟结果
    """
    max_drawdowns = results['max_drawdowns']
    
    fig = go.Figure()
    
    # 直方图
    fig.add_trace(go.Histogram(
        x=max_drawdowns * 100,
        nbinsx=50,
        name='回撤分布',
        marker_color='lightcoral',
        opacity=0.7
    ))
    
    # 添加中位数线
    median_dd = np.median(max_drawdowns)
    fig.add_vline(
        x=median_dd * 100,
        line_dash="dash",
        line_color="red",
        annotation_text=f"中位数: {median_dd:.2%}",
        annotation_position="top"
    )
    
    # 添加95%分位数
    percentile_95 = np.percentile(max_drawdowns, 95)
    fig.add_vline(
        x=percentile_95 * 100,
        line_dash="dot",
        line_color="darkred",
        annotation_text=f"95%: {percentile_95:.2%}",
        annotation_position="bottom"
    )
    
    fig.update_layout(
        title="最大回撤分布",
        xaxis_title="最大回撤 (%)",
        yaxis_title="频数",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_monte_carlo_statistics(results: Dict, initial_value: float, confidence_levels: List[float]):
    """显示蒙特卡洛统计摘要
    
    Args:
        results: 模拟结果
        initial_value: 初始资金
        confidence_levels: 置信区间
    """
    final_values = results['final_values']
    max_drawdowns = results['max_drawdowns']
    
    # 计算收益率
    returns = (final_values - initial_value) / initial_value
    
    # 基础统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均最终价值", f"{np.mean(final_values):,.0f}")
        st.metric("平均收益率", f"{np.mean(returns):.2%}")
    
    with col2:
        st.metric("中位数价值", f"{np.median(final_values):,.0f}")
        st.metric("中位数收益", f"{np.median(returns):.2%}")
    
    with col3:
        st.metric("最好情况", f"{np.max(final_values):,.0f}")
        st.metric("最佳收益", f"{np.max(returns):.2%}")
    
    with col4:
        st.metric("最差情况", f"{np.min(final_values):,.0f}")
        st.metric("最差收益", f"{np.min(returns):.2%}")
    
    st.markdown("---")
    
    # 风险统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**价值分位数**")
        for conf in sorted(confidence_levels):
            percentile_val = np.percentile(final_values, conf * 100)
            st.write(f"{conf:.0%}: {percentile_val:,.0f}")
    
    with col2:
        st.write("**回撤统计**")
        st.write(f"平均: {np.mean(max_drawdowns):.2%}")
        st.write(f"中位数: {np.median(max_drawdowns):.2%}")
        st.write(f"95%: {np.percentile(max_drawdowns, 95):.2%}")
    
    with col3:
        st.write("**概率分析**")
        prob_profit = (returns > 0).sum() / len(returns)
        prob_loss_10 = (returns < -0.10).sum() / len(returns)
        prob_gain_20 = (returns > 0.20).sum() / len(returns)
        st.write(f"盈利概率: {prob_profit:.1%}")
        st.write(f"亏损>10%: {prob_loss_10:.1%}")
        st.write(f"收益>20%: {prob_gain_20:.1%}")


def show_historical_risk_trends(data_manager, config):
    """显示历史风险趋势"""
    st.subheader("📈 历史风险趋势")
    
    st.markdown("""
    追踪风险指标的历史变化趋势,识别风险周期。
    """)
    
    # 参数设置
    col1, col2 = st.columns(2)
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="trend_asset")
    with col2:
        window = st.selectbox("滚动窗口", [20, 60, 120, 252], index=1, key="trend_window",
                             format_func=lambda x: f"{x}天")
    
    if st.button("📊 分析趋势", key="analyze_trend"):
        with st.spinner("正在分析历史趋势..."):
            # 生成模拟数据
            trend_data = generate_mock_trend_data(asset_code, window)
            
            # 显示风险趋势图
            show_risk_trend_chart(trend_data, window)
            
            # 显示相关性热力图
            st.markdown("### 🔥 风险指标相关性")
            show_risk_correlation_heatmap(trend_data)


def show_risk_trend_chart(trend_data: Dict, window: int):
    """显示风险趋势图表
    
    Args:
        trend_data: 趋势数据
        window: 滚动窗口
    """
    df = trend_data['dataframe']
    
    # 创建四个子图
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            "滚动波动率 (年化)",
            "滚动最大回撤",
            "滚动夏普比率",
            "滚动VaR (95%)"
        ),
        vertical_spacing=0.08,
        row_heights=[0.25, 0.25, 0.25, 0.25]
    )
    
    # 波动率
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['volatility'] * 100,
            name='波动率',
            line=dict(color='orange', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 165, 0, 0.2)'
        ),
        row=1, col=1
    )
    
    # 最大回撤
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['max_drawdown'] * 100,
            name='最大回撤',
            line=dict(color='red', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.2)'
        ),
        row=2, col=1
    )
    
    # 夏普比率
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['sharpe_ratio'],
            name='夏普比率',
            line=dict(color='green', width=2)
        ),
        row=3, col=1
    )
    # 添加0线
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
    
    # VaR
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['var_95'] * 100,
            name='VaR (95%)',
            line=dict(color='purple', width=2),
            fill='tozeroy',
            fillcolor='rgba(128, 0, 128, 0.2)'
        ),
        row=4, col=1
    )
    
    # 更新坐标轴
    fig.update_xaxes(title_text="日期", row=4, col=1)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="%", row=2, col=1)
    fig.update_yaxes(title_text="比率", row=3, col=1)
    fig.update_yaxes(title_text="%", row=4, col=1)
    
    fig.update_layout(
        title=f"风险指标历史趋势 (滚动窗口: {window}天)",
        height=900,
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 当前值摘要
    with st.expander("📊 当前风险指标"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("波动率", f"{df['volatility'].iloc[-1]:.2%}")
        with col2:
            st.metric("最大回撤", f"{df['max_drawdown'].iloc[-1]:.2%}")
        with col3:
            st.metric("夏普比率", f"{df['sharpe_ratio'].iloc[-1]:.2f}")
        with col4:
            st.metric("VaR (95%)", f"{df['var_95'].iloc[-1]:.2%}")


def show_risk_correlation_heatmap(trend_data: Dict):
    """显示风险指标相关性热力图
    
    Args:
        trend_data: 趋势数据
    """
    df = trend_data['dataframe']
    
    # 选择数值列
    numeric_cols = ['volatility', 'max_drawdown', 'sharpe_ratio', 'var_95']
    corr_matrix = df[numeric_cols].corr()
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=['波动率', '最大回撤', '夏普比率', 'VaR'],
        y=['波动率', '最大回撤', '夏普比率', 'VaR'],
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="相关系数")
    ))
    
    fig.update_layout(
        title="风险指标相关性矩阵",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_portfolio_risk(data_manager, config):
    """显示组合风险分析"""
    st.subheader("📊 组合风险分析")
    
    st.markdown("""
    分析投资组合的整体风险特征和资产间的相关性。
    """)
    
    # 组合配置
    st.markdown("### ⚙️ 组合配置")
    
    num_assets = st.slider("资产数量", 2, 10, 4, key="portfolio_num_assets")
    
    assets = []
    weights = []
    
    cols = st.columns(min(num_assets, 4))
    for i in range(num_assets):
        with cols[i % 4]:
            asset = st.text_input(f"资产{i+1}", value=f"Asset_{i+1}", key=f"asset_{i}")
            weight = st.number_input(f"权重{i+1}", 0.0, 1.0, 1.0/num_assets, 0.05, key=f"weight_{i}")
            assets.append(asset)
            weights.append(weight)
    
    # 归一化权重
    total_weight = sum(weights)
    if total_weight > 0:
        weights = [w / total_weight for w in weights]
    
    if st.button("📊 分析组合风险", key="analyze_portfolio"):
        with st.spinner("正在分析组合..."):
            # 生成模拟数据
            portfolio_data = generate_mock_portfolio_data(assets, weights)
            
            # 显示组合权重
            st.markdown("### 📊 资产配置")
            show_portfolio_allocation(assets, weights)
            
            # 显示相关性矩阵
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🔗 资产相关性")
                show_asset_correlation(portfolio_data)
            
            with col2:
                st.markdown("### 📈 风险贡献")
                show_risk_contribution(assets, weights, portfolio_data)
            
            # 显示有效前沿
            st.markdown("### 📉 有效前沿")
            show_efficient_frontier(portfolio_data)


def show_portfolio_allocation(assets: List[str], weights: List[float]):
    """显示组合配置饼图"""
    fig = go.Figure(data=[go.Pie(
        labels=assets,
        values=weights,
        hole=0.4,
        textposition='auto',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        title="组合资产配置",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_asset_correlation(portfolio_data: Dict):
    """显示资产相关性热力图"""
    corr_matrix = portfolio_data['correlation_matrix']
    assets = portfolio_data['assets']
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=assets,
        y=assets,
        colorscale='RdYlGn',
        zmid=0,
        text=corr_matrix,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="相关系数")
    ))
    
    fig.update_layout(
        title="资产相关性矩阵",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_risk_contribution(assets: List[str], weights: List[float], portfolio_data: Dict):
    """显示风险贡献图"""
    # 计算风险贡献 (简化版)
    risk_contrib = np.array(weights) * portfolio_data['volatilities']
    risk_contrib = risk_contrib / risk_contrib.sum()
    
    fig = go.Figure(data=[go.Bar(
        x=assets,
        y=risk_contrib * 100,
        marker_color='lightcoral',
        text=[f"{v:.1%}" for v in risk_contrib],
        textposition='auto'
    )])
    
    fig.update_layout(
        title="各资产风险贡献度",
        xaxis_title="资产",
        yaxis_title="风险贡献 (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_efficient_frontier(portfolio_data: Dict):
    """显示有效前沿"""
    # 生成有效前沿点
    returns = []
    risks = []
    sharpe_ratios = []
    
    for _ in range(1000):
        # 随机生成权重
        w = np.random.random(len(portfolio_data['assets']))
        w = w / w.sum()
        
        # 计算组合收益和风险
        port_return = np.dot(w, portfolio_data['returns'])
        port_risk = np.sqrt(np.dot(w.T, np.dot(portfolio_data['cov_matrix'], w)))
        
        returns.append(port_return)
        risks.append(port_risk)
        sharpe_ratios.append(port_return / port_risk if port_risk > 0 else 0)
    
    # 创建散点图
    fig = go.Figure()
    
    # 所有组合
    fig.add_trace(go.Scatter(
        x=np.array(risks) * 100,
        y=np.array(returns) * 100,
        mode='markers',
        marker=dict(
            size=5,
            color=sharpe_ratios,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="夏普比率")
        ),
        name='随机组合',
        text=[f"收益: {r:.2%}<br>风险: {v:.2%}<br>夏普: {s:.2f}" 
              for r, v, s in zip(returns, risks, sharpe_ratios)],
        hoverinfo='text'
    ))
    
    # 标记最大夏普比率组合
    max_sharpe_idx = np.argmax(sharpe_ratios)
    fig.add_trace(go.Scatter(
        x=[risks[max_sharpe_idx] * 100],
        y=[returns[max_sharpe_idx] * 100],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name='最优夏普',
        text=f"最优夏普组合<br>收益: {returns[max_sharpe_idx]:.2%}<br>风险: {risks[max_sharpe_idx]:.2%}",
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title="投资组合有效前沿",
        xaxis_title="风险 (年化波动率 %)",
        yaxis_title="收益 (年化收益率 %)",
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 最优组合信息
    with st.expander("⭐ 最优组合详情"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预期收益", f"{returns[max_sharpe_idx]:.2%}")
        with col2:
            st.metric("预期风险", f"{risks[max_sharpe_idx]:.2%}")
        with col3:
            st.metric("夏普比率", f"{sharpe_ratios[max_sharpe_idx]:.2f}")


# ============== 辅助函数 ==============

def generate_mock_risk_data(asset_code: str, period: str) -> Dict:
    """生成模拟风险数据"""
    # 生成模拟收益率
    days = {'1M': 30, '3M': 90, '6M': 180, '1Y': 252, '3Y': 756}.get(period, 252)
    returns = np.random.normal(0.0005, 0.015, days)
    
    # 生成权益曲线
    equity_curve = pd.Series((1 + returns).cumprod())
    
    return {
        'asset_code': asset_code,
        'returns': returns,
        'equity_curve': equity_curve,
        'volatility': np.std(returns) * np.sqrt(252),
        'volatility_change': -0.02,
        'max_drawdown': -0.18,
        'drawdown_change': 0.03,
        'var_95': np.percentile(returns, 5),
        'cvar_95': returns[returns <= np.percentile(returns, 5)].mean(),
        'sharpe_ratio': (np.mean(returns) * 252) / (np.std(returns) * np.sqrt(252)),
        'sharpe_change': 0.1,
        'volatility_score': 70,
        'liquidity_score': 80,
        'drawdown_score': 65,
        'tail_risk_score': 75,
        'concentration_score': 85
    }


def generate_mock_trend_data(asset_code: str, window: int) -> Dict:
    """生成模拟趋势数据"""
    days = 500
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成基础收益率
    returns = np.random.normal(0.0005, 0.015, days)
    
    # 计算滚动指标
    volatility = pd.Series(returns).rolling(window).std() * np.sqrt(252)
    
    # 计算滚动最大回撤
    equity = (1 + pd.Series(returns)).cumprod()
    max_drawdown = []
    for i in range(len(equity)):
        if i < window:
            max_drawdown.append(0)
        else:
            window_equity = equity.iloc[i-window:i+1]
            cummax = window_equity.cummax()
            dd = ((window_equity - cummax) / cummax).min()
            max_drawdown.append(dd)
    
    # 计算滚动夏普比率
    sharpe = (pd.Series(returns).rolling(window).mean() * 252) / (pd.Series(returns).rolling(window).std() * np.sqrt(252))
    
    # 计算滚动VaR
    var_95 = pd.Series(returns).rolling(window).quantile(0.05)
    
    df = pd.DataFrame({
        'date': dates,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe,
        'var_95': var_95
    }).fillna(0)
    
    return {'dataframe': df}


def generate_mock_portfolio_data(assets: List[str], weights: List[float]) -> Dict:
    """生成模拟组合数据"""
    n = len(assets)
    
    # 生成随机收益率和波动率
    returns = np.random.uniform(0.05, 0.15, n)
    volatilities = np.random.uniform(0.10, 0.30, n)
    
    # 生成相关性矩阵
    corr_matrix = np.random.uniform(0.3, 0.8, (n, n))
    corr_matrix = (corr_matrix + corr_matrix.T) / 2  # 对称
    np.fill_diagonal(corr_matrix, 1.0)  # 对角线为1
    
    # 生成协方差矩阵
    D = np.diag(volatilities)
    cov_matrix = D @ corr_matrix @ D
    
    return {
        'assets': assets,
        'returns': returns,
        'volatilities': volatilities,
        'correlation_matrix': corr_matrix,
        'cov_matrix': cov_matrix
    }


def calculate_drawdown_duration(drawdown: pd.Series) -> int:
    """计算最长回撤持续时间"""
    in_drawdown = drawdown < 0
    drawdown_periods = []
    current_period = 0
    
    for is_dd in in_drawdown:
        if is_dd:
            current_period += 1
        else:
            if current_period > 0:
                drawdown_periods.append(current_period)
            current_period = 0
    
    if current_period > 0:
        drawdown_periods.append(current_period)
    
    return max(drawdown_periods) if drawdown_periods else 0


def count_drawdown_periods(drawdown: pd.Series) -> int:
    """计算回撤次数"""
    in_drawdown = drawdown < 0
    count = 0
    prev = False
    
    for is_dd in in_drawdown:
        if is_dd and not prev:
            count += 1
        prev = is_dd
    
    return count


if __name__ == "__main__":
    st.set_page_config(page_title="风险管理增强", layout="wide")
    show_risk_enhanced(None, {})

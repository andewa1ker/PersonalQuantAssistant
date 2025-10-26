"""
增强版策略信号页面
包含信号强度可视化、历史回测、统计分析
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_signals_enhanced(config, data_manager, signal_gen):
    """显示增强版策略信号页面"""
    st.header("🎯 策略信号中心")
    
    # 顶部控制栏
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        view_mode = st.selectbox(
            "视图模式",
            ["实时信号", "历史回测", "统计分析"],
            key="signals_view_mode"
        )
    
    with col2:
        time_range = st.selectbox(
            "分析周期",
            ["1个月", "3个月", "6个月", "1年"],
            index=1,
            key="signals_time_range"
        )
    
    with col3:
        if st.button("🔄", help="刷新信号"):
            st.cache_resource.clear()
            st.rerun()
    
    # 根据视图模式显示不同内容
    if view_mode == "实时信号":
        show_realtime_signals(config, data_manager, signal_gen, time_range)
    elif view_mode == "历史回测":
        show_backtest_signals(config, data_manager, signal_gen, time_range)
    else:  # 统计分析
        show_signal_statistics(config, data_manager, signal_gen, time_range)


def show_realtime_signals(config, data_manager, signal_gen, time_range):
    """显示实时信号"""
    st.markdown("### 📊 实时交易信号")
    
    enabled_assets = config.get_enabled_assets()
    
    if not enabled_assets:
        st.warning("⚠️ 没有启用的资产")
        return
    
    with st.spinner("正在生成交易信号..."):
        signal_results = []
        detailed_signals = []
        
        # 时间周期映射
        period_map = {
            "1个月": "1m",
            "3个月": "3m",
            "6个月": "6m",
            "1年": "1y"
        }
        period = period_map.get(time_range, "3m")
        
        # ETF信号
        if 'etf_513500' in enabled_assets:
            try:
                history = data_manager.get_asset_data('etf', '513500', 'history', period=period)
                if history is not None and len(history) > 20:
                    report = signal_gen.analyze_with_signals(history)
                    if 'signals' in report:
                        signals = report['signals']
                        signal_results.append({
                            '品种': '513500 ETF',
                            '当前价格': f"¥{history['close'].iloc[-1]:.3f}",
                            '信号': signals['signal'],
                            '信心度': signals['confidence'],
                            '强度': signals['total_strength'],
                            '趋势': report.get('trend_analysis', {}).get('trend', {}).get('trend', 'N/A')
                        })
                        detailed_signals.append({
                            'asset': '513500 ETF',
                            'data': history,
                            'report': report,
                            'signals': signals
                        })
            except Exception as e:
                logger.error(f"获取513500信号失败: {e}")
        
        # 加密货币信号
        crypto_config = config.get_asset_config('crypto')
        if crypto_config:
            symbols = crypto_config.get('symbols', ['bitcoin', 'ethereum'])
            for symbol in symbols[:3]:
                try:
                    days_map = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}
                    history = data_manager.get_asset_data('crypto', symbol, 'history', 
                                                         days=days_map.get(period, 90))
                    if history is not None and len(history) > 20:
                        # 准备数据
                        if 'price' in history.columns:
                            analysis_data = history.rename(columns={'price': 'close'}).copy()
                            if 'high' not in analysis_data.columns:
                                analysis_data['high'] = analysis_data['close'] * 1.02
                                analysis_data['low'] = analysis_data['close'] * 0.98
                                analysis_data['open'] = analysis_data['close'].shift(1).fillna(analysis_data['close'])
                            if 'volume' not in analysis_data.columns:
                                analysis_data['volume'] = 1000000
                        else:
                            analysis_data = history
                        
                        report = signal_gen.analyze_with_signals(analysis_data)
                        if 'signals' in report:
                            signals = report['signals']
                            signal_results.append({
                                '品种': symbol.upper(),
                                '当前价格': f"${analysis_data['close'].iloc[-1]:,.2f}",
                                '信号': signals['signal'],
                                '信心度': signals['confidence'],
                                '强度': signals['total_strength'],
                                '趋势': report.get('trend_analysis', {}).get('trend', {}).get('trend', 'N/A')
                            })
                            detailed_signals.append({
                                'asset': symbol.upper(),
                                'data': analysis_data,
                                'report': report,
                                'signals': signals
                            })
                except Exception as e:
                    logger.warning(f"获取{symbol}信号失败: {e}")
    
    if signal_results:
        # 信号摘要卡片
        show_signal_summary_cards(signal_results)
        
        st.markdown("---")
        
        # 信号表格
        show_signal_table(signal_results)
        
        st.markdown("---")
        
        # 信号强度雷达图
        st.markdown("### 📡 信号强度对比")
        show_signal_radar(detailed_signals)
        
        st.markdown("---")
        
        # 详细信号分析
        st.markdown("### 📋 详细信号分析")
        show_detailed_signal_analysis(detailed_signals)
    else:
        st.info("暂无信号数据")


def show_signal_summary_cards(signal_results):
    """显示信号摘要卡片"""
    st.markdown("### 📊 信号概览")
    
    # 统计信号类型
    buy_count = sum(1 for s in signal_results if '买入' in s['信号'])
    sell_count = sum(1 for s in signal_results if '卖出' in s['信号'])
    hold_count = sum(1 for s in signal_results if '持有' in s['信号'] or '观望' in s['信号'])
    
    # 平均信心度 - 转换文字为数字
    def confidence_to_number(conf_str):
        """将信心度文字转换为数字"""
        conf_map = {'低': 33, '中': 66, '高': 90}
        # 如果是百分比数字,直接转换
        if isinstance(conf_str, (int, float)):
            return float(conf_str)
        conf_str = str(conf_str).strip()
        if conf_str.endswith('%'):
            try:
                return float(conf_str.rstrip('%'))
            except:
                pass
        # 如果是文字,使用映射
        return conf_map.get(conf_str, 50)
    
    avg_confidence = np.mean([confidence_to_number(s['信心度']) for s in signal_results])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 买入信号", buy_count)
    
    with col2:
        st.metric("🔴 卖出信号", sell_count)
    
    with col3:
        st.metric("🟡 持有/观望", hold_count)
    
    with col4:
        st.metric("📊 平均信心度", f"{avg_confidence:.1f}%")


def show_signal_table(signal_results):
    """显示信号表格"""
    st.markdown("### 📋 信号列表")
    
    df = pd.DataFrame(signal_results)
    
    # 颜色标记
    def highlight_signal(row):
        if '买入' in row['信号']:
            return ['background-color: #d4edda'] * len(row)
        elif '卖出' in row['信号']:
            return ['background-color: #f8d7da'] * len(row)
        else:
            return ['background-color: #fff3cd'] * len(row)
    
    st.dataframe(
        df.style.apply(highlight_signal, axis=1),
        use_container_width=True,
        hide_index=True
    )


def show_signal_radar(detailed_signals):
    """显示信号强度雷达图"""
    if not detailed_signals:
        return
    
    # 提取信号强度数据
    categories = ['趋势强度', '动量强度', '成交量', '波动率', '支撑阻力']
    
    fig = go.Figure()
    
    for detail in detailed_signals[:5]:  # 最多5个资产
        signals = detail['signals']
        
        # 提取各维度强度（归一化到0-100）
        values = [
            abs(signals.get('ma_strength', 0)) * 100,
            abs(signals.get('macd_strength', 0)) * 100,
            abs(signals.get('kdj_strength', 0)) * 100,
            abs(signals.get('rsi_strength', 0)) * 100,
            abs(signals.get('bollinger_strength', 0)) * 100
        ]
        values.append(values[0])  # 闭合雷达图
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=detail['asset']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=400,
        title="信号强度雷达图"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_detailed_signal_analysis(detailed_signals):
    """显示详细信号分析"""
    for detail in detailed_signals:
        asset = detail['asset']
        data = detail['data']
        report = detail['report']
        signals = detail['signals']
        
        with st.expander(f"📊 {asset} - {signals['signal']} ({signals['confidence']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("当前价格", f"{data['close'].iloc[-1]:.4f}")
                st.metric("信号", signals['signal'])
            
            with col2:
                st.metric("信心度", signals['confidence'])
                st.metric("总强度", f"{signals['total_strength']:.2f}")
            
            with col3:
                trend_info = report.get('trend_analysis', {}).get('trend', {})
                st.metric("趋势", trend_info.get('trend', 'N/A'))
                # 确保strength是数字类型
                strength_value = trend_info.get('strength', 0)
                if isinstance(strength_value, (int, float)):
                    st.metric("趋势强度", f"{strength_value:.2f}")
                else:
                    st.metric("趋势强度", str(strength_value))
            
            # 信号来源分解
            st.markdown("#### 信号来源")
            
            signal_components = []
            for key, value in signals.items():
                if 'strength' in key and 'total' not in key:
                    indicator = key.replace('_strength', '').upper()
                    signal_components.append({
                        '指标': indicator,
                        '强度': value,
                        '贡献': f"{abs(value) / abs(signals['total_strength']) * 100:.1f}%" if signals['total_strength'] != 0 else "0%"
                    })
            
            if signal_components:
                comp_df = pd.DataFrame(signal_components)
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
            
            # 价格走势图
            st.markdown("#### 价格走势")
            show_price_with_signals(data, signals)


def show_price_with_signals(data, signals):
    """显示带信号标记的价格图"""
    fig = go.Figure()
    
    # 价格线
    x_values = data.index if isinstance(data.index, pd.DatetimeIndex) else list(range(len(data)))
    fig.add_trace(go.Scatter(
        x=x_values,
        y=data['close'],
        name='价格',
        line=dict(color='blue')
    ))
    
    # 移动平均线
    if len(data) >= 20:
        ma20 = data['close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data.index if isinstance(data.index, pd.DatetimeIndex) else range(len(data)),
            y=ma20,
            name='MA20',
            line=dict(color='orange', dash='dash')
        ))
    
    fig.update_layout(
        title="价格走势与信号",
        xaxis_title="时间",
        yaxis_title="价格",
        height=300,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_backtest_signals(config, data_manager, signal_gen, time_range):
    """显示历史回测"""
    st.markdown("### 📈 历史信号回测")
    
    st.info("💡 信号回测功能展示历史信号的表现和胜率")
    
    # 选择资产
    col1, col2 = st.columns(2)
    
    with col1:
        asset_type = st.selectbox(
            "资产类型",
            ["ETF", "加密货币"],
            key="backtest_asset_type"
        )
    
    with col2:
        if asset_type == "ETF":
            asset_symbol = st.text_input("资产代码", value="513500", key="backtest_symbol")
        else:
            asset_symbol = st.selectbox(
                "加密货币",
                ["bitcoin", "ethereum", "bnb"],
                key="backtest_crypto"
            )
    
    if st.button("🔍 开始回测", key="start_backtest"):
        with st.spinner("正在回测..."):
            try:
                # 获取历史数据
                period_map = {"1个月": "1m", "3个月": "3m", "6个月": "6m", "1年": "1y"}
                period = period_map.get(time_range, "6m")
                
                if asset_type == "ETF":
                    data = data_manager.get_asset_data('etf', asset_symbol, 'history', period=period)
                else:
                    days_map = {"1m": 30, "3m": 90, "6m": 180, "1y": 365}
                    data = data_manager.get_asset_data('crypto', asset_symbol, 'history', 
                                                       days=days_map.get(period, 180))
                
                if data is None or len(data) < 30:
                    st.error("❌ 数据不足，无法回测")
                    return
                
                # 准备数据
                if 'price' in data.columns:
                    data = data.rename(columns={'price': 'close'}).copy()
                    if 'high' not in data.columns:
                        data['high'] = data['close'] * 1.02
                        data['low'] = data['close'] * 0.98
                        data['open'] = data['close'].shift(1).fillna(data['close'])
                    if 'volume' not in data.columns:
                        data['volume'] = 1000000
                
                # 模拟回测
                backtest_results = simulate_backtest(data, signal_gen)
                
                if backtest_results:
                    display_backtest_results(backtest_results, asset_symbol)
                
            except Exception as e:
                st.error(f"❌ 回测失败: {str(e)}")
                logger.error(f"回测错误: {e}", exc_info=True)


def simulate_backtest(data, signal_gen):
    """模拟信号回测"""
    signals_history = []
    trades = []
    
    # 滚动窗口生成历史信号
    window_size = 60
    step = 10
    
    for i in range(window_size, len(data), step):
        window_data = data.iloc[:i].copy()
        
        try:
            report = signal_gen.analyze_with_signals(window_data)
            if 'signals' in report:
                signals = report['signals']
                
                signal_date = data.index[i-1] if isinstance(data.index, pd.DatetimeIndex) else i-1
                signal_price = data['close'].iloc[i-1]
                
                signals_history.append({
                    'date': signal_date,
                    'price': signal_price,
                    'signal': signals['signal'],
                    'confidence': signals['confidence'],
                    'strength': signals['total_strength']
                })
                
                # 模拟交易
                if '买入' in signals['signal']:
                    # 检查未来收益
                    if i < len(data) - 10:
                        future_price = data['close'].iloc[i+9]
                        pnl = (future_price - signal_price) / signal_price
                        trades.append({
                            'entry_date': signal_date,
                            'entry_price': signal_price,
                            'exit_price': future_price,
                            'pnl': pnl,
                            'result': 'win' if pnl > 0 else 'loss'
                        })
        except Exception as e:
            logger.debug(f"回测窗口{i}失败: {e}")
            continue
    
    return {
        'signals_history': signals_history,
        'trades': trades,
        'data': data
    }


def display_backtest_results(results, asset_symbol):
    """显示回测结果"""
    st.success("✅ 回测完成")
    
    signals_history = results['signals_history']
    trades = results['trades']
    data = results['data']
    
    # 统计指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("信号总数", len(signals_history))
    
    with col2:
        st.metric("交易次数", len(trades))
    
    with col3:
        if trades:
            win_count = sum(1 for t in trades if t['result'] == 'win')
            win_rate = win_count / len(trades) * 100
            st.metric("胜率", f"{win_rate:.1f}%")
        else:
            st.metric("胜率", "—")
    
    with col4:
        if trades:
            avg_pnl = np.mean([t['pnl'] for t in trades]) * 100
            st.metric("平均收益", f"{avg_pnl:.2f}%")
        else:
            st.metric("平均收益", "—")
    
    st.markdown("---")
    
    # 回测图表
    st.markdown("### 📊 回测可视化")
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        subplot_titles=('价格与信号', '累计收益')
    )
    
    # 价格线
    fig.add_trace(
        go.Scatter(
            x=data.index if isinstance(data.index, pd.DatetimeIndex) else range(len(data)),
            y=data['close'],
            name='价格',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # 标记信号点
    buy_signals = [s for s in signals_history if '买入' in s['signal']]
    sell_signals = [s for s in signals_history if '卖出' in s['signal']]
    
    if buy_signals:
        fig.add_trace(
            go.Scatter(
                x=[s['date'] for s in buy_signals],
                y=[s['price'] for s in buy_signals],
                mode='markers',
                name='买入信号',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ),
            row=1, col=1
        )
    
    if sell_signals:
        fig.add_trace(
            go.Scatter(
                x=[s['date'] for s in sell_signals],
                y=[s['price'] for s in sell_signals],
                mode='markers',
                name='卖出信号',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ),
            row=1, col=1
        )
    
    # 累计收益曲线
    if trades:
        cumulative_pnl = np.cumsum([t['pnl'] for t in trades]) * 100
        fig.add_trace(
            go.Scatter(
                x=list(range(len(cumulative_pnl))),
                y=cumulative_pnl,
                name='累计收益',
                line=dict(color='purple'),
                fill='tozeroy'
            ),
            row=2, col=1
        )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="时间", row=2, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="累计收益(%)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 交易记录表
    if trades:
        st.markdown("---")
        st.markdown("### 📋 交易记录")
        
        trades_df = pd.DataFrame(trades)
        trades_df['pnl_pct'] = trades_df['pnl'] * 100
        trades_df = trades_df[['entry_date', 'entry_price', 'exit_price', 'pnl_pct', 'result']]
        trades_df.columns = ['入场时间', '入场价', '出场价', '收益率(%)', '结果']
        
        st.dataframe(trades_df, use_container_width=True, hide_index=True)


def show_signal_statistics(config, data_manager, signal_gen, time_range):
    """显示信号统计分析"""
    st.markdown("### 📊 信号统计分析")
    
    st.info("💡 统计分析展示各类信号的历史表现和可靠性")
    
    # 模拟统计数据（实际应从数据库或历史记录获取）
    stats_data = generate_mock_statistics()
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总信号数", "1,247")
    
    with col2:
        st.metric("平均胜率", "58.3%")
    
    with col3:
        st.metric("盈亏比", "1.8")
    
    with col4:
        st.metric("最佳策略", "MACD")
    
    st.markdown("---")
    
    # 图表展示
    tab1, tab2, tab3 = st.tabs(["信号分布", "胜率分析", "收益分析"])
    
    with tab1:
        show_signal_distribution(stats_data)
    
    with tab2:
        show_win_rate_analysis(stats_data)
    
    with tab3:
        show_profit_analysis(stats_data)


def generate_mock_statistics():
    """生成模拟统计数据"""
    return {
        'signal_types': {
            'MACD': {'count': 342, 'win_rate': 0.62, 'avg_profit': 0.035},
            'RSI': {'count': 289, 'win_rate': 0.55, 'avg_profit': 0.028},
            'KDJ': {'count': 267, 'win_rate': 0.58, 'avg_profit': 0.031},
            'MA': {'count': 349, 'win_rate': 0.59, 'avg_profit': 0.029}
        }
    }


def show_signal_distribution(stats_data):
    """显示信号分布"""
    st.markdown("#### 信号类型分布")
    
    signal_types = stats_data['signal_types']
    
    labels = list(signal_types.keys())
    values = [signal_types[k]['count'] for k in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3
    )])
    
    fig.update_layout(title="信号类型占比", height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_win_rate_analysis(stats_data):
    """显示胜率分析"""
    st.markdown("#### 各类信号胜率对比")
    
    signal_types = stats_data['signal_types']
    
    indicators = list(signal_types.keys())
    win_rates = [signal_types[k]['win_rate'] * 100 for k in indicators]
    
    fig = go.Figure(data=[
        go.Bar(
            x=indicators,
            y=win_rates,
            text=[f"{wr:.1f}%" for wr in win_rates],
            textposition='outside',
            marker_color=['green' if wr > 55 else 'orange' for wr in win_rates]
        )
    ])
    
    fig.update_layout(
        title="胜率对比",
        xaxis_title="指标",
        yaxis_title="胜率(%)",
        height=400
    )
    
    fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="50%基准线")
    
    st.plotly_chart(fig, use_container_width=True)


def show_profit_analysis(stats_data):
    """显示收益分析"""
    st.markdown("#### 平均收益对比")
    
    signal_types = stats_data['signal_types']
    
    indicators = list(signal_types.keys())
    profits = [signal_types[k]['avg_profit'] * 100 for k in indicators]
    
    fig = go.Figure(data=[
        go.Bar(
            x=indicators,
            y=profits,
            text=[f"{p:.2f}%" for p in profits],
            textposition='outside',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="平均收益对比",
        xaxis_title="指标",
        yaxis_title="平均收益率(%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

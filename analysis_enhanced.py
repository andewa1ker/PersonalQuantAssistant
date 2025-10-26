"""
增强版技术分析页面
包含K线图、技术指标叠加、形态识别
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_analysis_enhanced(config, data_manager):
    """显示增强版技术分析页面"""
    st.header("🔍 技术分析中心")
    
    # 顶部控制栏
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        asset_type = st.selectbox(
            "资产类型",
            ["ETF", "加密货币"],
            key="analysis_asset_type"
        )
    
    with col2:
        if asset_type == "ETF":
            symbol = st.text_input("ETF代码", value="513500", key="analysis_etf_symbol")
        else:
            symbol = st.selectbox(
                "加密货币",
                ["BTC", "ETH", "BNB", "XRP", "ADA"],
                key="analysis_crypto_symbol"
            )
    
    with col3:
        period = st.selectbox(
            "分析周期",
            ["1M", "3M", "6M", "1Y", "3Y"],
            index=2,
            key="analysis_period"
        )
    
    with col4:
        chart_type = st.selectbox(
            "图表类型",
            ["K线图", "折线图", "面积图"],
            key="analysis_chart_type"
        )
    
    if st.button("📊 开始分析", key="start_analysis"):
        with st.spinner("正在分析..."):
            try:
                # 获取历史数据
                data = fetch_analysis_data(data_manager, asset_type, symbol, period)
                
                if data is None or len(data) < 10:
                    st.error("❌ 数据不足，无法进行分析")
                    return
                
                # 显示主图表
                show_main_chart(data, symbol, chart_type)
                
                st.markdown("---")
                
                # 技术指标标签页
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 趋势指标",
                    "📈 动量指标",
                    "📉 波动率指标",
                    "🔍 形态识别"
                ])
                
                with tab1:
                    show_trend_indicators(data, symbol)
                
                with tab2:
                    show_momentum_indicators(data, symbol)
                
                with tab3:
                    show_volatility_indicators(data, symbol)
                
                with tab4:
                    show_pattern_recognition(data, symbol)
                
                st.markdown("---")
                
                # 综合分析
                show_comprehensive_analysis(data, symbol)
                
            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                logger.error(f"技术分析错误: {e}", exc_info=True)
    else:
        st.info("👆 选择资产和周期，点击【开始分析】")


def fetch_analysis_data(data_manager, asset_type, symbol, period):
    """获取分析数据"""
    try:
        # 转换周期格式
        period_map = {
            "1M": "1m",
            "3M": "3m",
            "6M": "6m",
            "1Y": "1y",
            "3Y": "3y"
        }
        period_value = period_map.get(period, "6m")
        
        if asset_type == "ETF":
            data = data_manager.get_asset_data(f"etf/{symbol}", "history", period=period_value)
        else:
            # 加密货币数据
            days_map = {"1m": 30, "3m": 90, "6m": 180, "1y": 365, "3y": 1095}
            days = days_map.get(period_value, 180)
            data = data_manager.get_asset_data(f"crypto/{symbol}", "history", days=days)
        
        return data
        
    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        return None


def generate_mock_crypto_data(symbol, period):
    """生成模拟加密货币数据"""
    # 实际应用中应该从真实API获取
    days_map = {"1m": 30, "3m": 90, "6m": 180, "1y": 365, "3y": 1095}
    days = days_map.get(period, 180)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # 生成随机价格数据
    np.random.seed(42)
    base_price = 50000 if symbol == "BTC" else 3000
    
    close_prices = base_price * (1 + np.cumsum(np.random.randn(days) * 0.02))
    
    data = pd.DataFrame({
        'date': dates,
        'open': close_prices * (1 + np.random.randn(days) * 0.01),
        'high': close_prices * (1 + abs(np.random.randn(days)) * 0.02),
        'low': close_prices * (1 - abs(np.random.randn(days)) * 0.02),
        'close': close_prices,
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    return data


def show_main_chart(data, symbol, chart_type):
    """显示主图表"""
    st.subheader(f"📊 {symbol} 价格走势")
    
    if chart_type == "K线图":
        show_candlestick_chart(data, symbol)
    elif chart_type == "折线图":
        show_line_chart(data, symbol)
    else:  # 面积图
        show_area_chart(data, symbol)


def show_candlestick_chart(data, symbol):
    """显示K线图"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} K线图', '成交量'),
        row_heights=[0.7, 0.3]
    )
    
    # K线图
    fig.add_trace(
        go.Candlestick(
            x=data['date'] if 'date' in data.columns else data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='K线'
        ),
        row=1, col=1
    )
    
    # 添加移动平均线
    if len(data) >= 20:
        ma5 = data['close'].rolling(window=5).mean()
        ma20 = data['close'].rolling(window=20).mean()
        
        fig.add_trace(
            go.Scatter(
                x=data['date'] if 'date' in data.columns else data.index,
                y=ma5,
                name='MA5',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data['date'] if 'date' in data.columns else data.index,
                y=ma20,
                name='MA20',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # 成交量
    colors = ['red' if close < open else 'green' 
              for close, open in zip(data['close'], data['open'])]
    
    fig.add_trace(
        go.Bar(
            x=data['date'] if 'date' in data.columns else data.index,
            y=data['volume'],
            name='成交量',
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="成交量", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def show_line_chart(data, symbol):
    """显示折线图"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['date'] if 'date' in data.columns else data.index,
        y=data['close'],
        mode='lines',
        name='收盘价',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title=f"{symbol} 价格走势",
        xaxis_title="日期",
        yaxis_title="价格",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_area_chart(data, symbol):
    """显示面积图"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['date'] if 'date' in data.columns else data.index,
        y=data['close'],
        fill='tozeroy',
        name='收盘价',
        line=dict(color='lightblue')
    ))
    
    fig.update_layout(
        title=f"{symbol} 价格走势",
        xaxis_title="日期",
        yaxis_title="价格",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_trend_indicators(data, symbol):
    """显示趋势指标"""
    st.markdown("### 📊 趋势指标分析")
    
    try:
        from analysis.indicators import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # 计算指标
        ma_result = indicators.calculate_ma(data, periods=[5, 10, 20, 60])
        macd_result = indicators.calculate_macd(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 移动平均线 (MA)")
            
            # MA图表
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data['date'] if 'date' in data.columns else data.index,
                y=data['close'],
                name='收盘价',
                line=dict(color='black', width=1)
            ))
            
            colors = ['orange', 'blue', 'green', 'red']
            for i, period in enumerate([5, 10, 20, 60]):
                if f'ma_{period}' in ma_result.data.columns:
                    fig.add_trace(go.Scatter(
                        x=ma_result.data['date'] if 'date' in ma_result.data.columns else ma_result.data.index,
                        y=ma_result.data[f'ma_{period}'],
                        name=f'MA{period}',
                        line=dict(color=colors[i], width=1)
                    ))
            
            fig.update_layout(
                title="移动平均线",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # MA信号
            if ma_result.signal and ma_result.signal != 'neutral':
                signal_emoji = "🟢" if ma_result.signal == 'bullish' else "🔴"
                st.info(f"{signal_emoji} 信号: {ma_result.signal} - {ma_result.reason}")
        
        with col2:
            st.markdown("#### MACD")
            
            if macd_result and macd_result.data is not None:
                # MACD图表
                fig = make_subplots(
                    rows=2, cols=1,
                    row_heights=[0.7, 0.3],
                    vertical_spacing=0.05
                )
                
                # MACD线和信号线
                fig.add_trace(go.Scatter(
                    x=macd_result.data['date'] if 'date' in macd_result.data.columns else macd_result.data.index,
                    y=macd_result.data['macd'],
                    name='MACD',
                    line=dict(color='blue')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=macd_result.data['date'] if 'date' in macd_result.data.columns else macd_result.data.index,
                    y=macd_result.data['signal'],
                    name='Signal',
                    line=dict(color='orange')
                ), row=1, col=1)
                
                # 柱状图
                colors = ['red' if val < 0 else 'green' for val in macd_result.data['histogram']]
                fig.add_trace(go.Bar(
                    x=macd_result.data['date'] if 'date' in macd_result.data.columns else macd_result.data.index,
                    y=macd_result.data['histogram'],
                    name='Histogram',
                    marker_color=colors
                ), row=2, col=1)
                
                fig.update_layout(
                    title="MACD指标",
                    height=300,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # MACD信号
                if macd_result.signal and macd_result.signal != 'neutral':
                    signal_emoji = "🟢" if macd_result.signal == 'bullish' else "🔴"
                    st.info(f"{signal_emoji} 信号: {macd_result.signal} - {macd_result.reason}")
        
    except Exception as e:
        st.error(f"计算趋势指标失败: {str(e)}")
        logger.error(f"趋势指标错误: {e}", exc_info=True)


def show_momentum_indicators(data, symbol):
    """显示动量指标"""
    st.markdown("### 📈 动量指标分析")
    
    try:
        from analysis.indicators import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### RSI (相对强弱指数)")
            
            rsi_result = indicators.calculate_rsi(data)
            
            if rsi_result and rsi_result.data is not None:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=rsi_result.data['date'] if 'date' in rsi_result.data.columns else rsi_result.data.index,
                    y=rsi_result.data['rsi'],
                    name='RSI',
                    line=dict(color='purple')
                ))
                
                # 添加超买超卖线
                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="超买")
                fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="超卖")
                
                fig.update_layout(
                    title="RSI指标",
                    yaxis_title="RSI",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI信号
                current_rsi = rsi_result.data['rsi'].iloc[-1]
                if current_rsi > 70:
                    st.warning(f"🔴 超买: RSI = {current_rsi:.2f}")
                elif current_rsi < 30:
                    st.success(f"🟢 超卖: RSI = {current_rsi:.2f}")
                else:
                    st.info(f"➡️ 中性: RSI = {current_rsi:.2f}")
        
        with col2:
            st.markdown("#### KDJ")
            
            kdj_result = indicators.calculate_kdj(data)
            
            if kdj_result and kdj_result.data is not None:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=kdj_result.data['date'] if 'date' in kdj_result.data.columns else kdj_result.data.index,
                    y=kdj_result.data['k'],
                    name='K',
                    line=dict(color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=kdj_result.data['date'] if 'date' in kdj_result.data.columns else kdj_result.data.index,
                    y=kdj_result.data['d'],
                    name='D',
                    line=dict(color='orange')
                ))
                
                fig.add_trace(go.Scatter(
                    x=kdj_result.data['date'] if 'date' in kdj_result.data.columns else kdj_result.data.index,
                    y=kdj_result.data['j'],
                    name='J',
                    line=dict(color='purple')
                ))
                
                fig.add_hline(y=80, line_dash="dash", line_color="red")
                fig.add_hline(y=20, line_dash="dash", line_color="green")
                
                fig.update_layout(
                    title="KDJ指标",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # KDJ信号
                if kdj_result.signal and kdj_result.signal != 'neutral':
                    signal_emoji = "🟢" if kdj_result.signal == 'bullish' else "🔴"
                    st.info(f"{signal_emoji} 信号: {kdj_result.signal}")
        
    except Exception as e:
        st.error(f"计算动量指标失败: {str(e)}")
        logger.error(f"动量指标错误: {e}", exc_info=True)


def show_volatility_indicators(data, symbol):
    """显示波动率指标"""
    st.markdown("### 📉 波动率指标分析")
    
    try:
        from analysis.indicators import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        
        # 布林带
        bollinger_result = indicators.calculate_bollinger_bands(data)
        
        if bollinger_result and bollinger_result.data is not None:
            fig = go.Figure()
            
            # 价格
            fig.add_trace(go.Scatter(
                x=bollinger_result.data['date'] if 'date' in bollinger_result.data.columns else bollinger_result.data.index,
                y=data['close'],
                name='收盘价',
                line=dict(color='black')
            ))
            
            # 上轨
            fig.add_trace(go.Scatter(
                x=bollinger_result.data['date'] if 'date' in bollinger_result.data.columns else bollinger_result.data.index,
                y=bollinger_result.data['upper'],
                name='上轨',
                line=dict(color='red', dash='dash')
            ))
            
            # 中轨
            fig.add_trace(go.Scatter(
                x=bollinger_result.data['date'] if 'date' in bollinger_result.data.columns else bollinger_result.data.index,
                y=bollinger_result.data['middle'],
                name='中轨',
                line=dict(color='blue')
            ))
            
            # 下轨
            fig.add_trace(go.Scatter(
                x=bollinger_result.data['date'] if 'date' in bollinger_result.data.columns else bollinger_result.data.index,
                y=bollinger_result.data['lower'],
                name='下轨',
                line=dict(color='green', dash='dash'),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title="布林带指标",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 布林带信号
            if bollinger_result.signal and bollinger_result.signal != 'neutral':
                signal_emoji = "🟢" if bollinger_result.signal == 'bullish' else "🔴"
                st.info(f"{signal_emoji} 信号: {bollinger_result.signal} - {bollinger_result.reason}")
        
    except Exception as e:
        st.error(f"计算波动率指标失败: {str(e)}")
        logger.error(f"波动率指标错误: {e}", exc_info=True)


def show_pattern_recognition(data, symbol):
    """显示形态识别"""
    st.markdown("### 🔍 技术形态识别")
    
    try:
        from analysis.patterns import PatternRecognizer
        
        recognizer = PatternRecognizer()
        patterns = recognizer.recognize_all(data, asset_symbol=symbol)
        
        if patterns and len(patterns) > 0:
            st.success(f"✅ 识别到 {len(patterns)} 个形态")
            
            for pattern in patterns:
                with st.expander(f"{pattern.pattern_type} - {pattern.signal}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**形态类型**: {pattern.pattern_type}")
                        st.write(f"**信号**: {pattern.signal}")
                        st.write(f"**置信度**: {pattern.confidence:.0%}")
                        st.write(f"**描述**: {pattern.description}")
                    
                    with col2:
                        if pattern.signal == 'bullish':
                            st.success("🟢 看涨")
                        elif pattern.signal == 'bearish':
                            st.error("🔴 看跌")
                        else:
                            st.info("➡️ 中性")
        else:
            st.info("暂未识别到明显形态")
        
    except Exception as e:
        st.warning("形态识别功能开发中...")
        logger.debug(f"形态识别: {e}")


def show_comprehensive_analysis(data, symbol):
    """显示综合分析"""
    st.subheader("📋 综合分析报告")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 趋势分析")
        
        # 计算趋势
        returns = data['close'].pct_change()
        avg_return = returns.mean()
        
        if avg_return > 0.001:
            st.success("🟢 上升趋势")
        elif avg_return < -0.001:
            st.error("🔴 下降趋势")
        else:
            st.info("➡️ 横盘整理")
        
        st.write(f"平均日收益: {avg_return:.2%}")
    
    with col2:
        st.markdown("#### 📈 动量分析")
        
        # 最近5日涨跌
        recent_change = (data['close'].iloc[-1] - data['close'].iloc[-6]) / data['close'].iloc[-6]
        
        if recent_change > 0.05:
            st.success("🟢 动量强劲")
        elif recent_change < -0.05:
            st.error("🔴 动量疲软")
        else:
            st.info("➡️ 动量中性")
        
        st.write(f"5日涨跌: {recent_change:.2%}")
    
    with col3:
        st.markdown("#### 📉 波动率分析")
        
        # 计算波动率
        volatility = returns.std() * np.sqrt(252)
        
        if volatility > 0.30:
            st.warning("🔴 高波动")
        elif volatility > 0.15:
            st.info("🟡 中等波动")
        else:
            st.success("🟢 低波动")
        
        st.write(f"年化波动率: {volatility:.2%}")

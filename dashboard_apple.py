"""
Apple级别投资仪表板 V2
参考Meevis Solar Panel的专业设计
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ui.apple_dashboard import AppleDashboard
from ui.modern_components import ModernComponents
from ui.minimal_icons import MinimalIcons, SVGIcons
import random


def show_apple_dashboard(data_manager, signal_generator):
    """显示Apple级别仪表板"""
    
    # Hero Banner with 3D Grid
    AppleDashboard.create_hero_banner(
        title="Personal Quant Assistant",
        subtitle="AI驱动的量化金融分析平台"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 核心指标 - 4列网格
    show_core_metrics_apple(data_manager)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 信号 + 市场数据 - 2列布局
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        show_trading_signal_apple(data_manager, signal_generator)
    
    with col2:
        show_market_overview_apple(data_manager)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 投资组合趋势
    show_portfolio_trend_apple(data_manager)


def show_core_metrics_apple(data_manager):
    """核心指标 - Apple卡片网格"""
    
    # 添加区块标题
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    ">
        <span style="font-size: 28px;">{MinimalIcons.get('diamond')}</span>
        <h3 style="
            font-size: 28px;
            font-weight: 700;
            color: #F5F5F7;
            letter-spacing: -0.02em;
            margin: 0;
        ">核心指标</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取实时数据
    try:
        btc_data = data_manager.get_asset_data('crypto', 'bitcoin', 'realtime')
        eth_data = data_manager.get_asset_data('crypto', 'ethereum', 'realtime')
        etf_data = data_manager.get_asset_data('etf', '513500', 'realtime')
    except:
        btc_data = eth_data = etf_data = None
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Bitcoin卡片
    with col1:
        if btc_data:
            price = btc_data.get('price_usd', 0)
            change = btc_data.get('change_24h', 0)
            trend = 'up' if change > 0 else 'down' if change < 0 else 'neutral'
            
            AppleDashboard.create_metric_card(
                label=f"{MinimalIcons.get('bitcoin')} BITCOIN",
                value=f"{price:,.0f}",
                unit="USD",
                sublabel="24h Change",
                subvalue=f"{change:+.2f}%",
                trend=trend,
                color='warning'
            )
        else:
            st.info(f"{MinimalIcons.get('clock')} Bitcoin")
    
    # Ethereum卡片
    with col2:
        if eth_data:
            price = eth_data.get('price_usd', 0)
            change = eth_data.get('change_24h', 0)
            trend = 'up' if change > 0 else 'down' if change < 0 else 'neutral'
            
            AppleDashboard.create_metric_card(
                label=f"{MinimalIcons.get('ethereum')} ETHEREUM",
                value=f"{price:,.0f}",
                unit="USD",
                sublabel="24h Change",
                subvalue=f"{change:+.2f}%",
                trend=trend,
                color='purple'
            )
        else:
            st.info(f"{MinimalIcons.get('clock')} Ethereum")
    
    # ETF卡片
    with col3:
        if etf_data:
            price = etf_data.get('current', 0)
            change = etf_data.get('change_percent', 0)
            trend = 'up' if change > 0 else 'down' if change < 0 else 'neutral'
            
            AppleDashboard.create_metric_card(
                label=f"{MinimalIcons.get('chart_line')} ETF 513500",
                value=f"{price:.3f}",
                unit="¥",
                sublabel="Today",
                subvalue=f"{change:+.2f}%",
                trend=trend,
                color='teal'
            )
        else:
            st.info(f"{MinimalIcons.get('clock')} ETF 513500")
    
    # 持仓统计卡片
    with col4:
        AppleDashboard.create_metric_card(
            label=f"{MinimalIcons.get('portfolio')} PORTFOLIO",
            value="12",
            unit="Assets",
            sublabel="Active",
            subvalue="8",
            trend='up',
            color='success'
        )


def show_trading_signal_apple(data_manager, signal_generator):
    """交易信号 - Apple面板"""
    
    # 区块标题
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    ">
        <span style="font-size: 26px;">{MinimalIcons.get('signal')}</span>
        <h3 style="
            font-size: 26px;
            font-weight: 700;
            color: #F5F5F7;
            letter-spacing: -0.02em;
            margin: 0;
        ">交易信号</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 获取历史数据用于信号生成
        btc_history = data_manager.get_asset_data('crypto', 'bitcoin', 'history', days=30)
        
        if btc_history is not None and not btc_history.empty:
            # 使用analyze_with_signals方法
            signal_result = signal_generator.analyze_with_signals(btc_history)
            
            if signal_result and 'comprehensive_signal' in signal_result:
                comp_signal = signal_result['comprehensive_signal']
                signal = comp_signal.get('signal', '观望')
                confidence = comp_signal.get('confidence', 0) * 100
                
                # 技术指标
                signals_detail = signal_result.get('signals', {})
                indicators = {
                    '上升': signals_detail.get('up', 0),
                    '金叉': signals_detail.get('golden', 0),
                    '中性': signals_detail.get('neutral', 0),
                }
                
                AppleDashboard.create_signal_panel(
                    signal=signal,
                    confidence=confidence,
                    indicators=indicators
                )
            else:
                st.warning("⚠️ 信号数据不完整")
        else:
            st.info("⏳ 信号生成中...")
    except Exception as e:
        st.error(f"❌ 信号生成失败: {str(e)}")


def show_market_overview_apple(data_manager):
    """市场概览 - Apple卡片"""
    
    # 区块标题
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    ">
        <span style="font-size: 26px;">{MinimalIcons.get('chart_up')}</span>
        <h3 style="
            font-size: 26px;
            font-weight: 700;
            color: #F5F5F7;
            letter-spacing: -0.02em;
            margin: 0;
        ">市场概览</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        btc_data = data_manager.get_asset_data('crypto', 'bitcoin', 'realtime')
        
        if btc_data:
            market_cap = btc_data.get('market_cap', 0) / 1e9  # 十亿
            volume = btc_data.get('volume_24h', 0) / 1e9
            
            # 生成模拟图表数据
            chart_data = [random.uniform(0.85, 1.15) * market_cap for _ in range(20)]
            
            AppleDashboard.create_metric_card(
                label="MARKET CAP",
                value=f"{market_cap:.1f}",
                unit="B",
                sublabel="24h Volume",
                subvalue=f"${volume:.1f}B",
                chart_data=chart_data,
                color='primary'
            )
        else:
            st.info("⏳ 市场数据加载中...")
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")


def show_portfolio_trend_apple(data_manager):
    """投资组合趋势图表"""
    
    # 区块标题
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    ">
        <span style="font-size: 26px;">{MinimalIcons.get('trending_up')}</span>
        <h3 style="
            font-size: 26px;
            font-weight: 700;
            color: #F5F5F7;
            letter-spacing: -0.02em;
            margin: 0;
        ">投资组合趋势 (30天)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # 获取历史数据
        btc_history = data_manager.get_asset_data('crypto', 'bitcoin', 'history', days=30)
        
        if btc_history and not btc_history.empty:
            # 使用Plotly创建图表
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # 主曲线
            fig.add_trace(go.Scatter(
                x=btc_history.index,
                y=btc_history['close'],
                mode='lines',
                name='BTC Price',
                line=dict(
                    color='#0A84FF',
                    width=3,
                    shape='spline'
                ),
                fill='tozeroy',
                fillcolor='rgba(10, 132, 255, 0.1)'
            ))
            
            # 布局 - Apple风格
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(28, 28, 30, 0.6)',
                font=dict(
                    family='-apple-system, BlinkMacSystemFont, SF Pro Display',
                    color='#F5F5F7',
                    size=13
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.06)',
                    gridwidth=1,
                    zeroline=False
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.06)',
                    gridwidth=1,
                    zeroline=False
                ),
                hovermode='x unified',
                height=400,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⏳ 历史数据加载中...")
    except Exception as e:
        st.error(f"❌ 图表生成失败: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Apple Dashboard",
        page_icon="🍎",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .stApp {
        background: #000000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Apple Dashboard Preview")
    
    # 模拟数据
    class MockDataManager:
        def get_asset_data(self, *args, **kwargs):
            import pandas as pd
            if 'history' in args:
                dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                return pd.DataFrame({
                    'close': [random.uniform(90000, 110000) for _ in range(30)]
                }, index=dates)
            return {
                'price_usd': 98765,
                'change_24h': 2.34,
                'market_cap': 1900000000000,
                'volume_24h': 45000000000
            }
    
    class MockSignalGenerator:
        def generate_signal(self, *args, **kwargs):
            return {
                'signal': '买入',
                'confidence': 0.75,
                'signals': {'up': 5, 'golden': 3, 'neutral': 2}
            }
    
    show_apple_dashboard(MockDataManager(), MockSignalGenerator())

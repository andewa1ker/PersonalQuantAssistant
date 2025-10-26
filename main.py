"""
PersonalQuantAssistant - 个人AI量化金融分析师
主程序入口 - Streamlit Web应用 (现代化UI版本)
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import get_config
from data_fetcher.data_manager import DataManager
from analysis.signal_generator import SignalGenerator
from utils.cache_helper import (
    init_session_state, 
    show_cache_manager, 
    show_performance_metrics,
    preload_common_data
)
# 导入现代化UI组件
from ui.modern_theme import ModernTheme
from ui.modern_components import ModernComponents

# 导入AI助手
from ai.ai_assistant import AIAssistant, init_ai_assistant, show_ai_chat_interface

import pandas as pd
import plotly.graph_objects as go
# from utils.logger import setup_logger

# ==================== 数据缓存系统 ====================

@st.cache_resource
def init_signal_generator():
    """初始化信号生成器（缓存）"""
    return SignalGenerator()

@st.cache_resource
def init_data_manager():
    """初始化数据管理器（缓存）"""
    return DataManager()

@st.cache_data(ttl=300)  # 缓存5分钟
def get_cached_realtime_data(data_manager, asset_type, asset_code):
    """缓存实时数据获取"""
    try:
        return data_manager.get_asset_data(asset_type, asset_code, 'realtime')
    except:
        return None

@st.cache_data(ttl=1800)  # 缓存30分钟
def get_cached_history_data(data_manager, asset_type, asset_code, period='1y'):
    """缓存历史数据获取"""
    try:
        return data_manager.get_asset_data(asset_type, asset_code, 'history', period=period)
    except:
        return None

def get_cached_market_data(data_manager):
    """获取市场数据(不使用st.cache_data,避免UnhashableParamError)"""
    try:
        # 获取常用资产的实时数据
        crypto_data = []
        for symbol in ['bitcoin', 'ethereum', 'binancecoin']:
            data = data_manager.get_asset_data('crypto', symbol, 'realtime')
            if data:
                crypto_data.append(data)
        return crypto_data
    except:
        return []

def get_cached_signals(signal_gen, data_manager, assets):
    """获取信号生成结果(不使用st.cache_data)"""
    try:
        signals = []
        for asset_type, asset_code in assets:
            data = get_cached_history_data(data_manager, asset_type, asset_code, '3m')
            if data is not None and len(data) > 0:
                result = signal_gen.analyze_with_signals(data, asset_code)
                if result:
                    signals.append({
                        'asset': asset_code,
                        'type': asset_type,
                        'signal': result['comprehensive_signal']['signal'],
                        'confidence': result['comprehensive_signal']['confidence'],
                        'strength': result['comprehensive_signal']['strength']
                    })
        return signals
    except:
        return []

# 页面配置
st.set_page_config(
    page_title="Personal Quant Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 应用现代化主题
ModernTheme.apply_theme()


def load_app_config():
    """加载应用配置"""
    try:
        config = get_config()
        # logger = setup_logger(config.log_level)
        return config, None  # logger
    except Exception as e:
        st.error(f"配置加载失败: {str(e)}")
        st.stop()


def main():
    """主函数"""
    
    # 初始化会话状态和缓存系统
    init_session_state()
    
    # 加载配置
    config, logger = load_app_config()
    
    # 初始化数据管理器和信号生成器(缓存的)
    data_manager = init_data_manager()
    signal_gen = init_signal_generator()
    
    # 预加载常用数据(后台静默加载)
    preload_common_data(data_manager)
    
    # 侧边栏导航 - 使用简约图标
    from ui.minimal_icons import MinimalIcons
    
    st.sidebar.title(f"{MinimalIcons.get('menu')} 导航菜单")
    page = st.sidebar.radio(
        "选择功能模块",
        [
            f"{MinimalIcons.get('dashboard')} 投资仪表板",
            f"{MinimalIcons.get('ai')} AI投资顾问",
            f"🤖 AI智能预测",
            f"💬 情感分析",
            f"{MinimalIcons.get('grid')} 总览面板",
            f"{MinimalIcons.get('search')} 品种分析",
            f"{MinimalIcons.get('signal')} 策略信号",
            f"{MinimalIcons.get('money')} 投资策略",
            f"{MinimalIcons.get('warning')} 风险管理",
            f"{MinimalIcons.get('database')} 数据导出",
            f"{MinimalIcons.get('settings')} 系统设置",
            f"{MinimalIcons.get('server')} 数据源管理",
        ],
        label_visibility="collapsed"
    )
    
    # 显示缓存管理工具
    show_cache_manager()
    show_performance_metrics()
    
    # 显示版本信息
    st.sidebar.markdown("---")
    st.sidebar.caption(f"版本: {config.app_version}")
    st.sidebar.caption("© 2025 Personal Quant Assistant")
    
    # 根据选择显示不同页面(匹配新图标)
    if MinimalIcons.get('dashboard') in page or "投资仪表板" in page:
        # Apple级别仪表板
        from dashboard_apple import show_apple_dashboard
        show_apple_dashboard(data_manager, signal_gen)
    elif MinimalIcons.get('ai') in page or "AI投资顾问" in page:
        # 初始化AI助手
        ai_assistant = init_ai_assistant(config.deepseek_api_key)
        if ai_assistant:
            # 获取当前市场数据作为上下文
            context = {
                'crypto_data': get_cached_market_data(data_manager),
                'timestamp': datetime.now().isoformat()
            }
            show_ai_chat_interface(ai_assistant, context)
        else:
            st.error("⚠️ AI助手未配置")
            st.info("""
            **配置步骤：**
            1. 获取DeepSeek API Key: https://platform.deepseek.com
            2. 在 `config/api_keys.yaml` 中配置：
               ```yaml
               deepseek:
                 api_key: "your_api_key_here"
               ```
            3. 重启应用
            """)
    elif "AI智能预测" in page:
        from src.ui.ai_prediction_page import show_ai_prediction_page
        show_ai_prediction_page()
    elif "情感分析" in page:
        from src.ui.sentiment_page import show_sentiment_page
        show_sentiment_page()
    elif "总览面板" in page:
        from overview_enhanced import show_overview_enhanced
        show_overview_enhanced(config, data_manager)
    elif "品种分析" in page:
        from analysis_enhanced import show_analysis_enhanced
        show_analysis_enhanced(config, data_manager)
    elif "策略信号" in page:
        from signals_enhanced import show_signals_enhanced
        show_signals_enhanced(config, data_manager, signal_gen)
    elif "投资策略" in page:
        from strategy_page import show_strategy_page
        show_strategy_page(config)
    elif "风险管理" in page:
        from risk_enhanced import show_risk_enhanced
        show_risk_enhanced(data_manager, config)
    elif "数据导出" in page:
        from export_module import show_export_functions
        show_export_functions(data_manager, config)
    elif "系统设置" in page:
        from settings_enhanced import show_settings_enhanced
        show_settings_enhanced(config)
    elif "数据源管理" in page:
        from datasource_manager import show_datasource_manager
        show_datasource_manager()


def show_overview_page(config):
    """显示总览面板"""
    st.header(f"{MinimalIcons.get('grid')} 投资组合总览")
    
    # 初始化数据管理器
    data_manager = init_data_manager()
    
    # 添加刷新按钮
    col_refresh, col_space = st.columns([1, 5])
    with col_refresh:
        if st.button("� 刷新数据"):
            st.cache_resource.clear()
            st.rerun()
    
    # 获取投资组合数据
    with st.spinner("正在获取数据..."):
        try:
            portfolio = data_manager.get_portfolio_data()
            
            # 指标卡片
            col1, col2, col3, col4 = st.columns(4)
            
            # ETF数据
            etf_data = portfolio.get('etf_513500')
            crypto_data = portfolio.get('crypto')
            
            with col1:
                if etf_data:
                    st.metric(
                        label="513500 ETF",
                        value=f"¥{etf_data['price']:.3f}",
                        delta=f"{etf_data['change_pct']:.2f}%",
                    )
                else:
                    st.metric(label="513500 ETF", value="获取中...")
            
            with col2:
                if crypto_data is not None and len(crypto_data) > 0:
                    btc = crypto_data[crypto_data['symbol'] == 'BTC']
                    if len(btc) > 0:
                        btc_row = btc.iloc[0]
                        st.metric(
                            label="BTC",
                            value=f"${btc_row['price_usd']:,.0f}",
                            delta=f"{btc_row['change_24h']:.2f}%",
                        )
                    else:
                        st.metric(label="BTC", value="获取中...")
                else:
                    st.metric(label="BTC", value="获取中...")
            
            with col3:
                if crypto_data is not None and len(crypto_data) > 0:
                    eth = crypto_data[crypto_data['symbol'] == 'ETH']
                    if len(eth) > 0:
                        eth_row = eth.iloc[0]
                        st.metric(
                            label="ETH",
                            value=f"${eth_row['price_usd']:,.0f}",
                            delta=f"{eth_row['change_24h']:.2f}%",
                        )
                    else:
                        st.metric(label="ETH", value="获取中...")
                else:
                    st.metric(label="ETH", value="获取中...")
            
            with col4:
                # 恐惧贪婪指数
                fng = data_manager.get_fear_greed_index()
                if fng:
                    st.metric(
                        label="恐惧贪婪指数",
                        value=f"{fng['value']}",
                        delta=fng['classification'],
                    )
                else:
                    st.metric(label="恐惧贪婪指数", value="获取中...")
            
            st.markdown("---")
            
            # 详细数据表格
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.subheader("📊 ETF详情")
                if etf_data:
                    etf_df = pd.DataFrame([{
                        '名称': etf_data['name'],
                        '最新价': f"¥{etf_data['price']:.3f}",
                        '涨跌幅': f"{etf_data['change_pct']:.2f}%",
                        '成交量': f"{etf_data['volume']:,.0f}",
                        '成交额': f"{etf_data['amount']/1e8:.2f}亿"
                    }])
                    st.dataframe(etf_df, use_container_width=True, hide_index=True)
                else:
                    st.info("暂无数据")
            
            with col_right:
                st.subheader("💰 加密货币详情")
                if crypto_data is not None and len(crypto_data) > 0:
                    crypto_display = crypto_data[['symbol', 'price_usd', 'change_24h', 'market_cap']].copy()
                    crypto_display.columns = ['币种', '价格(USD)', '24h涨跌%', '市值(USD)']
                    crypto_display['价格(USD)'] = crypto_display['价格(USD)'].apply(lambda x: f"${x:,.2f}")
                    crypto_display['24h涨跌%'] = crypto_display['24h涨跌%'].apply(lambda x: f"{x:.2f}%")
                    crypto_display['市值(USD)'] = crypto_display['市值(USD)'].apply(lambda x: f"${x/1e9:.2f}B" if x else "N/A")
                    st.dataframe(crypto_display, use_container_width=True, hide_index=True)
                else:
                    st.info("暂无数据")
            
            # 显示更新时间
            st.caption(f"数据更新时间: {portfolio['timestamp']}")
            
        except Exception as e:
            st.error(f"获取数据失败: {str(e)}")
            st.info("💡 请检查网络连接和API配置")


def show_analysis_page(config):
    """显示品种分析页面"""
    st.header("🔍 品种深度分析")
    
    # 初始化数据管理器
    data_manager = init_data_manager()
    
    # 获取启用的资产
    enabled_assets = config.get_enabled_assets()
    
    if not enabled_assets:
        st.warning("⚠️ 没有启用的资产，请在配置文件中启用资产")
        return
    
    # 资产选择
    asset_options = {
        'etf_513500': '513500 标普500ETF',
        'crypto': '加密货币'
    }
    
    selected_asset = st.selectbox(
        "选择分析品种",
        list(asset_options.keys()),
        format_func=lambda x: asset_options.get(x, x)
    )
    
    # 根据选择的资产类型显示数据
    if selected_asset == 'etf_513500':
        show_etf_analysis(data_manager, config)
    elif selected_asset == 'crypto':
        show_crypto_analysis(data_manager, config)


def show_etf_analysis(data_manager, config):
    """显示ETF分析"""
    symbol = '513500'
    signal_gen = init_signal_generator()
    
    with st.spinner("正在获取ETF数据..."):
        try:
            # 获取实时数据
            realtime = data_manager.get_asset_data('etf', symbol, 'realtime')
            
            # 获取历史数据 (3个月用于技术分析)
            history = data_manager.get_asset_data('etf', symbol, 'history', period='3mo')
            
            tab1, tab2, tab3, tab4 = st.tabs(["📈 实时行情", "📊 历史走势", "🔬 技术分析", "📋 估值数据"])
            
            with tab1:
                if realtime:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("最新价", f"¥{realtime['price']:.3f}", f"{realtime['change_pct']:.2f}%")
                    with col2:
                        st.metric("成交量", f"{realtime['volume']/1e4:.2f}万")
                    with col3:
                        st.metric("成交额", f"{realtime['amount']/1e8:.2f}亿")
                    
                    # 详细信息
                    st.subheader("详细信息")
                    info_df = pd.DataFrame([{
                        '开盘价': f"¥{realtime['open']:.3f}",
                        '最高价': f"¥{realtime['high']:.3f}",
                        '最低价': f"¥{realtime['low']:.3f}",
                        '昨收价': f"¥{realtime['pre_close']:.3f}",
                        '涨跌额': f"¥{realtime['change']:.3f}"
                    }])
                    st.dataframe(info_df, use_container_width=True, hide_index=True)
                else:
                    st.error("无法获取实时数据")
            
            with tab2:
                if history is not None and len(history) > 0:
                    st.subheader(f"最近30天价格走势")
                    
                    # 使用Plotly绘制K线图
                    fig = go.Figure(data=[go.Candlestick(
                        x=history['date'],
                        open=history['open'],
                        high=history['high'],
                        low=history['low'],
                        close=history['close'],
                        name='K线'
                    )])
                    
                    fig.update_layout(
                        title=f'{symbol} K线图',
                        yaxis_title='价格 (¥)',
                        xaxis_title='日期',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 显示数据表
                    st.subheader("历史数据")
                    display_df = history.tail(10).copy()
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.error("无法获取历史数据")
            
            with tab3:
                # 技术分析页签
                if history is not None and len(history) > 20:
                    st.subheader("🔬 技术指标分析")
                    
                    with st.spinner("正在分析技术指标..."):
                        try:
                            # 生成完整分析报告
                            analysis_report = signal_gen.analyze_with_signals(history)
                            
                            if 'signals' in analysis_report:
                                signals = analysis_report['signals']
                                
                                # 交易信号卡片
                                st.markdown("### 📊 交易信号")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    signal_color = {
                                        '强烈买入': '🟢', '买入': '🟢',
                                        '观望': '🟡',
                                        '卖出': '🔴', '强烈卖出': '🔴'
                                    }
                                    signal_emoji = signal_color.get(signals['signal'], '⚪')
                                    st.metric(
                                        label="当前信号",
                                        value=f"{signal_emoji} {signals['signal']}"
                                    )
                                
                                with col2:
                                    confidence_emoji = {'高': '⭐⭐⭐', '中': '⭐⭐', '低': '⭐'}
                                    st.metric(
                                        label="信心度",
                                        value=f"{signals['confidence']}"
                                    )
                                    st.caption(confidence_emoji.get(signals['confidence'], '⭐'))
                                
                                with col3:
                                    st.metric(
                                        label="信号强度",
                                        value=signals['total_strength'],
                                        delta=f"买{signals['buy_signals']}/卖{signals['sell_signals']}"
                                    )
                                
                                # 信号依据
                                st.markdown("### 📌 信号依据")
                                if signals.get('reasons'):
                                    for reason in signals['reasons'][:5]:
                                        st.write(f"• {reason}")
                                else:
                                    st.info("暂无详细依据")
                                
                                # 各指标详情
                                st.markdown("---")
                                col_left, col_right = st.columns(2)
                                
                                with col_left:
                                    st.markdown("### 📊 技术指标")
                                    
                                    analyzed_data = analysis_report.get('data')
                                    if analyzed_data is not None and len(analyzed_data) > 0:
                                        latest = analyzed_data.iloc[-1]
                                        
                                        # MA指标
                                        if 'MA5' in latest:
                                            with st.expander("**移动平均线 (MA)**", expanded=True):
                                                ma_df = pd.DataFrame({
                                                    '周期': ['MA5', 'MA10', 'MA20', 'MA60'],
                                                    '数值': [
                                                        f"¥{latest.get('MA5', 0):.3f}",
                                                        f"¥{latest.get('MA10', 0):.3f}",
                                                        f"¥{latest.get('MA20', 0):.3f}",
                                                        f"¥{latest.get('MA60', 0):.3f}"
                                                    ]
                                                })
                                                st.dataframe(ma_df, use_container_width=True, hide_index=True)
                                        
                                        # RSI指标
                                        if 'RSI' in latest:
                                            with st.expander("**相对强弱指标 (RSI)**"):
                                                rsi_val = latest['RSI']
                                                rsi_status = "超买" if rsi_val > 70 else "超卖" if rsi_val < 30 else "正常"
                                                col_a, col_b = st.columns(2)
                                                with col_a:
                                                    st.metric("RSI值", f"{rsi_val:.2f}")
                                                with col_b:
                                                    st.metric("状态", rsi_status)
                                        
                                        # KDJ指标
                                        if 'K' in latest:
                                            with st.expander("**KDJ指标**"):
                                                kdj_df = pd.DataFrame({
                                                    '指标': ['K', 'D', 'J'],
                                                    '数值': [
                                                        f"{latest.get('K', 0):.2f}",
                                                        f"{latest.get('D', 0):.2f}",
                                                        f"{latest.get('J', 0):.2f}"
                                                    ]
                                                })
                                                st.dataframe(kdj_df, use_container_width=True, hide_index=True)
                                
                                with col_right:
                                    st.markdown("### 📈 趋势分析")
                                    
                                    trend_info = analysis_report.get('trend_analysis', {}).get('trend', {})
                                    if trend_info:
                                        with st.expander("**当前趋势**", expanded=True):
                                            st.write(f"**趋势方向:** {trend_info.get('trend', 'N/A')}")
                                            st.write(f"**均线排列:** {trend_info.get('ma_alignment', 'N/A')}")
                                            st.write(f"**价格变化:** {trend_info.get('price_change', 0):.2f}%")
                                        
                                        # 支撑阻力位
                                        sr_levels = analysis_report.get('trend_analysis', {}).get('support_resistance', {})
                                        if sr_levels and (sr_levels.get('support') or sr_levels.get('resistance')):
                                            with st.expander("**支撑与阻力位**"):
                                                col_s, col_r = st.columns(2)
                                                with col_s:
                                                    st.write("**支撑位:**")
                                                    for level in sr_levels.get('support', [])[:3]:
                                                        st.write(f"¥{level:.3f}")
                                                    if not sr_levels.get('support'):
                                                        st.caption("未检测到")
                                                
                                                with col_r:
                                                    st.write("**阻力位:**")
                                                    for level in sr_levels.get('resistance', [])[:3]:
                                                        st.write(f"¥{level:.3f}")
                                                    if not sr_levels.get('resistance'):
                                                        st.caption("未检测到")
                                    
                                    # 波动率分析
                                    vol_info = analysis_report.get('volatility_analysis', {}).get('historical_volatility', {})
                                    if vol_info:
                                        with st.expander("**波动率分析**"):
                                            st.metric(
                                                "当前波动率",
                                                f"{vol_info.get('current_volatility', 0):.2f}%"
                                            )
                                            st.caption(f"级别: {vol_info.get('volatility_level', 'N/A')}")
                                
                                # MACD图表
                                if analyzed_data is not None and 'MACD' in analyzed_data.columns:
                                    st.markdown("---")
                                    st.markdown("### 📉 MACD指标图")
                                    
                                    fig_macd = go.Figure()
                                    
                                    # MACD线
                                    fig_macd.add_trace(go.Scatter(
                                        x=analyzed_data['date'],
                                        y=analyzed_data['MACD'],
                                        name='MACD',
                                        line=dict(color='blue', width=2)
                                    ))
                                    
                                    # Signal线
                                    fig_macd.add_trace(go.Scatter(
                                        x=analyzed_data['date'],
                                        y=analyzed_data['MACD_Signal'],
                                        name='Signal',
                                        line=dict(color='orange', width=2)
                                    ))
                                    
                                    # 柱状图
                                    colors = ['green' if val > 0 else 'red' for val in analyzed_data['MACD_Hist']]
                                    fig_macd.add_trace(go.Bar(
                                        x=analyzed_data['date'],
                                        y=analyzed_data['MACD_Hist'],
                                        name='Histogram',
                                        marker_color=colors
                                    ))
                                    
                                    fig_macd.update_layout(
                                        title='MACD指标',
                                        height=400,
                                        xaxis_title='日期',
                                        yaxis_title='MACD值'
                                    )
                                    
                                    st.plotly_chart(fig_macd, use_container_width=True)
                            
                            else:
                                st.error("技术分析失败，请稍后重试")
                        
                        except Exception as e:
                            st.error(f"技术分析出错: {str(e)}")
                            with st.expander("查看错误详情"):
                                import traceback
                                st.code(traceback.format_exc())
                else:
                    st.warning("⚠️ 数据不足，需要至少20天的历史数据进行技术分析")
                    st.info("💡 请稍后再试，或检查网络连接")
            
            with tab4:
                valuation = data_manager.get_asset_data('etf', symbol, 'valuation')
                if valuation:
                    col1, col2 = st.columns(2)
                    with col1:
                        pe = valuation.get('pe')
                        st.metric("市盈率 (PE)", f"{pe:.2f}" if pe else "N/A")
                    with col2:
                        pb = valuation.get('pb')
                        st.metric("市净率 (PB)", f"{pb:.2f}" if pb else "N/A")
                else:
                    st.info("暂无估值数据")
        
        except Exception as e:
            st.error(f"获取数据失败: {str(e)}")


def show_crypto_analysis(data_manager, config):
    """显示加密货币分析"""
    signal_gen = init_signal_generator()
    crypto_config = config.get_asset_config('crypto')
    symbols = crypto_config.get('symbols', ['bitcoin', 'ethereum']) if crypto_config else ['bitcoin']
    
    selected_crypto = st.selectbox("选择币种", symbols)
    
    with st.spinner(f"正在获取{selected_crypto}数据..."):
        try:
            # 获取实时数据
            realtime = data_manager.get_asset_data('crypto', selected_crypto, 'realtime')
            
            # 获取历史数据 (90天用于技术分析)
            history = data_manager.get_asset_data('crypto', selected_crypto, 'history', days=90)
            
            tab1, tab2, tab3 = st.tabs(["📈 实时行情", "📊 历史走势", "🔬 技术分析"])
            
            with tab1:
                if realtime:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("USD价格", f"${realtime['price_usd']:,.2f}", f"{realtime['change_24h']:.2f}%")
                    with col2:
                        st.metric("CNY价格", f"¥{realtime['price_cny']:,.2f}")
                    with col3:
                        st.metric("24h成交量", f"${realtime['volume_24h']/1e9:.2f}B")
                    
                    st.metric("市值", f"${realtime['market_cap']/1e9:.2f}B" if realtime['market_cap'] else "N/A")
                else:
                    st.error("无法获取实时数据")
            
            with tab2:
                if history is not None and len(history) > 0:
                    st.subheader(f"{selected_crypto}最近30天价格走势")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=history['date'],
                        y=history['price'],
                        mode='lines',
                        name='价格',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f'{selected_crypto} 价格走势',
                        yaxis_title='价格 (USD)',
                        xaxis_title='日期',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 显示数据表
                    st.subheader("历史数据")
                    display_df = history.tail(10).copy()
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                    display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.error("无法获取历史数据")
            
            with tab3:
                # 技术分析页签
                if history is not None and len(history) > 20:
                    # 准备数据：加密货币数据需要转换为标准格式
                    if 'price' in history.columns:
                        analysis_data = history.rename(columns={'price': 'close'}).copy()
                        # 为加密货币生成OHLC数据（简化处理）
                        if 'high' not in analysis_data.columns:
                            analysis_data['high'] = analysis_data['close'] * 1.02
                            analysis_data['low'] = analysis_data['close'] * 0.98
                            analysis_data['open'] = analysis_data['close'].shift(1).fillna(analysis_data['close'])
                        if 'volume' not in analysis_data.columns:
                            analysis_data['volume'] = 1000000  # 默认值
                    else:
                        analysis_data = history
                    
                    st.subheader("🔬 技术指标分析")
                    
                    with st.spinner("正在分析技术指标..."):
                        try:
                            # 生成完整分析报告
                            analysis_report = signal_gen.analyze_with_signals(analysis_data)
                            
                            if 'signals' in analysis_report:
                                signals = analysis_report['signals']
                                
                                # 交易信号卡片
                                st.markdown("### 📊 交易信号")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    signal_color = {
                                        '强烈买入': '🟢', '买入': '🟢',
                                        '观望': '🟡',
                                        '卖出': '🔴', '强烈卖出': '🔴'
                                    }
                                    signal_emoji = signal_color.get(signals['signal'], '⚪')
                                    st.metric("当前信号", f"{signal_emoji} {signals['signal']}")
                                
                                with col2:
                                    st.metric("信心度", f"{signals['confidence']}")
                                
                                with col3:
                                    st.metric("信号强度", signals['total_strength'])
                                
                                # 信号依据
                                st.markdown("### 📌 信号依据")
                                for reason in signals.get('reasons', [])[:5]:
                                    st.write(f"• {reason}")
                                
                                # 技术指标
                                st.markdown("---")
                                analyzed_data = analysis_report.get('data')
                                if analyzed_data is not None and len(analyzed_data) > 0:
                                    latest = analyzed_data.iloc[-1]
                                    
                                    col_l, col_r = st.columns(2)
                                    with col_l:
                                        if 'RSI' in latest:
                                            rsi_val = latest['RSI']
                                            rsi_status = "超买" if rsi_val > 70 else "超卖" if rsi_val < 30 else "正常"
                                            st.metric("RSI指标", f"{rsi_val:.2f}", rsi_status)
                                        
                                        if 'MACD' in latest:
                                            st.metric("MACD", f"{latest['MACD']:.4f}")
                                    
                                    with col_r:
                                        trend_info = analysis_report.get('trend_analysis', {}).get('trend', {})
                                        if trend_info:
                                            st.metric("当前趋势", trend_info.get('trend', 'N/A'))
                                            st.metric("价格变化", f"{trend_info.get('price_change', 0):.2f}%")
                            
                            else:
                                st.error("技术分析失败")
                        
                        except Exception as e:
                            st.error(f"技术分析出错: {str(e)}")
                else:
                    st.warning("数据不足，需要至少20天的历史数据")
        
        except Exception as e:
            st.error(f"获取数据失败: {str(e)}")


def show_signals_page(config):
    """显示策略信号页面"""
    st.header("🎯 策略信号中心")
    
    data_manager = init_data_manager()
    signal_gen = init_signal_generator()
    
    st.markdown("### 📊 实时交易信号")
    
    # 获取启用的资产
    enabled_assets = config.get_enabled_assets()
    
    if not enabled_assets:
        st.warning("⚠️ 没有启用的资产")
        return
    
    # 添加刷新按钮
    if st.button("🔄 刷新信号"):
        st.cache_resource.clear()
        st.rerun()
    
    with st.spinner("正在生成交易信号..."):
        signal_results = []
        
        # ETF信号
        if 'etf_513500' in enabled_assets:
            try:
                history = data_manager.get_asset_data('etf', '513500', 'history', period='3mo')
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
            except Exception as e:
                st.error(f"获取513500信号失败: {e}")
        
        # 加密货币信号
        crypto_config = config.get_asset_config('crypto')
        if crypto_config:
            symbols = crypto_config.get('symbols', ['bitcoin', 'ethereum'])
            for symbol in symbols[:3]:  # 最多3个
                try:
                    history = data_manager.get_asset_data('crypto', symbol, 'history', days=90)
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
                except Exception as e:
                    st.warning(f"获取{symbol}信号失败: {e}")
    
    # 显示信号表格
    if signal_results:
        st.markdown("---")
        
        # 将信号转换为DataFrame
        signals_df = pd.DataFrame(signal_results)
        
        # 使用颜色标记信号
        def highlight_signal(row):
            if '买入' in row['信号']:
                return ['background-color: #d4edda'] * len(row)
            elif '卖出' in row['信号']:
                return ['background-color: #f8d7da'] * len(row)
            else:
                return ['background-color: #fff3cd'] * len(row)
        
        st.dataframe(
            signals_df.style.apply(highlight_signal, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # 显示详细信号
        st.markdown("---")
        st.markdown("### 📋 详细分析")
        
        for idx, result in enumerate(signal_results):
            with st.expander(f"{result['品种']} - {result['信号']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("价格", result['当前价格'])
                with col2:
                    st.metric("信号", result['信号'])
                with col3:
                    st.metric("信心度", result['信心度'])
                
                st.write(f"**趋势:** {result['趋势']}")
                st.write(f"**信号强度:** {result['强度']}")
    else:
        st.warning("暂无可用的交易信号")


# 原有的show_risk_page已移至risk_page.py模块
# def show_risk_page(config):
#     """显示风险管理页面 - 已弃用,使用risk_page.show_risk_page"""
#     pass


def show_settings_page(config):
    """显示系统设置页面"""
    st.header("⚙️ 系统设置")
    
    st.info("💡 设置页面正在开发中...")
    
    tab1, tab2, tab3 = st.tabs(["🔑 API配置", "📊 策略参数", "⚠️ 风险参数"])
    
    with tab1:
        st.subheader("API密钥配置")
        st.warning("⚠️ 请勿在此处输入真实API密钥，请编辑 config/api_keys.yaml 文件")
        
        with st.expander("Tushare配置"):
            tushare_token = st.text_input("Tushare Token", type="password")
        
        with st.expander("CoinGecko配置"):
            st.write("CoinGecko免费API无需密钥")
    
    with tab2:
        st.subheader("策略参数调整")
        
        st.write("**均线策略**")
        ma_short = st.slider("短期均线周期", 5, 60, 20)
        ma_long = st.slider("长期均线周期", 20, 250, 60)
        
        st.write("**RSI策略**")
        rsi_oversold = st.slider("超卖阈值", 10, 40, 30)
        rsi_overbought = st.slider("超买阈值", 60, 90, 70)
    
    with tab3:
        st.subheader("风险参数设置")
        
        max_pos = st.slider("单品种最大仓位 (%)", 10, 100, 50)
        max_dd = st.slider("最大回撤限制 (%)", 5, 50, 20)
        
        if st.button("保存设置"):
            st.success("✅ 设置已保存（演示功能）")


if __name__ == "__main__":
    main()

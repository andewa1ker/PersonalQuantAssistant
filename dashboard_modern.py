"""
现代化投资仪表板页面
Apple风格设计：简洁、优雅、流畅的动画效果
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ui.modern_theme import ModernTheme
from ui.modern_components import ModernComponents


def show_modern_dashboard(data_manager, config):
    """显示现代化仪表板"""
    
    # Hero区域
    ModernTheme.create_hero_section(
        "投资仪表板",
        "实时监控您的投资组合表现"
    )
    
    # 快速刷新按钮
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.button("🔄 刷新", key="refresh_dashboard"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        auto_refresh = st.toggle("自动", key="auto_refresh")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== 核心指标卡片 =====
    show_core_metrics(data_manager)
    
    ModernTheme.create_divider()
    
    # ===== 市场实时行情 =====
    show_market_realtime(data_manager)
    
    ModernTheme.create_divider()
    
    # ===== 投资组合与信号 =====
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_portfolio_chart(data_manager)
    
    with col2:
        show_trading_signals(data_manager)
    
    ModernTheme.create_divider()
    
    # ===== 市场情绪与新闻 =====
    col1, col2 = st.columns(2)
    
    with col1:
        show_market_sentiment()
    
    with col2:
        show_market_alerts()


def show_core_metrics(data_manager):
    """显示核心指标"""
    st.markdown("### 💎 核心指标")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 获取实时数据
    try:
        btc_data = data_manager.get_asset_data('crypto', 'bitcoin', 'realtime')
        eth_data = data_manager.get_asset_data('crypto', 'ethereum', 'realtime')
        etf_data = data_manager.get_asset_data('etf', '513500', 'realtime')
    except:
        btc_data = eth_data = etf_data = None
    
    # 指标网格
    metrics = []
    
    if btc_data:
        metrics.append({
            'label': 'Bitcoin',
            'value': f"${btc_data.get('price_usd', 0):,.0f}",
            'change': f"{btc_data.get('change_24h', 0):+.2f}%",
            'icon': '₿'
        })
    
    if eth_data:
        metrics.append({
            'label': 'Ethereum',
            'value': f"${eth_data.get('price_usd', 0):,.0f}",
            'change': f"{eth_data.get('change_24h', 0):+.2f}%",
            'icon': 'Ξ'
        })
    
    if etf_data:
        metrics.append({
            'label': 'ETF 513500',
            'value': f"¥{etf_data.get('current', 0):.3f}",
            'change': f"{etf_data.get('change_percent', 0):+.2f}%",
            'icon': '📈'
        })
    
    # 添加组合指标
    metrics.append({
        'label': '持仓品种',
        'value': '12',
        'change': '+2',
        'icon': '💼'
    })
    
    ModernComponents.metric_grid(metrics, columns=4)


def show_market_realtime(data_manager):
    """显示市场实时行情"""
    st.markdown("### 🌐 市场实时行情")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 获取市场数据
    try:
        btc_data = data_manager.get_asset_data('crypto', 'bitcoin', 'realtime')
        eth_data = data_manager.get_asset_data('crypto', 'ethereum', 'realtime')
        bnb_data = data_manager.get_asset_data('crypto', 'binancecoin', 'realtime')
    except:
        btc_data = eth_data = bnb_data = None
    
    # 价格卡片网格
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if btc_data:
            ModernComponents.price_card(
                symbol="BTC",
                name="Bitcoin",
                price=btc_data.get('price_usd', 0),
                change_24h=btc_data.get('change_24h', 0),
                volume_24h=btc_data.get('volume_24h'),
                market_cap=btc_data.get('market_cap'),
                icon="₿"
            )
        else:
            st.info("Bitcoin数据加载中...")
    
    with col2:
        if eth_data:
            ModernComponents.price_card(
                symbol="ETH",
                name="Ethereum",
                price=eth_data.get('price_usd', 0),
                change_24h=eth_data.get('change_24h', 0),
                volume_24h=eth_data.get('volume_24h'),
                market_cap=eth_data.get('market_cap'),
                icon="Ξ"
            )
        else:
            st.info("Ethereum数据加载中...")
    
    with col3:
        if bnb_data:
            ModernComponents.price_card(
                symbol="BNB",
                name="Binance Coin",
                price=bnb_data.get('price_usd', 0),
                change_24h=bnb_data.get('change_24h', 0),
                volume_24h=bnb_data.get('volume_24h'),
                market_cap=bnb_data.get('market_cap'),
                icon="🔶"
            )
        else:
            st.info("BNB数据加载中...")


def show_portfolio_chart(data_manager):
    """显示投资组合图表"""
    st.markdown("### 📊 投资组合")
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        # 获取历史数据
        btc_hist = data_manager.get_asset_data('crypto', 'bitcoin', 'history', days=30)
        
        if btc_hist is not None and len(btc_hist) > 0:
            # 创建现代化图表
            chart_data = {
                'x': btc_hist.index.tolist(),
                'y': btc_hist['close'].tolist() if 'close' in btc_hist.columns else btc_hist['price'].tolist(),
                'name': 'Bitcoin'
            }
            
            fig = ModernComponents.create_modern_chart(
                data=chart_data,
                chart_type='area',
                title='投资组合价值走势 (30天)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            ModernComponents.alert_box(
                "暂无历史数据，请稍后再试",
                type='info'
            )
    
    except Exception as e:
        ModernComponents.alert_box(
            f"数据加载失败: {str(e)}",
            type='danger'
        )


def show_trading_signals(data_manager):
    """显示交易信号"""
    st.markdown("### 🎯 交易信号")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 示例信号
    ModernComponents.signal_indicator(
        signal="买入",
        confidence=75,
        signals_detail={
            'MA趋势': '上升',
            'MACD': '金叉',
            'RSI': '46.3',
            'KDJ': '中性'
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 时间线
    st.markdown("#### 📅 最近信号")
    st.markdown("<br>", unsafe_allow_html=True)
    
    ModernComponents.timeline_item(
        time="2小时前",
        title="BTC买入信号",
        description="多项技术指标显示上涨趋势",
        type="success"
    )
    
    ModernComponents.timeline_item(
        time="5小时前",
        title="ETH持有建议",
        description="短期震荡，建议持有观望",
        type="info"
    )
    
    ModernComponents.timeline_item(
        time="昨天",
        title="风险提示",
        description="市场波动加剧，注意风险控制",
        type="warning"
    )


def show_market_sentiment():
    """显示市场情绪"""
    st.markdown("### 😊 市场情绪")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 恐惧贪婪指数
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ModernTheme.create_progress_ring(40, "恐惧贪婪指数")
    
    with col2:
        st.markdown("""
        <div style="padding: 20px;">
            <h4 style="color: var(--text-primary); margin-bottom: 16px;">市场处于恐惧状态</h4>
            <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6;">
                当前指数为 <strong style="color: #FF9500;">40</strong>，
                表明投资者情绪偏向谨慎。历史数据显示，
                这通常是逢低买入的好时机。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 市场统计
    metrics = [
        {'label': '24h交易量', 'value': '$1.2T', 'change': '+5.2%', 'icon': '💹'},
        {'label': '活跃币种', 'value': '2,456', 'change': '+12', 'icon': '🪙'},
        {'label': '总市值', 'value': '$2.8T', 'change': '+2.1%', 'icon': '💰'},
    ]
    
    ModernComponents.metric_grid(metrics, columns=3)


def show_market_alerts():
    """显示市场预警"""
    st.markdown("### ⚠️ 市场预警")
    st.markdown("<br>", unsafe_allow_html=True)
    
    ModernComponents.alert_box(
        "BTC突破关键阻力位 $115,000，可能继续上涨",
        type='success'
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ModernComponents.alert_box(
        "ETH交易量异常增加，注意市场变化",
        type='warning'
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ModernComponents.alert_box(
        "多个技术指标显示超买信号，建议谨慎",
        type='info'
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 快速操作
    st.markdown("#### ⚡ 快速操作")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("📊 查看详细分析", use_container_width=True)
        st.button("⚙️ 调整策略", use_container_width=True)
    
    with col2:
        st.button("📤 导出报告", use_container_width=True)
        st.button("🔔 设置提醒", use_container_width=True)


# 使用示例
if __name__ == "__main__":
    st.set_page_config(page_title="现代化仪表板", layout="wide")
    
    ModernTheme.apply_theme()
    
    # 模拟数据管理器
    class MockDataManager:
        def get_asset_data(self, asset_type, symbol, data_type, **kwargs):
            return {
                'price_usd': 113655.00,
                'change_24h': 2.5,
                'volume_24h': 45000000000,
                'market_cap': 2200000000000
            }
    
    show_modern_dashboard(MockDataManager(), None)

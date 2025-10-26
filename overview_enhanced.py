"""
增强版投资组合总览页面
包含数据可视化、实时更新、资产配置分析
性能优化: 使用缓存系统提升加载速度
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入缓存辅助函数
from utils.cache_helper import (
    get_realtime_with_cache,
    get_history_with_cache,
    batch_get_realtime,
    get_market_overview_cache,
    clear_cache
)


def show_overview_enhanced(config, data_manager):
    """显示增强版总览页面"""
    st.header("📈 投资组合总览")
    
    # 顶部控制栏
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        auto_refresh = st.checkbox("🔄 自动刷新", value=False, key="auto_refresh")
    
    with col2:
        refresh_interval = st.selectbox(
            "刷新间隔",
            [30, 60, 300],
            format_func=lambda x: f"{x}秒" if x < 60 else f"{x//60}分钟",
            key="refresh_interval"
        )
    
    with col3:
        view_mode = st.selectbox(
            "视图模式",
            ["简洁", "详细", "专业"],
            key="view_mode"
        )
    
    with col4:
        if st.button("🔄", help="立即刷新"):
            # 清除缓存并重新加载
            st.cache_data.clear()
            clear_cache()
            st.rerun()
    
    # 使用缓存获取市场数据
    with st.spinner("正在加载市场数据..."):
        market_data = get_market_overview_cache(data_manager)
    with st.spinner("正在加载数据..."):
        try:
            portfolio = data_manager.get_portfolio_data()
            
            # 核心指标卡片
            show_key_metrics(portfolio, data_manager)
            
            st.markdown("---")
            
            # 根据视图模式显示不同内容
            if view_mode == "简洁":
                show_simple_view(portfolio, data_manager)
            elif view_mode == "详细":
                show_detailed_view(portfolio, data_manager)
            else:  # 专业
                show_professional_view(portfolio, data_manager)
            
        except Exception as e:
            st.error(f"❌ 数据加载失败: {str(e)}")
            logger.error(f"总览页面错误: {e}", exc_info=True)


def show_key_metrics(portfolio, data_manager):
    """显示核心指标卡片"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    etf_data = portfolio.get('etf_513500')
    crypto_data = portfolio.get('crypto')
    
    # ETF 513500
    with col1:
        if etf_data:
            st.metric(
                label="📊 513500 ETF",
                value=f"¥{etf_data['price']:.3f}",
                delta=f"{etf_data['change_pct']:.2f}%",
                delta_color="normal"
            )
        else:
            st.metric(label="📊 513500 ETF", value="—")
    
    # BTC
    with col2:
        if crypto_data is not None and len(crypto_data) > 0:
            btc = crypto_data[crypto_data['symbol'] == 'BTC']
            if len(btc) > 0:
                btc_row = btc.iloc[0]
                st.metric(
                    label="₿ Bitcoin",
                    value=f"${btc_row['price_usd']:,.0f}",
                    delta=f"{btc_row['change_24h']:.2f}%"
                )
            else:
                st.metric(label="₿ Bitcoin", value="—")
        else:
            st.metric(label="₿ Bitcoin", value="—")
    
    # ETH
    with col3:
        if crypto_data is not None and len(crypto_data) > 0:
            eth = crypto_data[crypto_data['symbol'] == 'ETH']
            if len(eth) > 0:
                eth_row = eth.iloc[0]
                st.metric(
                    label="Ξ Ethereum",
                    value=f"${eth_row['price_usd']:,.0f}",
                    delta=f"{eth_row['change_24h']:.2f}%"
                )
            else:
                st.metric(label="Ξ Ethereum", value="—")
        else:
            st.metric(label="Ξ Ethereum", value="—")
    
    # 恐惧贪婪指数
    with col4:
        fng = data_manager.get_fear_greed_index()
        if fng:
            value = int(fng['value'])
            classification = fng['classification']
            
            # 根据值设置颜色
            if value <= 25:
                emoji = "😱"
            elif value <= 45:
                emoji = "😰"
            elif value <= 55:
                emoji = "😐"
            elif value <= 75:
                emoji = "😊"
            else:
                emoji = "🤑"
            
            st.metric(
                label=f"{emoji} 恐惧贪婪",
                value=f"{value}",
                delta=classification
            )
        else:
            st.metric(label="😐 恐惧贪婪", value="—")
    
    # 市场状态
    with col5:
        market_status = analyze_market_status(crypto_data)
        st.metric(
            label="📡 市场状态",
            value=market_status['status'],
            delta=market_status['trend']
        )


def show_simple_view(portfolio, data_manager):
    """简洁视图"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 资产价格")
        show_price_summary(portfolio)
    
    with col2:
        st.subheader("📈 24小时涨跌")
        show_change_chart(portfolio)


def show_detailed_view(portfolio, data_manager):
    """详细视图"""
    # 第一行：价格趋势
    st.subheader("📊 资产配置与表现")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        show_asset_allocation_pie(portfolio)
    
    with col2:
        show_performance_comparison(portfolio)
    
    st.markdown("---")
    
    # 第二行：详细表格
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 ETF详细信息")
        show_etf_details(portfolio)
    
    with col2:
        st.subheader("💎 加密货币详情")
        show_crypto_details(portfolio)
    
    st.markdown("---")
    
    # 第三行：市场分析
    st.subheader("🌐 市场情绪分析")
    show_market_sentiment(portfolio, data_manager)


def show_professional_view(portfolio, data_manager):
    """专业视图"""
    # 顶部：核心图表
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 资产总览",
        "📈 趋势分析",
        "🔥 热力图",
        "📉 相关性"
    ])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            show_asset_allocation_pie(portfolio)
        with col2:
            show_asset_metrics_table(portfolio)
    
    with tab2:
        show_price_trend_chart(portfolio, data_manager)
    
    with tab3:
        show_heatmap(portfolio)
    
    with tab4:
        show_correlation_analysis(portfolio, data_manager)
    
    st.markdown("---")
    
    # 底部：详细数据
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 技术指标")
        show_technical_indicators(portfolio)
    
    with col2:
        st.subheader("⚠️ 风险指标")
        show_risk_indicators(portfolio)
    
    with col3:
        st.subheader("🎯 交易信号")
        show_trading_signals(portfolio)


def show_price_summary(portfolio):
    """显示价格摘要"""
    data = []
    
    # ETF
    etf_data = portfolio.get('etf_513500')
    if etf_data:
        data.append({
            '资产': '513500 ETF',
            '价格': f"¥{etf_data['price']:.3f}",
            '涨跌幅': f"{etf_data['change_pct']:.2f}%"
        })
    
    # 加密货币
    crypto_data = portfolio.get('crypto')
    if crypto_data is not None and len(crypto_data) > 0:
        for _, row in crypto_data.iterrows():
            data.append({
                '资产': row['symbol'],
                '价格': f"${row['price_usd']:,.2f}",
                '涨跌幅': f"{row['change_24h']:.2f}%"
            })
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无数据")


def show_change_chart(portfolio):
    """显示涨跌柱状图"""
    data = []
    
    # ETF
    etf_data = portfolio.get('etf_513500')
    if etf_data:
        data.append({
            'asset': '513500',
            'change': etf_data['change_pct']
        })
    
    # 加密货币
    crypto_data = portfolio.get('crypto')
    if crypto_data is not None and len(crypto_data) > 0:
        for _, row in crypto_data.iterrows():
            data.append({
                'asset': row['symbol'],
                'change': row['change_24h']
            })
    
    if data:
        df = pd.DataFrame(data)
        
        fig = go.Figure()
        
        colors = ['red' if x < 0 else 'green' for x in df['change']]
        
        fig.add_trace(go.Bar(
            x=df['asset'],
            y=df['change'],
            marker_color=colors,
            text=df['change'].apply(lambda x: f"{x:.2f}%"),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="24小时涨跌幅",
            xaxis_title="资产",
            yaxis_title="涨跌幅 (%)",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")


def show_asset_allocation_pie(portfolio):
    """显示资产配置饼图"""
    st.markdown("#### 💼 资产配置")
    
    # 模拟持仓数据（实际应从配置或数据库读取）
    allocation = {
        '513500 ETF': 40,
        'Bitcoin': 30,
        'Ethereum': 20,
        '其他': 10
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(allocation.keys()),
        values=list(allocation.values()),
        hole=0.4,
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    )])
    
    fig.update_layout(
        title="当前持仓配置",
        height=350,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_performance_comparison(portfolio):
    """显示表现对比"""
    st.markdown("#### 📈 表现对比")
    
    data = []
    
    etf_data = portfolio.get('etf_513500')
    if etf_data:
        data.append({
            'asset': '513500',
            'change': etf_data['change_pct']
        })
    
    crypto_data = portfolio.get('crypto')
    if crypto_data is not None and len(crypto_data) > 0:
        for _, row in crypto_data.iterrows():
            data.append({
                'asset': row['symbol'],
                'change': row['change_24h']
            })
    
    if data:
        df = pd.DataFrame(data)
        df = df.sort_values('change', ascending=True)
        
        fig = go.Figure()
        
        colors = ['#FF6B6B' if x < 0 else '#51CF66' for x in df['change']]
        
        fig.add_trace(go.Bar(
            y=df['asset'],
            x=df['change'],
            orientation='h',
            marker_color=colors,
            text=df['change'].apply(lambda x: f"{x:.2f}%"),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="24小时收益率排行",
            xaxis_title="收益率 (%)",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")


def show_etf_details(portfolio):
    """显示ETF详细信息"""
    etf_data = portfolio.get('etf_513500')
    
    if etf_data:
        details = {
            '指标': ['名称', '最新价', '涨跌幅', '成交量', '成交额', '振幅', '换手率'],
            '数值': [
                etf_data.get('name', '—'),
                f"¥{etf_data['price']:.3f}",
                f"{etf_data['change_pct']:.2f}%",
                f"{etf_data['volume']:,.0f}",
                f"{etf_data['amount']/1e8:.2f}亿",
                f"{etf_data.get('amplitude', 0):.2f}%" if 'amplitude' in etf_data else "—",
                f"{etf_data.get('turnover', 0):.2f}%" if 'turnover' in etf_data else "—"
            ]
        }
        
        df = pd.DataFrame(details)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无数据")


def show_crypto_details(portfolio):
    """显示加密货币详细信息"""
    crypto_data = portfolio.get('crypto')
    
    if crypto_data is not None and len(crypto_data) > 0:
        display_data = []
        
        for _, row in crypto_data.iterrows():
            display_data.append({
                '币种': row['symbol'],
                '价格': f"${row['price_usd']:,.2f}",
                '24h涨跌': f"{row['change_24h']:.2f}%",
                '市值': f"${row['market_cap']/1e9:.2f}B" if row['market_cap'] else "—",
                '24h成交量': f"${row.get('volume_24h', 0)/1e9:.2f}B" if 'volume_24h' in row else "—"
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无数据")


def show_market_sentiment(portfolio, data_manager):
    """显示市场情绪分析"""
    col1, col2, col3 = st.columns(3)
    
    fng = data_manager.get_fear_greed_index()
    
    with col1:
        if fng:
            value = int(fng['value'])
            
            # 创建仪表盘
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "恐惧贪婪指数"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "red"},
                        {'range': [25, 45], 'color': "orange"},
                        {'range': [45, 55], 'color': "yellow"},
                        {'range': [55, 75], 'color': "lightgreen"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")
    
    with col2:
        st.markdown("**情绪指标**")
        if fng:
            st.write(f"分类: {fng['classification']}")
            st.write(f"数值: {fng['value']}")
            
            # 解读
            value = int(fng['value'])
            if value <= 25:
                st.warning("🔴 极度恐惧 - 可能是买入机会")
            elif value <= 45:
                st.warning("🟠 恐惧 - 市场谨慎")
            elif value <= 55:
                st.info("🟡 中性 - 市场平稳")
            elif value <= 75:
                st.success("🟢 贪婪 - 市场乐观")
            else:
                st.error("🔴 极度贪婪 - 注意风险")
        else:
            st.info("暂无数据")
    
    with col3:
        st.markdown("**市场总结**")
        crypto_data = portfolio.get('crypto')
        
        if crypto_data is not None and len(crypto_data) > 0:
            avg_change = crypto_data['change_24h'].mean()
            positive_count = (crypto_data['change_24h'] > 0).sum()
            total_count = len(crypto_data)
            
            st.write(f"平均涨幅: {avg_change:.2f}%")
            st.write(f"上涨数量: {positive_count}/{total_count}")
            
            if avg_change > 2:
                st.success("📈 市场强势上涨")
            elif avg_change > 0:
                st.info("📊 市场小幅上涨")
            elif avg_change > -2:
                st.info("📉 市场小幅下跌")
            else:
                st.error("📉 市场大幅下跌")
        else:
            st.info("暂无数据")


def show_asset_metrics_table(portfolio):
    """显示资产指标表格"""
    st.markdown("#### 📋 核心指标")
    
    metrics = []
    
    etf_data = portfolio.get('etf_513500')
    if etf_data:
        metrics.append({
            '资产': '513500',
            '价格': f"¥{etf_data['price']:.3f}",
            '涨跌': f"{etf_data['change_pct']:.2f}%",
            '成交额': f"{etf_data['amount']/1e8:.2f}亿"
        })
    
    crypto_data = portfolio.get('crypto')
    if crypto_data is not None and len(crypto_data) > 0:
        for _, row in crypto_data.iterrows():
            metrics.append({
                '资产': row['symbol'],
                '价格': f"${row['price_usd']:,.0f}",
                '涨跌': f"{row['change_24h']:.2f}%",
                '市值': f"${row['market_cap']/1e9:.1f}B" if row['market_cap'] else "—"
            })
    
    if metrics:
        df = pd.DataFrame(metrics)
        st.dataframe(df, use_container_width=True, hide_index=True)


def show_price_trend_chart(portfolio, data_manager):
    """显示价格趋势图"""
    st.markdown("#### 📈 历史价格走势")
    
    st.info("💡 价格趋势图需要历史数据，将在下一版本实现")


def show_heatmap(portfolio):
    """显示热力图"""
    st.markdown("#### 🔥 资产表现热力图")
    
    crypto_data = portfolio.get('crypto')
    
    if crypto_data is not None and len(crypto_data) > 0:
        # 创建热力图数据
        z_data = [crypto_data['change_24h'].tolist()]
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=crypto_data['symbol'].tolist(),
            y=['24h涨跌'],
            colorscale='RdYlGn',
            zmid=0,
            text=z_data,
            texttemplate='%{text:.2f}%',
            textfont={"size": 14}
        ))
        
        fig.update_layout(
            title="24小时涨跌热力图",
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")


def show_correlation_analysis(portfolio, data_manager):
    """显示相关性分析"""
    st.markdown("#### 📉 资产相关性分析")
    
    st.info("💡 相关性分析需要历史数据，将在下一版本实现")


def show_technical_indicators(portfolio):
    """显示技术指标"""
    st.info("💡 技术指标计算中...")


def show_risk_indicators(portfolio):
    """显示风险指标"""
    st.info("💡 风险指标计算中...")


def show_trading_signals(portfolio):
    """显示交易信号"""
    st.info("💡 交易信号分析中...")


def analyze_market_status(crypto_data):
    """分析市场状态"""
    if crypto_data is None or len(crypto_data) == 0:
        return {'status': '未知', 'trend': '—'}
    
    avg_change = crypto_data['change_24h'].mean()
    
    if avg_change > 3:
        return {'status': '热', 'trend': '📈 强势'}
    elif avg_change > 1:
        return {'status': '暖', 'trend': '📈 上涨'}
    elif avg_change > -1:
        return {'status': '平', 'trend': '➡️ 震荡'}
    elif avg_change > -3:
        return {'status': '冷', 'trend': '📉 下跌'}
    else:
        return {'status': '冻', 'trend': '📉 暴跌'}

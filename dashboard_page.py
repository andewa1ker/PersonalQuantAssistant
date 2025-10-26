"""
综合仪表板页面
整合关键指标、实时行情、告警信息、快速操作于一体的总览仪表板
性能优化: 使用缓存系统提升加载速度
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
from pathlib import Path
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入缓存辅助函数
from utils.cache_helper import (
    get_realtime_with_cache,
    batch_get_realtime,
    get_market_overview_cache,
    clear_cache
)


def show_dashboard_page(data_manager, config):
    """显示综合仪表板页面"""
    st.header("🎯 投资仪表板")
    
    # 自动刷新选项
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📊 实时投资总览")
    with col2:
        auto_refresh = st.checkbox("🔄 自动刷新", value=False, key="dashboard_auto_refresh")
    with col3:
        if auto_refresh:
            refresh_interval = st.selectbox("间隔", [30, 60, 300], format_func=lambda x: f"{x}秒", key="dashboard_interval")
            st.markdown(f"<small>每{refresh_interval}秒刷新</small>", unsafe_allow_html=True)
    
    # 刷新按钮
    if st.button("🔄 立即刷新", key="dashboard_refresh_now"):
        st.cache_data.clear()
        clear_cache()
        st.rerun()
    
    # 仪表板布局
    show_key_metrics_panel(data_manager, config)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        show_market_overview_panel(data_manager)
    with col2:
        show_alerts_panel(data_manager)
    
    col1, col2 = st.columns(2)
    with col1:
        show_top_gainers_losers(data_manager)
    with col2:
        show_portfolio_allocation_widget(data_manager)
    
    show_quick_actions_panel(config)
    
    show_recent_signals_panel(data_manager)


def show_key_metrics_panel(data_manager, config):
    """显示关键指标面板"""
    st.markdown("### 💰 关键指标")
    
    # 生成模拟数据
    metrics = generate_mock_dashboard_metrics()
    
    # 5列指标卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_color = "normal" if metrics['total_return_change'] >= 0 else "inverse"
        st.metric(
            "总资产",
            f"¥{metrics['total_value']:,.0f}",
            delta=f"{metrics['total_return']:.2%}",
            delta_color=delta_color
        )
    
    with col2:
        st.metric(
            "今日盈亏",
            f"¥{metrics['daily_pnl']:,.0f}",
            delta=f"{metrics['daily_pnl_pct']:.2%}",
            delta_color="normal" if metrics['daily_pnl'] >= 0 else "inverse"
        )
    
    with col3:
        st.metric(
            "持仓收益",
            f"¥{metrics['unrealized_pnl']:,.0f}",
            delta=f"{metrics['unrealized_pnl_pct']:.2%}",
            delta_color="normal" if metrics['unrealized_pnl'] >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            "夏普比率",
            f"{metrics['sharpe_ratio']:.2f}",
            delta=f"{metrics['sharpe_change']:.2f}",
            delta_color="normal" if metrics['sharpe_change'] >= 0 else "inverse"
        )
    
    with col5:
        risk_color = "🟢" if metrics['risk_level'] == "低" else ("🟡" if metrics['risk_level'] == "中" else "🔴")
        st.metric(
            "风险等级",
            f"{risk_color} {metrics['risk_level']}",
            delta=f"{metrics['risk_score']}/100"
        )
    
    st.markdown("---")


def show_market_overview_panel(data_manager):
    """显示市场概览面板"""
    st.markdown("### 📈 市场动态")
    
    # 生成市场数据
    market_data = generate_mock_market_data()
    
    # 创建市场指数走势图
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=("主要指数走势 (日内)", "市场情绪指标"),
        vertical_spacing=0.12
    )
    
    # 添加指数曲线
    colors = ['blue', 'red', 'green', 'orange']
    for idx, (name, data) in enumerate(market_data['indices'].items()):
        fig.add_trace(
            go.Scatter(
                x=data['time'],
                y=data['value'],
                name=name,
                line=dict(color=colors[idx], width=2),
                mode='lines'
            ),
            row=1, col=1
        )
    
    # 添加市场情绪条形图
    sentiment = market_data['sentiment']
    fig.add_trace(
        go.Bar(
            x=list(sentiment.keys()),
            y=list(sentiment.values()),
            marker_color=['green' if v > 50 else 'red' for v in sentiment.values()],
            text=[f"{v:.0f}" for v in sentiment.values()],
            textposition='auto',
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_xaxes(title_text="时间", row=1, col=1)
    fig.update_xaxes(title_text="指标", row=2, col=1)
    fig.update_yaxes(title_text="涨跌幅 (%)", row=1, col=1)
    fig.update_yaxes(title_text="情绪值", row=2, col=1)
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 市场统计
    with st.expander("📊 市场统计"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**涨跌家数**")
            st.write(f"上涨: {market_data['stats']['up']}")
            st.write(f"下跌: {market_data['stats']['down']}")
        with col2:
            st.write("**成交量**")
            st.write(f"沪市: {market_data['stats']['sh_volume']:.0f}亿")
            st.write(f"深市: {market_data['stats']['sz_volume']:.0f}亿")
        with col3:
            st.write("**资金流向**")
            net_flow = market_data['stats']['net_inflow']
            flow_color = "green" if net_flow > 0 else "red"
            st.markdown(f"净流入: :{flow_color}[{net_flow:+.0f}亿]")


def show_alerts_panel(data_manager):
    """显示告警面板"""
    st.markdown("### 🚨 实时告警")
    
    # 生成告警数据
    alerts = generate_mock_alerts()
    
    # 告警计数
    col1, col2, col3 = st.columns(3)
    with col1:
        critical_count = len([a for a in alerts if a['level'] == 'critical'])
        st.metric("🔴 严重", critical_count)
    with col2:
        warning_count = len([a for a in alerts if a['level'] == 'warning'])
        st.metric("🟡 警告", warning_count)
    with col3:
        info_count = len([a for a in alerts if a['level'] == 'info'])
        st.metric("🔵 信息", info_count)
    
    # 告警列表
    st.markdown("**最近告警:**")
    
    for alert in alerts[:5]:  # 只显示最近5条
        level_emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(alert['level'], '⚪')
        time_str = alert['time'].strftime('%H:%M:%S')
        
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"{level_emoji}")
            with col2:
                st.markdown(f"**{alert['title']}**")
                st.caption(f"{alert['message']} · {time_str}")
    
    if st.button("查看全部告警", key="view_all_alerts"):
        show_alerts_detail(alerts)


def show_alerts_detail(alerts: List[Dict]):
    """显示告警详情"""
    with st.expander("📋 全部告警", expanded=True):
        for alert in alerts:
            level_emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(alert['level'], '⚪')
            time_str = alert['time'].strftime('%Y-%m-%d %H:%M:%S')
            
            st.markdown(f"{level_emoji} **{alert['title']}** ({time_str})")
            st.write(alert['message'])
            if alert.get('action'):
                st.caption(f"建议操作: {alert['action']}")
            st.markdown("---")


def show_top_gainers_losers(data_manager):
    """显示涨跌幅榜"""
    st.markdown("### 📊 持仓涨跌榜")
    
    # 生成持仓涨跌数据
    holdings = generate_mock_holdings()
    
    # 排序
    holdings_sorted = sorted(holdings, key=lambda x: x['change_pct'], reverse=True)
    
    # 涨幅榜前5
    top_gainers = holdings_sorted[:5]
    # 跌幅榜前5
    top_losers = holdings_sorted[-5:][::-1]
    
    tab1, tab2 = st.tabs(["📈 涨幅榜", "📉 跌幅榜"])
    
    with tab1:
        for holding in top_gainers:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{holding['name']}**")
                st.caption(holding['code'])
            with col2:
                st.write(f"¥{holding['price']:.2f}")
            with col3:
                st.markdown(f":green[+{holding['change_pct']:.2%}]")
    
    with tab2:
        for holding in top_losers:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{holding['name']}**")
                st.caption(holding['code'])
            with col2:
                st.write(f"¥{holding['price']:.2f}")
            with col3:
                st.markdown(f":red[{holding['change_pct']:.2%}]")


def show_portfolio_allocation_widget(data_manager):
    """显示投资组合配置小部件"""
    st.markdown("### 🥧 资产配置")
    
    # 生成配置数据
    allocation = generate_mock_allocation()
    
    # 饼图
    fig = go.Figure(data=[go.Pie(
        labels=list(allocation.keys()),
        values=list(allocation.values()),
        hole=0.4,
        textposition='auto',
        textinfo='label+percent',
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])
    )])
    
    fig.update_layout(
        height=300,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 配置建议
    with st.expander("💡 配置建议"):
        st.write("**当前配置评估:**")
        st.write("✅ 股票配置适中 (45%)")
        st.write("⚠️ 加密货币占比偏高 (25%)")
        st.write("💡 建议增加债券配置以降低风险")


def show_quick_actions_panel(config):
    """显示快速操作面板"""
    st.markdown("### ⚡ 快速操作")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 刷新数据", key="quick_refresh_data", use_container_width=True):
            st.success("✅ 数据已刷新")
    
    with col2:
        if st.button("🔍 生成信号", key="quick_generate_signal", use_container_width=True):
            st.info("🔄 正在生成交易信号...")
    
    with col3:
        if st.button("📈 运行回测", key="quick_run_backtest", use_container_width=True):
            st.info("🔄 正在运行回测...")
    
    with col4:
        if st.button("📄 导出报告", key="quick_export_report", use_container_width=True):
            st.info("📥 正在生成报告...")


def show_recent_signals_panel(data_manager):
    """显示最近信号面板"""
    st.markdown("### 📡 最近交易信号")
    
    # 生成信号数据
    signals = generate_mock_recent_signals()
    
    # 信号表格
    df = pd.DataFrame(signals)
    
    # 格式化显示
    def format_signal_type(signal_type):
        colors = {'买入': '🟢', '卖出': '🔴', '持有': '🟡'}
        return f"{colors.get(signal_type, '⚪')} {signal_type}"
    
    df['信号'] = df['signal_type'].apply(format_signal_type)
    df['强度'] = df['strength'].apply(lambda x: '⭐' * int(x))
    
    # 显示表格
    st.dataframe(
        df[['time', 'asset_name', '信号', '强度', 'price', 'reason']].rename(columns={
            'time': '时间',
            'asset_name': '资产',
            'price': '价格',
            'reason': '原因'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # 信号统计
    with st.expander("📊 信号统计"):
        col1, col2, col3 = st.columns(3)
        
        buy_count = len([s for s in signals if s['signal_type'] == '买入'])
        sell_count = len([s for s in signals if s['signal_type'] == '卖出'])
        hold_count = len([s for s in signals if s['signal_type'] == '持有'])
        
        with col1:
            st.metric("买入信号", buy_count)
        with col2:
            st.metric("卖出信号", sell_count)
        with col3:
            st.metric("持有信号", hold_count)


# ============== 辅助函数 ==============

def generate_mock_dashboard_metrics() -> Dict:
    """生成模拟仪表板指标"""
    return {
        'total_value': 1256789.50,
        'total_return': 0.1523,
        'total_return_change': 0.0234,
        'daily_pnl': 8456.30,
        'daily_pnl_pct': 0.0068,
        'unrealized_pnl': 156789.50,
        'unrealized_pnl_pct': 0.1425,
        'sharpe_ratio': 1.85,
        'sharpe_change': 0.12,
        'risk_level': '中',
        'risk_score': 62
    }


def generate_mock_market_data() -> Dict:
    """生成模拟市场数据"""
    # 生成日内走势
    times = pd.date_range(start='09:30', end='15:00', freq='5min').strftime('%H:%M').tolist()
    
    indices = {
        '上证指数': {
            'time': times,
            'value': np.cumsum(np.random.randn(len(times)) * 0.2)
        },
        '深证成指': {
            'time': times,
            'value': np.cumsum(np.random.randn(len(times)) * 0.25)
        },
        '创业板指': {
            'time': times,
            'value': np.cumsum(np.random.randn(len(times)) * 0.3)
        },
        '沪深300': {
            'time': times,
            'value': np.cumsum(np.random.randn(len(times)) * 0.18)
        }
    }
    
    sentiment = {
        '恐慌指数': 45,
        '贪婪指数': 62,
        '多空比': 55,
        '北向资金': 58
    }
    
    stats = {
        'up': 2156,
        'down': 1847,
        'sh_volume': 3456,
        'sz_volume': 4523,
        'net_inflow': 123.5
    }
    
    return {
        'indices': indices,
        'sentiment': sentiment,
        'stats': stats
    }


def generate_mock_alerts() -> List[Dict]:
    """生成模拟告警"""
    now = datetime.now()
    
    alerts = [
        {
            'level': 'critical',
            'title': '止损触发',
            'message': 'BTC持仓跌破止损线(-8%)',
            'time': now - timedelta(minutes=5),
            'action': '建议立即减仓'
        },
        {
            'level': 'warning',
            'title': '波动率异常',
            'message': 'ETH波动率突破30%',
            'time': now - timedelta(minutes=15),
            'action': '关注市场动态'
        },
        {
            'level': 'warning',
            'title': '资金流出',
            'message': '主力资金持续流出3天',
            'time': now - timedelta(hours=1),
            'action': '谨慎操作'
        },
        {
            'level': 'info',
            'title': '买入信号',
            'message': '纳指ETF出现金叉信号',
            'time': now - timedelta(hours=2),
            'action': '可考虑建仓'
        },
        {
            'level': 'info',
            'title': '定投提醒',
            'message': '本月定投计划待执行',
            'time': now - timedelta(hours=3),
            'action': '查看定投详情'
        },
        {
            'level': 'critical',
            'title': '最大回撤警告',
            'message': '组合回撤达到-12%',
            'time': now - timedelta(hours=4),
            'action': '评估风险敞口'
        },
        {
            'level': 'info',
            'title': '收益达标',
            'message': '月度收益目标已达成',
            'time': now - timedelta(days=1),
            'action': '考虑获利了结'
        }
    ]
    
    return alerts


def generate_mock_holdings() -> List[Dict]:
    """生成模拟持仓"""
    holdings = [
        {'code': '513500', 'name': '标普500ETF', 'price': 2.156, 'change_pct': 0.0234},
        {'code': '513100', 'name': '纳指ETF', 'price': 3.678, 'change_pct': 0.0412},
        {'code': 'BTC', 'name': '比特币', 'price': 67234.50, 'change_pct': -0.0523},
        {'code': 'ETH', 'name': '以太坊', 'price': 3456.78, 'change_pct': -0.0387},
        {'code': '159941', 'name': '纳指100ETF', 'price': 1.234, 'change_pct': 0.0298},
        {'code': '510300', 'name': '沪深300ETF', 'price': 4.567, 'change_pct': -0.0156},
        {'code': '512000', 'name': '券商ETF', 'price': 1.089, 'change_pct': 0.0512},
        {'code': '515790', 'name': '光伏ETF', 'price': 0.876, 'change_pct': -0.0623}
    ]
    
    return holdings


def generate_mock_allocation() -> Dict:
    """生成模拟资产配置"""
    return {
        '股票ETF': 45,
        '加密货币': 25,
        '债券': 15,
        '商品': 10,
        '现金': 5
    }


def generate_mock_recent_signals() -> List[Dict]:
    """生成模拟最近信号"""
    now = datetime.now()
    
    signals = [
        {
            'time': (now - timedelta(minutes=5)).strftime('%H:%M'),
            'asset_name': '标普500ETF',
            'signal_type': '买入',
            'strength': 4,
            'price': 2.156,
            'reason': 'MACD金叉+RSI超卖'
        },
        {
            'time': (now - timedelta(minutes=15)).strftime('%H:%M'),
            'asset_name': '比特币',
            'signal_type': '卖出',
            'strength': 3,
            'price': 67234.50,
            'reason': '跌破MA20+成交量萎缩'
        },
        {
            'time': (now - timedelta(minutes=30)).strftime('%H:%M'),
            'asset_name': '纳指ETF',
            'signal_type': '持有',
            'strength': 2,
            'price': 3.678,
            'reason': '震荡整理,观望为主'
        },
        {
            'time': (now - timedelta(hours=1)).strftime('%H:%M'),
            'asset_name': '以太坊',
            'signal_type': '买入',
            'strength': 5,
            'price': 3456.78,
            'reason': '突破关键阻力+量能放大'
        },
        {
            'time': (now - timedelta(hours=2)).strftime('%H:%M'),
            'asset_name': '沪深300ETF',
            'signal_type': '持有',
            'strength': 3,
            'price': 4.567,
            'reason': '趋势向上,继续持有'
        }
    ]
    
    return signals


if __name__ == "__main__":
    st.set_page_config(page_title="投资仪表板", layout="wide")
    show_dashboard_page(None, {})

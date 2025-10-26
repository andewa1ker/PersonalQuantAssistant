"""
数据连接示例 - 如何将真实数据绑定到 Premium UI 组件
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# 导入 Premium UI 组件
from styles_premium import inject_premium_styles, DESIGN_TOKENS, create_divider
from components_premium import (
    render_balance_card,
    render_profit_chart,
    render_transaction_list,
    render_kpi_card,
    render_donut_chart,
    render_signal_table,
    render_upcoming_card,
    show_toast,
)
from icons import icon


# ==================== 模拟数据源 ====================
# 在实际应用中，这些函数应该从数据库或 API 获取数据

def get_portfolio_balance():
    """获取投资组合余额（模拟）"""
    # 实际应用中，从 DataManager 获取
    # portfolio = data_manager.get_portfolio_data()
    
    # 模拟数据
    return {
        "total": 127802.05,
        "change_pct": 0.15,
        "change_amount": 16500.32,
        "currency": "CNY"
    }


def get_profit_history(days=90):
    """获取收益历史（模拟）"""
    # 实际应用中:
    # history = data_manager.get_profit_history(days=days)
    
    # 模拟数据
    dates = []
    values = []
    base_value = 100000
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        # 模拟增长趋势 + 随机波动
        value = base_value * (1 + 0.003 * i + random.uniform(-0.02, 0.02))
        dates.append(date)
        values.append(round(value, 2))
    
    return {
        "dates": dates,
        "values": values
    }


def get_recent_transactions(limit=5):
    """获取最近交易（模拟）"""
    # 实际应用中:
    # transactions = data_manager.get_recent_transactions(limit=limit)
    
    # 模拟数据
    tx_types = [
        {"title": "工资收入", "tag": "月薪", "icon": "wallet", "amount_range": (8000, 15000)},
        {"title": "投资收益", "tag": "基金分红", "icon": "trending_up", "amount_range": (500, 5000)},
        {"title": "股票买入", "tag": "A股", "icon": "arrow_up_right", "amount_range": (-10000, -1000)},
        {"title": "餐饮消费", "tag": "日常", "icon": "credit_card", "amount_range": (-200, -50)},
        {"title": "房租支出", "tag": "固定", "icon": "credit_card", "amount_range": (-3000, -2000)},
    ]
    
    transactions = []
    for i in range(limit):
        tx_type = random.choice(tx_types)
        amount = random.uniform(*tx_type["amount_range"])
        
        # 时间
        hours_ago = i * 8
        if hours_ago < 24:
            time_str = f"{hours_ago}小时前"
        else:
            days_ago = hours_ago // 24
            time_str = f"{days_ago}天前"
        
        transactions.append({
            "title": tx_type["title"],
            "tag": tx_type["tag"],
            "amount": round(amount, 2),
            "time": time_str,
            "icon": tx_type["icon"]
        })
    
    return transactions


def get_kpi_metrics():
    """获取 KPI 指标（模拟）"""
    # 实际应用中:
    # metrics = data_manager.get_portfolio_metrics()
    
    return {
        "saving_rate": 0.68,       # 储蓄率
        "win_rate": 0.72,          # 胜率
        "sharpe": 1.85,            # 夏普比率
        "mdd": -0.12,              # 最大回撤
        "total_return": 0.28,      # 总收益率
        "annualized_return": 0.15, # 年化收益率
    }


def get_strategy_signals():
    """获取策略信号（模拟）"""
    # 实际应用中:
    # signals = signal_generator.get_current_signals()
    
    assets = ["BTC", "ETH", "513500 ETF", "沪深300", "恒生科技"]
    signal_types = ["买入", "卖出", "持有"]
    
    signals = []
    for asset in assets[:3]:  # 只取前3个
        signals.append({
            "资产": asset,
            "信号": random.choice(signal_types),
            "价格": f"¥{random.randint(100, 50000):,}",
            "时间": f"{random.randint(1, 12)}:{random.randint(0, 59):02d}"
        })
    
    return pd.DataFrame(signals)


def get_upcoming_events():
    """获取即将到期事项（模拟）"""
    # 实际应用中:
    # events = data_manager.get_upcoming_payments()
    
    return [
        {"name": "信用卡还款", "amount": 8500, "days_left": 3},
        {"name": "房贷月供", "amount": 6800, "days_left": 7},
        {"name": "保险续费", "amount": 2400, "days_left": 15},
    ]


# ==================== 数据转换函数 ====================

def format_balance_data(raw_data):
    """格式化余额数据为组件所需格式"""
    return {
        "total": raw_data["total"],
        "change_pct": raw_data["change_pct"],
        "change_amount": raw_data["change_amount"]
    }


def format_chart_data(raw_data):
    """格式化图表数据"""
    return {
        "dates": raw_data["dates"],
        "values": raw_data["values"]
    }


def format_transactions(raw_data):
    """格式化交易数据"""
    formatted = []
    for tx in raw_data:
        formatted.append({
            "title": tx["title"],
            "tag": tx["tag"],
            "amount": tx["amount"],
            "time": tx["time"],
            "icon": tx["icon"]
        })
    return formatted


# ==================== 完整示例页面 ====================

def show_data_binding_example():
    """展示数据绑定的完整示例"""
    
    # 应用样式
    inject_premium_styles()
    
    # 页面标题
    st.markdown(f"""
    <div style="font-size: 2rem; font-weight: 700;">
        {icon('home', 28, DESIGN_TOKENS['primary_solid'])} 数据绑定示例
    </div>
    <p style="color: {DESIGN_TOKENS['text_secondary']}; margin-top: 0.5rem;">
        演示如何将真实数据绑定到 Premium UI 组件
    </p>
    """, unsafe_allow_html=True)
    
    create_divider()
    
    # 获取数据
    with st.spinner("正在加载数据..."):
        balance = get_portfolio_balance()
        chart_data = get_profit_history(days=90)
        transactions = get_recent_transactions(limit=5)
        kpi_metrics = get_kpi_metrics()
        signals = get_strategy_signals()
        upcoming = get_upcoming_events()
    
    # 第一行：账户总览 + 收益曲线
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 💰 账户总览")
        render_balance_card(balance)
        
        st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
        
        st.markdown("### 📅 即将到期")
        render_upcoming_card(upcoming)
    
    with col2:
        st.markdown("### 📈 收益走势")
        render_profit_chart(chart_data, "最近90天收益")
    
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    # 第二行：KPI 统计
    st.markdown(f"""
    <h3 style="margin: 0 0 1.5rem 0; font-size: 1.2rem;">
        {icon('bar_chart', 20, DESIGN_TOKENS['primary_solid'])}
        <span style="margin-left: 0.5rem;">关键指标</span>
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card(
            "储蓄率",
            f"{kpi_metrics['saving_rate']*100:.0f}%",
            "+5%",
            "wallet"
        )
    
    with col2:
        render_kpi_card(
            "胜率",
            f"{kpi_metrics['win_rate']*100:.0f}%",
            "+8%",
            "target"
        )
    
    with col3:
        render_kpi_card(
            "夏普比率",
            f"{kpi_metrics['sharpe']:.2f}",
            "+0.15",
            "trending_up"
        )
    
    with col4:
        render_kpi_card(
            "最大回撤",
            f"{abs(kpi_metrics['mdd'])*100:.1f}%",
            "-2%",
            "shield_check"
        )
    
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    # 第三行：交易列表 + 策略信号
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💳 最近交易")
        render_transaction_list(transactions)
    
    with col2:
        st.markdown("### 🎯 策略信号")
        render_signal_table(signals)
    
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    # 第四行：环形统计图
    st.markdown(f"""
    <h3 style="margin: 0 0 1.5rem 0; font-size: 1.2rem;">
        {icon('pie_chart', 20, DESIGN_TOKENS['primary_solid'])}
        <span style="margin-left: 0.5rem;">分析指标</span>
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_donut_chart(kpi_metrics['saving_rate'], "储蓄率", DESIGN_TOKENS['primary_solid'])
    
    with col2:
        render_donut_chart(kpi_metrics['win_rate'], "胜率", DESIGN_TOKENS['success'])
    
    with col3:
        render_donut_chart(abs(kpi_metrics['mdd']), "风险利用", DESIGN_TOKENS['warning'])
    
    # 代码示例
    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)
    create_divider()
    
    st.markdown("## 📝 代码示例")
    
    with st.expander("查看余额卡数据绑定代码"):
        st.code('''
# 1. 获取数据
balance = get_portfolio_balance()
# 返回: {"total": 127802.05, "change_pct": 0.15, "change_amount": 16500.32}

# 2. 格式化（如果需要）
formatted = format_balance_data(balance)

# 3. 渲染组件
render_balance_card(formatted)
        ''', language='python')
    
    with st.expander("查看收益曲线数据绑定代码"):
        st.code('''
# 1. 获取历史数据
chart_data = get_profit_history(days=90)
# 返回: {"dates": [...], "values": [...]}

# 2. 渲染组件
render_profit_chart(chart_data, "最近90天收益")
        ''', language='python')
    
    with st.expander("查看交易列表数据绑定代码"):
        st.code('''
# 1. 获取交易记录
transactions = get_recent_transactions(limit=5)
# 返回: [{"title": "...", "tag": "...", "amount": ..., "time": "...", "icon": "..."}]

# 2. 格式化（如果需要）
formatted = format_transactions(transactions)

# 3. 渲染组件
render_transaction_list(formatted)
        ''', language='python')
    
    # 刷新按钮
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    if st.button("🔄 刷新数据", use_container_width=True):
        st.rerun()


# ==================== 实际应用集成示例 ====================

def integrate_with_data_manager(data_manager, signal_gen):
    """与 DataManager 和 SignalGenerator 集成的示例"""
    
    inject_premium_styles()
    
    st.markdown("## 🔌 与现有系统集成")
    
    st.markdown("""
    ### 集成步骤
    
    1. **导入现有模块**
    ```python
    from data_fetcher.data_manager import DataManager
    from analysis.signal_generator import SignalGenerator
    ```
    
    2. **初始化管理器**
    ```python
    data_manager = DataManager()
    signal_gen = SignalGenerator()
    ```
    
    3. **获取数据**
    ```python
    # 获取投资组合数据
    portfolio = data_manager.get_portfolio_data()
    
    # 获取历史数据
    history = data_manager.get_asset_data('crypto', 'bitcoin', 'history', days=90)
    
    # 生成信号
    signals = signal_gen.analyze_with_signals(history)
    ```
    
    4. **转换为组件格式**
    ```python
    # 余额数据
    balance = {
        "total": portfolio['total_value'],
        "change_pct": portfolio['daily_change_pct'],
        "change_amount": portfolio['daily_change_amount']
    }
    
    # 图表数据
    chart_data = {
        "dates": history.index.strftime('%Y-%m-%d').tolist(),
        "values": history['close'].tolist()
    }
    ```
    
    5. **渲染组件**
    ```python
    render_balance_card(balance)
    render_profit_chart(chart_data)
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("### 📦 完整集成示例")
    
    st.code('''
import streamlit as st
from data_fetcher.data_manager import DataManager
from analysis.signal_generator import SignalGenerator
from styles_premium import inject_premium_styles
from components_premium import (
    render_balance_card,
    render_profit_chart,
    render_transaction_list,
)

def show_dashboard():
    """完整的Dashboard"""
    
    # 应用样式
    inject_premium_styles()
    
    # 初始化
    data_manager = DataManager()
    signal_gen = SignalGenerator()
    
    # 获取数据
    portfolio = data_manager.get_portfolio_data()
    history = data_manager.get_profit_history()
    transactions = data_manager.get_recent_transactions()
    
    # 转换格式
    balance = {
        "total": portfolio['total_value'],
        "change_pct": portfolio['daily_change_pct'],
        "change_amount": portfolio['daily_change_amount']
    }
    
    chart_data = {
        "dates": history['dates'].tolist(),
        "values": history['values'].tolist()
    }
    
    formatted_txs = []
    for tx in transactions:
        formatted_txs.append({
            "title": tx['description'],
            "tag": tx['category'],
            "amount": tx['amount'],
            "time": tx['datetime'].strftime('%Y-%m-%d %H:%M'),
            "icon": "wallet" if tx['amount'] > 0 else "credit_card"
        })
    
    # 渲染组件
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_balance_card(balance)
    
    with col2:
        render_profit_chart(chart_data)
    
    render_transaction_list(formatted_txs)

if __name__ == "__main__":
    show_dashboard()
    ''', language='python')


# ==================== 主函数 ====================

if __name__ == "__main__":
    st.set_page_config(
        page_title="数据绑定示例",
        layout="wide",
        page_icon="🔗"
    )
    
    page = st.sidebar.radio(
        "选择示例",
        ["数据绑定演示", "系统集成说明"]
    )
    
    if page == "数据绑定演示":
        show_data_binding_example()
    else:
        integrate_with_data_manager(None, None)

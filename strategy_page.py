"""
投资策略页面模块
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_strategy_page(config):
    """显示投资策略页面"""
    st.header("💰 投资策略中心")
    
    st.markdown("""
    ### 智能投资策略
    基于量化分析的多种投资策略，帮助您做出更明智的投资决策。
    """)
    
    # 策略选择
    strategy_type = st.selectbox(
        "选择策略类型",
        ["ETF估值策略", "加密货币动量策略", "定投策略", "投资组合再平衡"],
        key="strategy_type"
    )
    
    if strategy_type == "ETF估值策略":
        show_etf_valuation_strategy(config)
    elif strategy_type == "加密货币动量策略":
        show_crypto_momentum_strategy(config)
    elif strategy_type == "定投策略":
        show_dca_strategy(config)
    elif strategy_type == "投资组合再平衡":
        show_portfolio_rebalance(config)


def show_etf_valuation_strategy(config):
    """显示ETF估值策略"""
    st.subheader("📊 ETF估值策略")
    
    st.markdown("""
    通过PE、PB等估值指标的历史百分位判断ETF是否被低估或高估，
    在低估时买入，高估时卖出。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        etf_code = st.text_input("ETF代码", value="513500", key="etf_val_code")
        buy_percentile = st.slider("买入百分位", 0, 50, 30, key="etf_buy_pct")
        
    with col2:
        capital = st.number_input("投资金额 (元)", value=100000, step=10000, key="etf_capital")
        sell_percentile = st.slider("卖出百分位", 50, 100, 70, key="etf_sell_pct")
    
    if st.button("🔍 分析ETF估值", key="analyze_etf_val"):
        with st.spinner("正在分析..."):
            try:
                from strategy.etf_valuation import ETFValuationStrategy
                # 使用已有的DataManager而不是AKShareFetcher
                from data_fetcher.data_manager import DataManager
                
                # 配置策略
                strategy_config = {
                    'buy_percentile': buy_percentile,
                    'sell_percentile': sell_percentile
                }
                strategy = ETFValuationStrategy(strategy_config)
                
                # 获取数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_etf_hist(etf_code, period="3y")
                
                if data is None or len(data) < 100:
                    st.error("❌ 无法获取足够的ETF数据")
                    return
                
                # 执行策略分析
                result = strategy.analyze(data, asset_symbol=etf_code, capital=capital)
                
                # 显示结果
                st.success("✅ 分析完成")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    action_emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
                    st.metric("操作建议", 
                             f"{action_emoji.get(result.action, '🟡')} {result.action.upper()}")
                
                with col2:
                    st.metric("当前价格", f"¥{result.current_price:.3f}")
                
                with col3:
                    st.metric("信心度", f"{result.confidence:.0%}")
                
                # 详细信息
                st.markdown("---")
                st.markdown("### 📋 分析详情")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**策略建议**")
                    st.write(result.reason)
                    st.write(f"风险等级: {result.risk_level}")
                    if result.action == "buy" and result.quantity:
                        st.write(f"建议买入数量: {result.quantity:.0f} 份")
                    elif result.action == "sell" and result.quantity:
                        st.write(f"建议卖出数量: {result.quantity:.0f} 份")
                
                with col2:
                    st.markdown("**关键指标**")
                    if result.indicators:
                        for key in ['pe_percentile', 'pb_percentile', 'price_percentile', 
                                   'current_pe', 'current_pb']:
                            if key in result.indicators:
                                value = result.indicators[key]
                                if isinstance(value, (int, float)):
                                    st.write(f"{key}: {value:.2f}")
                                else:
                                    st.write(f"{key}: {value}")
                
            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                logger.error(f"ETF估值策略错误: {e}", exc_info=True)


def show_crypto_momentum_strategy(config):
    """显示加密货币动量策略"""
    st.subheader("🚀 加密货币动量策略")
    
    st.markdown("""
    基于价格动量和趋势指标，捕捉加密货币的上涨趋势。
    适合中短期交易。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        crypto_symbol = st.text_input("加密货币", value="BTC", key="crypto_symbol")
        short_window = st.slider("短期均线", 5, 20, 10, key="crypto_short")
        
    with col2:
        capital = st.number_input("投资金额 (USDT)", value=50000, step=5000, key="crypto_capital")
        long_window = st.slider("长期均线", 20, 60, 30, key="crypto_long")
    
    if st.button("🔍 分析动量", key="analyze_crypto_momentum"):
        with st.spinner("正在分析..."):
            try:
                from strategy.crypto_momentum import CryptoMomentumStrategy
                from data_fetcher.data_manager import DataManager
                
                # 配置策略
                strategy_config = {
                    'short_window': short_window,
                    'long_window': long_window
                }
                strategy = CryptoMomentumStrategy(strategy_config)
                
                # 获取数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_crypto_hist(crypto_symbol, period="90d")
                
                if data is None or len(data) < long_window:
                    st.error("❌ 无法获取足够的加密货币数据")
                    return
                
                # 执行策略分析
                result = strategy.analyze(data, asset_symbol=crypto_symbol, capital=capital)
                
                # 显示结果
                st.success("✅ 分析完成")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    action_emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
                    st.metric("操作建议", 
                             f"{action_emoji.get(result.action, '🟡')} {result.action.upper()}")
                
                with col2:
                    st.metric("当前价格", f"${result.current_price:,.2f}")
                
                with col3:
                    st.metric("信心度", f"{result.confidence:.0%}")
                
                # 详细信息
                st.markdown("---")
                st.markdown("### 📋 分析详情")
                st.write(result.reason)
                st.write(f"风险等级: {result.risk_level}")
                
            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                logger.error(f"加密货币动量策略错误: {e}", exc_info=True)


def show_dca_strategy(config):
    """显示定投策略"""
    st.subheader("📅 定投策略计算器")
    
    st.markdown("""
    定期定额投资策略，通过分散投资时间降低风险。
    支持固定定投、智能定投和网格定投。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="dca_code")
        dca_type = st.selectbox("定投类型", 
                               ["fixed", "smart", "grid"], 
                               format_func=lambda x: {"fixed": "固定定投", 
                                                     "smart": "智能定投", 
                                                     "grid": "网格定投"}[x],
                               key="dca_type")
        base_amount = st.number_input("定投金额 (元)", value=1000, step=100, key="dca_amount")
        
    with col2:
        frequency = st.slider("定投频率 (天)", 1, 30, 7, key="dca_freq")
        
        if dca_type == "smart":
            valuation_factor = st.slider("估值调整因子", 0.0, 1.0, 0.5, 0.1, key="dca_val_factor")
        elif dca_type == "grid":
            grid_levels = st.slider("网格层数", 3, 10, 5, key="dca_grid_levels")
            grid_spacing = st.slider("网格间距 (%)", 1, 10, 5, key="dca_grid_spacing") / 100
    
    if st.button("💰 计算定投收益", key="calculate_dca"):
        with st.spinner("正在计算..."):
            try:
                from strategy.dca_strategy import DCAStrategy
                from data_fetcher.data_manager import DataManager
                
                # 配置策略
                strategy_config = {
                    'base_amount': base_amount,
                    'frequency': frequency,
                    'dca_type': dca_type
                }
                
                if dca_type == "smart":
                    strategy_config['valuation_factor'] = valuation_factor
                elif dca_type == "grid":
                    strategy_config['grid_levels'] = grid_levels
                    strategy_config['grid_spacing'] = grid_spacing
                
                strategy = DCAStrategy(strategy_config)
                
                # 获取历史数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_etf_hist(asset_code, period="1y")
                
                if data is None or len(data) < 30:
                    st.error("❌ 无法获取足够的历史数据")
                    return
                
                # 模拟定投
                from datetime import datetime, timedelta
                last_dca_date = None
                total_invested = 0
                total_shares = 0
                dca_records = []
                
                for idx, row in data.iterrows():
                    # 执行策略分析
                    current_data = data.loc[:idx]
                    result = strategy.analyze(
                        current_data, 
                        asset_symbol=asset_code,
                        last_dca_date=last_dca_date
                    )
                    
                    if result.action == "buy":
                        amount = result.indicators.get('dca_amount', base_amount)
                        shares = amount / result.current_price
                        total_invested += amount
                        total_shares += shares
                        last_dca_date = row['date'] if 'date' in row else idx
                        
                        dca_records.append({
                            'date': row['date'] if 'date' in row else idx,
                            'price': result.current_price,
                            'amount': amount,
                            'shares': shares
                        })
                
                # 计算收益
                current_price = float(data['close'].iloc[-1])
                total_value = total_shares * current_price
                total_profit = total_value - total_invested
                return_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0
                
                # 显示结果
                st.success("✅ 计算完成")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("总投入", f"¥{total_invested:,.2f}")
                
                with col2:
                    st.metric("当前市值", f"¥{total_value:,.2f}")
                
                with col3:
                    profit_color = "normal" if total_profit >= 0 else "inverse"
                    st.metric("总收益", f"¥{total_profit:,.2f}", 
                             delta_color=profit_color)
                
                with col4:
                    st.metric("收益率", f"{return_rate:.2f}%")
                
                # 定投记录
                if dca_records:
                    st.markdown("---")
                    st.markdown("### 📊 定投记录")
                    st.write(f"定投次数: {len(dca_records)}")
                    
                    df_records = pd.DataFrame(dca_records)
                    st.dataframe(df_records.tail(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 计算失败: {str(e)}")
                logger.error(f"定投策略错误: {e}", exc_info=True)


def show_portfolio_rebalance(config):
    """显示投资组合再平衡"""
    st.subheader("⚖️ 投资组合再平衡")
    
    st.markdown("""
    根据目标配置比例，计算需要调整的持仓，保持投资组合平衡。
    """)
    
    st.markdown("### 当前持仓")
    
    # 使用session_state保存持仓数据
    if 'portfolio_holdings' not in st.session_state:
        st.session_state.portfolio_holdings = [
            {'asset': '513500', 'value': 50000, 'quantity': 40000, 'target': 40},
            {'asset': 'BTC', 'value': 30000, 'quantity': 0.5, 'target': 35},
            {'asset': 'ETH', 'value': 20000, 'quantity': 8, 'target': 25},
        ]
    
    df_holdings = pd.DataFrame(st.session_state.portfolio_holdings)
    
    edited_df = st.data_editor(
        df_holdings,
        column_config={
            "asset": st.column_config.TextColumn("资产代码", required=True),
            "value": st.column_config.NumberColumn("当前市值 (元)", format="¥%.2f"),
            "quantity": st.column_config.NumberColumn("持有数量"),
            "target": st.column_config.NumberColumn("目标配置 (%)", min_value=0, max_value=100),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="portfolio_editor"
    )
    
    if st.button("⚖️ 计算再平衡方案", key="calc_rebalance"):
        with st.spinner("正在计算..."):
            try:
                from strategy.portfolio_manager import PortfolioManager
                import numpy as np
                
                # 验证目标配置总和
                total_target = edited_df['target'].sum()
                if abs(total_target - 100) > 0.1:
                    st.error(f"❌ 目标配置总和必须为100%，当前为{total_target:.1f}%")
                    return
                
                # 准备数据
                current_holdings = {}
                target_allocation = {}
                
                for _, row in edited_df.iterrows():
                    asset = row['asset']
                    current_holdings[asset] = {
                        'value': float(row['value']),
                        'quantity': float(row['quantity'])
                    }
                    target_allocation[asset] = float(row['target']) / 100
                
                # 创建投资组合管理器
                portfolio_manager = PortfolioManager()
                
                # 模拟数据用于analyze方法
                dummy_data = pd.DataFrame({
                    'close': np.ones(10)
                })
                
                # 执行分析
                result = portfolio_manager.analyze(
                    dummy_data,
                    asset_symbol="Portfolio",
                    current_holdings=current_holdings,
                    target_allocation=target_allocation
                )
                
                # 显示结果
                st.success("✅ 计算完成")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_value = sum(h['value'] for h in current_holdings.values())
                    st.metric("组合总值", f"¥{total_value:,.2f}")
                
                with col2:
                    st.metric("操作建议", f"🔄 {result.action.upper()}")
                
                with col3:
                    st.metric("信心度", f"{result.confidence:.0%}")
                
                # 再平衡详情
                st.markdown("---")
                st.markdown("### 📋 再平衡方案")
                st.write(result.reason)
                
                if result.indicators and 'rebalance_plan' in result.indicators:
                    rebalance_plan = result.indicators['rebalance_plan']
                    
                    rebalance_data = []
                    for asset, plan in rebalance_plan.items():
                        rebalance_data.append({
                            '资产': asset,
                            '操作': plan['action'],
                            '金额': f"¥{abs(plan['amount']):,.2f}",
                            '数量': f"{abs(plan.get('quantity', 0)):,.4f}"
                        })
                    
                    df_rebalance = pd.DataFrame(rebalance_data)
                    st.dataframe(df_rebalance, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 计算失败: {str(e)}")
                logger.error(f"投资组合再平衡错误: {e}", exc_info=True)

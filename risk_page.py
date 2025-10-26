"""
风险管理页面模块
展示风险指标、仓位建议、止损止盈、风险告警
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_risk_page(config):
    """显示风险管理页面"""
    st.header("⚠️ 风险管理中心")
    
    st.markdown("""
    ### 全方位风险管理
    实时监控风险指标，智能仓位建议，动态止损止盈
    """)
    
    # 选择功能模块
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 风险指标分析",
        "💼 仓位管理",
        "🛡️ 止损止盈",
        "🚨 风险监控告警"
    ])
    
    with tab1:
        show_risk_metrics(config)
    
    with tab2:
        show_position_management(config)
    
    with tab3:
        show_stop_loss_management(config)
    
    with tab4:
        show_risk_monitoring(config)


def show_risk_metrics(config):
    """显示风险指标分析"""
    st.subheader("📊 风险指标分析")
    
    st.markdown("""
    计算资产的全面风险指标，包括VaR、CVaR、最大回撤、夏普比率等。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="risk_asset_code")
        period = st.selectbox(
            "分析周期",
            ["1y", "6m", "3m", "1m"],
            format_func=lambda x: {"1y": "1年", "6m": "6个月", "3m": "3个月", "1m": "1个月"}[x],
            key="risk_period"
        )
    
    with col2:
        confidence_level = st.slider("VaR置信水平", 0.90, 0.99, 0.95, 0.01, key="var_confidence")
        risk_free_rate = st.slider("无风险利率", 0.0, 0.10, 0.03, 0.01, format="%.2f", key="risk_free")
    
    if st.button("🔍 分析风险指标", key="analyze_risk"):
        with st.spinner("正在分析..."):
            try:
                from risk_management import RiskMeasurement
                from data.fetcher_akshare import AKShareFetcher
                
                # 获取数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_etf_hist(asset_code, period=period)
                
                if data is None or len(data) < 30:
                    st.error("❌ 无法获取足够的历史数据")
                    return
                
                # 配置风险度量器
                risk_config = {
                    'confidence_level': confidence_level,
                    'risk_free_rate': risk_free_rate
                }
                risk_measurement = RiskMeasurement(risk_config)
                
                # 计算风险指标
                metrics = risk_measurement.calculate_metrics(data, asset_symbol=asset_code)
                
                # 显示结果
                st.success("✅ 分析完成")
                
                # 风险等级展示
                risk_color_map = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🟠',
                    'extreme': '🔴'
                }
                risk_emoji = risk_color_map.get(metrics.risk_level, '⚪')
                
                st.markdown(f"### {risk_emoji} 风险等级: {metrics.risk_level.upper()}")
                st.progress(metrics.risk_score / 100)
                st.caption(f"风险评分: {metrics.risk_score:.0f}/100")
                
                st.markdown("---")
                
                # 关键指标
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "年化收益",
                        f"{metrics.annualized_return:.2%}",
                        delta=f"{metrics.total_return:.2%}"
                    )
                
                with col2:
                    st.metric(
                        "波动率",
                        f"{metrics.volatility:.2%}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "最大回撤",
                        f"{metrics.max_drawdown:.2%}",
                        delta=None,
                        delta_color="inverse"
                    )
                
                with col4:
                    st.metric(
                        "夏普比率",
                        f"{metrics.sharpe_ratio:.2f}",
                        delta=None
                    )
                
                # 详细指标
                st.markdown("---")
                st.markdown("### 📋 详细风险指标")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**风险指标**")
                    st.write(f"VaR (95%): {metrics.var_95:.2%}")
                    st.write(f"CVaR (95%): {metrics.cvar_95:.2%}")
                    st.write(f"下行波动率: {metrics.downside_volatility:.2%}")
                
                with col2:
                    st.markdown("**收益指标**")
                    st.write(f"索提诺比率: {metrics.sortino_ratio:.2f}")
                    st.write(f"卡玛比率: {metrics.calmar_ratio:.2f}")
                    st.write(f"胜率: {metrics.win_rate:.1%}")
                    st.write(f"盈亏比: {metrics.profit_loss_ratio:.2f}")
                
                # 数据统计
                if metrics.details:
                    st.markdown("---")
                    st.markdown("### 📈 数据统计")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"数据点数: {metrics.details.get('data_points', 0)}")
                        st.write(f"正收益天数: {metrics.details.get('positive_returns', 0)}")
                    
                    with col2:
                        st.write(f"负收益天数: {metrics.details.get('negative_returns', 0)}")
                        st.write(f"最佳单日: {metrics.details.get('best_day', 0):.2%}")
                    
                    with col3:
                        st.write(f"最差单日: {metrics.details.get('worst_day', 0):.2%}")
                        st.write(f"平均收益: {metrics.details.get('avg_return', 0):.2%}")
                
            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                logger.error(f"风险指标分析错误: {e}", exc_info=True)


def show_position_management(config):
    """显示仓位管理"""
    st.subheader("💼 智能仓位管理")
    
    st.markdown("""
    基于风险收益特征，计算最优仓位配置。
    """)
    
    # 选择计算方法
    method = st.selectbox(
        "计算方法",
        ["综合", "凯利公式", "波动率调整", "固定风险"],
        key="position_method"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="pos_asset_code")
        
        if method in ["凯利公式", "综合"]:
            win_rate = st.slider("历史胜率", 0.0, 1.0, 0.55, 0.01, key="pos_win_rate")
            pl_ratio = st.slider("盈亏比", 0.5, 5.0, 2.0, 0.1, key="pos_pl_ratio")
    
    with col2:
        capital = st.number_input("投资金额 (元)", value=100000, step=10000, key="pos_capital")
        
        if method == "固定风险":
            stop_loss_pct = st.slider("止损幅度", 0.01, 0.20, 0.05, 0.01, format="%.2f", key="pos_stop")
    
    if st.button("💰 计算建议仓位", key="calc_position"):
        with st.spinner("正在计算..."):
            try:
                from risk_management import PositionManager
                from data.fetcher_akshare import AKShareFetcher
                
                position_manager = PositionManager()
                
                if method == "凯利公式":
                    position = position_manager.calculate_position_kelly(
                        win_rate=win_rate,
                        profit_loss_ratio=pl_ratio,
                        asset_symbol=asset_code
                    )
                
                elif method == "波动率调整":
                    fetcher = AKShareFetcher()
                    data = fetcher.fetch_etf_hist(asset_code, period="3m")
                    
                    if data is None or len(data) < 30:
                        st.error("❌ 无法获取足够的历史数据")
                        return
                    
                    position = position_manager.calculate_position_volatility(
                        data,
                        asset_symbol=asset_code
                    )
                
                elif method == "固定风险":
                    position = position_manager.calculate_position_fixed_risk(
                        stop_loss_pct=stop_loss_pct,
                        asset_symbol=asset_code
                    )
                
                else:  # 综合
                    fetcher = AKShareFetcher()
                    data = fetcher.fetch_etf_hist(asset_code, period="3m")
                    
                    if data is None or len(data) < 30:
                        st.error("❌ 无法获取足够的历史数据")
                        return
                    
                    position = position_manager.calculate_position_综合(
                        data,
                        win_rate=win_rate if method == "综合" else None,
                        profit_loss_ratio=pl_ratio if method == "综合" else None,
                        asset_symbol=asset_code
                    )
                
                # 显示结果
                st.success("✅ 计算完成")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("建议仓位", f"{position.recommended_position:.1%}")
                
                with col2:
                    recommended_amount = capital * position.recommended_position
                    st.metric("建议金额", f"¥{recommended_amount:,.0f}")
                
                with col3:
                    risk_level_emoji = {
                        'very_low': '🟢',
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🔴'
                    }
                    emoji = risk_level_emoji.get(position.risk_level, '⚪')
                    st.metric("风险等级", f"{emoji} {position.risk_level}")
                
                st.markdown("---")
                
                # 详细信息
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**计算依据**")
                    st.write(f"方法: {position.method}")
                    st.write(f"信心度: {position.confidence:.0%}")
                    st.write(position.reason)
                
                with col2:
                    st.markdown("**仓位范围**")
                    st.write(f"最小仓位: {position.min_position:.1%}")
                    st.write(f"最大仓位: {position.max_position:.1%}")
                    
                    if position.win_probability:
                        st.write(f"胜率: {position.win_probability:.1%}")
                    if position.win_loss_ratio:
                        st.write(f"盈亏比: {position.win_loss_ratio:.2f}")
                
            except Exception as e:
                st.error(f"❌ 计算失败: {str(e)}")
                logger.error(f"仓位计算错误: {e}", exc_info=True)


def show_stop_loss_management(config):
    """显示止损止盈管理"""
    st.subheader("🛡️ 止损止盈管理")
    
    st.markdown("""
    设置科学的止损止盈点位，控制风险，锁定利润。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="sl_asset_code")
        direction = st.selectbox("交易方向", ["做多 (Long)", "做空 (Short)"], key="sl_direction")
        direction_value = 'long' if '做多' in direction else 'short'
    
    with col2:
        method = st.selectbox(
            "止损方法",
            ["固定百分比", "ATR动态", "支撑阻力"],
            key="sl_method"
        )
        
        if method == "固定百分比":
            stop_pct = st.slider("止损幅度", 0.01, 0.20, 0.05, 0.01, format="%.2f", key="sl_stop_pct")
            profit_pct = st.slider("止盈幅度", 0.05, 0.50, 0.15, 0.05, format="%.2f", key="sl_profit_pct")
    
    if st.button("🎯 计算止损止盈", key="calc_stoploss"):
        with st.spinner("正在计算..."):
            try:
                from risk_management import StopLossManager
                from data.fetcher_akshare import AKShareFetcher
                
                stop_loss_manager = StopLossManager()
                
                # 获取数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_etf_hist(asset_code, period="3m")
                
                if data is None or len(data) < 20:
                    st.error("❌ 无法获取足够的历史数据")
                    return
                
                current_price = float(data['close'].iloc[-1])
                
                # 根据方法计算
                if method == "固定百分比":
                    target = stop_loss_manager.calculate_fixed_stop_loss(
                        current_price=current_price,
                        direction=direction_value,
                        asset_symbol=asset_code,
                        stop_loss_pct=stop_pct,
                        take_profit_pct=profit_pct
                    )
                
                elif method == "ATR动态":
                    target = stop_loss_manager.calculate_atr_stop_loss(
                        data,
                        direction=direction_value,
                        asset_symbol=asset_code
                    )
                
                else:  # 支撑阻力
                    target = stop_loss_manager.calculate_支撑阻力_stop_loss(
                        data,
                        direction=direction_value,
                        asset_symbol=asset_code
                    )
                
                # 显示结果
                st.success("✅ 计算完成")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("当前价格", f"¥{target.current_price:.4f}")
                
                with col2:
                    st.metric(
                        "止损价格",
                        f"¥{target.stop_loss_price:.4f}",
                        delta=f"-{target.stop_loss_pct:.1%}"
                    )
                
                with col3:
                    st.metric(
                        "止盈价格",
                        f"¥{target.take_profit_price:.4f}",
                        delta=f"+{target.take_profit_pct:.1%}"
                    )
                
                st.markdown("---")
                
                # 详细信息
                st.markdown("### 📋 详细信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**方法**: {target.method}")
                    st.write(f"**交易方向**: {direction}")
                    st.write(f"**止损幅度**: {target.stop_loss_pct:.2%}")
                    st.write(f"**止盈幅度**: {target.take_profit_pct:.2%}")
                
                with col2:
                    if target.atr_value:
                        st.write(f"**ATR值**: {target.atr_value:.4f}")
                        st.write(f"**ATR倍数**: {target.atr_multiplier:.1f}x")
                    
                    rr_ratio = target.take_profit_pct / target.stop_loss_pct if target.stop_loss_pct > 0 else 0
                    st.write(f"**风险收益比**: 1:{rr_ratio:.2f}")
                
                st.info(f"💡 {target.reason}")
                
                # 可视化
                st.markdown("---")
                st.markdown("### 📊 价格分布")
                
                price_range = [
                    target.stop_loss_price,
                    target.current_price,
                    target.take_profit_price
                ]
                labels = ['止损', '当前', '止盈']
                
                chart_data = pd.DataFrame({
                    '价格': price_range,
                    '类型': labels
                })
                
                st.bar_chart(chart_data.set_index('类型'))
                
            except Exception as e:
                st.error(f"❌ 计算失败: {str(e)}")
                logger.error(f"止损止盈计算错误: {e}", exc_info=True)


def show_risk_monitoring(config):
    """显示风险监控告警"""
    st.subheader("🚨 风险监控告警")
    
    st.markdown("""
    实时监控风险指标，及时发现潜在风险。
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_code = st.text_input("资产代码", value="513500", key="mon_asset_code")
        current_position = st.slider("当前仓位", 0.0, 1.0, 0.2, 0.05, format="%.1f", key="mon_position")
    
    with col2:
        max_drawdown_threshold = st.slider("回撤阈值", 0.05, 0.50, 0.20, 0.05, format="%.2f", key="mon_dd_threshold")
        volatility_threshold = st.slider("波动率阈值", 0.10, 1.00, 0.40, 0.10, format="%.2f", key="mon_vol_threshold")
    
    if st.button("🔍 开始监控", key="start_monitoring"):
        with st.spinner("正在监控..."):
            try:
                from risk_management import RiskMonitor
                from data.fetcher_akshare import AKShareFetcher
                
                # 获取数据
                fetcher = AKShareFetcher()
                data = fetcher.fetch_etf_hist(asset_code, period="6m")
                
                if data is None or len(data) < 30:
                    st.error("❌ 无法获取足够的历史数据")
                    return
                
                # 配置监控器
                monitor_config = {
                    'max_drawdown_threshold': max_drawdown_threshold,
                    'volatility_threshold': volatility_threshold
                }
                risk_monitor = RiskMonitor(monitor_config)
                
                # 监控资产风险
                metrics, alerts = risk_monitor.monitor_asset_risk(
                    data,
                    asset_symbol=asset_code,
                    current_position=current_position
                )
                
                # 显示结果
                st.success("✅ 监控完成")
                
                # 风险概览
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'extreme': '🔴'}
                    st.metric(
                        "风险等级",
                        f"{risk_emoji.get(metrics.risk_level, '⚪')} {metrics.risk_level.upper()}"
                    )
                
                with col2:
                    st.metric("风险评分", f"{metrics.risk_score:.0f}/100")
                
                with col3:
                    st.metric("告警数量", len(alerts))
                
                with col4:
                    critical_count = sum(1 for a in alerts if a.alert_type == 'critical')
                    st.metric("严重告警", critical_count)
                
                # 告警列表
                if alerts:
                    st.markdown("---")
                    st.markdown("### 🚨 风险告警")
                    
                    for alert in alerts:
                        alert_emoji = {
                            'info': 'ℹ️',
                            'warning': '⚠️',
                            'critical': '🔴'
                        }
                        emoji = alert_emoji.get(alert.alert_type, '📢')
                        
                        with st.expander(f"{emoji} {alert.title} ({alert.alert_type.upper()})"):
                            st.write(f"**资产**: {alert.asset_symbol}")
                            st.write(f"**时间**: {alert.timestamp}")
                            st.write(f"**消息**: {alert.message}")
                            st.write(f"**指标**: {alert.metric_name} = {alert.metric_value:.2f}")
                            st.write(f"**阈值**: {alert.threshold:.2f}")
                            st.write(f"**严重程度**: {'⭐' * alert.severity}")
                            
                            if alert.suggested_action:
                                st.info(f"💡 建议操作: {alert.suggested_action}")
                else:
                    st.success("✅ 暂无风险告警")
                
                # 关键指标
                st.markdown("---")
                st.markdown("### 📊 关键风险指标")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"最大回撤: {metrics.max_drawdown:.2%}")
                    st.write(f"波动率: {metrics.volatility:.2%}")
                    st.write(f"VaR (95%): {metrics.var_95:.2%}")
                
                with col2:
                    st.write(f"夏普比率: {metrics.sharpe_ratio:.2f}")
                    st.write(f"索提诺比率: {metrics.sortino_ratio:.2f}")
                    st.write(f"胜率: {metrics.win_rate:.1%}")
                
                with col3:
                    st.write(f"年化收益: {metrics.annualized_return:.2%}")
                    st.write(f"CVaR (95%): {metrics.cvar_95:.2%}")
                    st.write(f"盈亏比: {metrics.profit_loss_ratio:.2f}")
                
            except Exception as e:
                st.error(f"❌ 监控失败: {str(e)}")
                logger.error(f"风险监控错误: {e}", exc_info=True)

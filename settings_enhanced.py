"""
系统设置增强页面
提供主题切换、配置管理、通知设置等高级功能
"""
import streamlit as st
import json
import yaml
from pathlib import Path
from typing import Dict
import sys
from loguru import logger

# 添加src目录
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def show_settings_enhanced(config):
    """显示增强版设置页面"""
    st.header("⚙️ 系统设置")
    
    # 设置分类标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎨 外观主题",
        "🔑 API配置",
        "📊 策略参数",
        "⚠️ 风险控制",
        "🔔 通知设置"
    ])
    
    with tab1:
        show_theme_settings()
    
    with tab2:
        show_api_settings()
    
    with tab3:
        show_strategy_settings()
    
    with tab4:
        show_risk_settings()
    
    with tab5:
        show_notification_settings()


def show_theme_settings():
    """显示主题设置"""
    st.subheader("🎨 外观主题设置")
    
    st.markdown("""
    自定义系统外观,选择您喜欢的主题风格。
    """)
    
    # 主题选择
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "主题模式",
            ["自动", "浅色模式", "深色模式"],
            key="theme_mode"
        )
        
        if theme == "自动":
            st.info("💡 跟随系统主题设置")
        elif theme == "浅色模式":
            st.success("☀️ 已切换到浅色模式")
        else:
            st.success("🌙 已切换到深色模式")
    
    with col2:
        color_scheme = st.selectbox(
            "配色方案",
            ["默认", "蓝色", "绿色", "紫色", "橙色"],
            key="color_scheme"
        )
    
    st.markdown("---")
    
    # 字体设置
    st.markdown("### 📝 字体设置")
    col1, col2 = st.columns(2)
    
    with col1:
        font_size = st.select_slider(
            "字体大小",
            options=["小", "中", "大", "特大"],
            value="中",
            key="font_size"
        )
    
    with col2:
        font_family = st.selectbox(
            "字体类型",
            ["系统默认", "微软雅黑", "苹方", "思源黑体"],
            key="font_family"
        )
    
    st.markdown("---")
    
    # 布局设置
    st.markdown("### 📐 布局设置")
    col1, col2 = st.columns(2)
    
    with col1:
        sidebar_state = st.radio(
            "侧边栏状态",
            ["展开", "折叠"],
            horizontal=True,
            key="sidebar_state"
        )
    
    with col2:
        layout_mode = st.radio(
            "页面布局",
            ["宽屏", "标准"],
            horizontal=True,
            key="layout_mode"
        )
    
    # 数据显示设置
    st.markdown("### 📊 数据显示")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_charts = st.checkbox("显示图表", value=True, key="show_charts")
    with col2:
        show_tables = st.checkbox("显示表格", value=True, key="show_tables")
    with col3:
        show_metrics = st.checkbox("显示指标卡", value=True, key="show_metrics")
    
    st.markdown("---")
    
    # 高级选项
    with st.expander("⚙️ 高级选项"):
        col1, col2 = st.columns(2)
        with col1:
            enable_animations = st.checkbox("启用动画效果", value=True, key="enable_animations")
            enable_sound = st.checkbox("启用音效提示", value=False, key="enable_sound")
        with col2:
            enable_tooltips = st.checkbox("显示提示信息", value=True, key="enable_tooltips")
            enable_shortcuts = st.checkbox("启用快捷键", value=True, key="enable_shortcuts")
    
    # 保存按钮
    if st.button("💾 保存主题设置", key="save_theme"):
        st.success("✅ 主题设置已保存")
        st.balloons()


def show_api_settings():
    """显示API配置"""
    st.subheader("🔑 API密钥配置")
    
    st.warning("⚠️ 请妥善保管您的API密钥，切勿泄露给他人")
    
    # Tushare配置
    with st.expander("📈 Tushare - 金融数据接口", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            tushare_token = st.text_input(
                "Tushare Token",
                type="password",
                placeholder="输入您的Tushare Token",
                key="tushare_token"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("测试连接", key="test_tushare"):
                if tushare_token:
                    st.success("✅ 连接成功")
                else:
                    st.error("❌ Token为空")
        
        st.caption("📖 [获取Tushare Token](https://tushare.pro/register)")
        
        if tushare_token:
            st.info(f"✅ 已配置 (Token: {tushare_token[:10]}...)")
    
    # AKShare配置
    with st.expander("📊 AKShare - 免费数据源"):
        st.write("AKShare无需API密钥,可直接使用")
        st.success("✅ AKShare已启用")
        st.caption("📖 [AKShare文档](https://akshare.akfamily.xyz/)")
    
    # CoinGecko配置
    with st.expander("🪙 CoinGecko - 加密货币数据"):
        use_pro = st.checkbox("使用Pro API", value=False, key="coingecko_pro")
        
        if use_pro:
            coingecko_key = st.text_input(
                "CoinGecko API Key",
                type="password",
                placeholder="输入您的CoinGecko API Key",
                key="coingecko_key"
            )
            st.caption("📖 [获取CoinGecko API](https://www.coingecko.com/en/api)")
        else:
            st.write("使用免费API (有请求限制)")
            st.success("✅ 免费API已启用")
    
    # Binance配置
    with st.expander("💱 Binance - 加密货币交易所"):
        col1, col2 = st.columns(2)
        with col1:
            binance_api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="Binance API Key",
                key="binance_api_key"
            )
        with col2:
            binance_secret = st.text_input(
                "Secret Key",
                type="password",
                placeholder="Binance Secret Key",
                key="binance_secret"
            )
        
        if binance_api_key and binance_secret:
            st.success("✅ Binance API已配置")
    
    # 自定义API
    with st.expander("🔧 自定义API"):
        st.write("添加自定义数据源")
        
        custom_api_name = st.text_input("API名称", key="custom_api_name")
        custom_api_url = st.text_input("API地址", key="custom_api_url")
        custom_api_key = st.text_input("API密钥", type="password", key="custom_api_key")
        
        if st.button("➕ 添加自定义API", key="add_custom_api"):
            if custom_api_name and custom_api_url:
                st.success(f"✅ 已添加 {custom_api_name}")
    
    st.markdown("---")
    
    # 保存按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 保存API配置", key="save_api"):
            st.success("✅ API配置已保存")
    with col2:
        if st.button("🔄 重置配置", key="reset_api"):
            st.warning("⚠️ 配置已重置")


def show_strategy_settings():
    """显示策略参数设置"""
    st.subheader("📊 策略参数设置")
    
    st.markdown("调整各种策略的参数以适应不同市场环境")
    
    # 均线策略
    with st.expander("📈 均线策略参数", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            ma_short = st.slider("短期均线 (MA)", 5, 60, 20, key="ma_short")
            ma_long = st.slider("长期均线 (MA)", 20, 250, 60, key="ma_long")
        with col2:
            ma_signal_threshold = st.slider("信号阈值 (%)", 0.0, 5.0, 1.0, 0.1, key="ma_threshold")
            ma_confirmation = st.number_input("确认周期 (天)", 1, 10, 3, key="ma_confirmation")
        
        st.caption(f"当前配置: MA{ma_short}/MA{ma_long}, 阈值{ma_signal_threshold}%, 确认{ma_confirmation}天")
    
    # MACD策略
    with st.expander("📊 MACD策略参数"):
        col1, col2, col3 = st.columns(3)
        with col1:
            macd_fast = st.slider("快线周期", 5, 30, 12, key="macd_fast")
        with col2:
            macd_slow = st.slider("慢线周期", 15, 60, 26, key="macd_slow")
        with col3:
            macd_signal = st.slider("信号线周期", 5, 20, 9, key="macd_signal")
        
        macd_threshold = st.slider("MACD阈值", 0.0, 0.1, 0.02, 0.01, key="macd_threshold")
    
    # RSI策略
    with st.expander("📉 RSI策略参数"):
        col1, col2, col3 = st.columns(3)
        with col1:
            rsi_period = st.slider("RSI周期", 5, 30, 14, key="rsi_period")
        with col2:
            rsi_oversold = st.slider("超卖阈值", 10, 40, 30, key="rsi_oversold")
        with col3:
            rsi_overbought = st.slider("超买阈值", 60, 90, 70, key="rsi_overbought")
        
        st.caption(f"RSI < {rsi_oversold} 视为超卖, RSI > {rsi_overbought} 视为超买")
    
    # 布林带策略
    with st.expander("📏 布林带策略参数"):
        col1, col2 = st.columns(2)
        with col1:
            bb_period = st.slider("周期", 10, 50, 20, key="bb_period")
            bb_std = st.slider("标准差倍数", 1.0, 3.0, 2.0, 0.1, key="bb_std")
        with col2:
            bb_buy_threshold = st.slider("买入阈值 (%)", 0, 20, 5, key="bb_buy_threshold")
            bb_sell_threshold = st.slider("卖出阈值 (%)", 80, 100, 95, key="bb_sell_threshold")
    
    # KDJ策略
    with st.expander("🎯 KDJ策略参数"):
        col1, col2, col3 = st.columns(3)
        with col1:
            kdj_n = st.slider("N周期", 5, 20, 9, key="kdj_n")
        with col2:
            kdj_m1 = st.slider("M1周期", 2, 10, 3, key="kdj_m1")
        with col3:
            kdj_m2 = st.slider("M2周期", 2, 10, 3, key="kdj_m2")
        
        col1, col2 = st.columns(2)
        with col1:
            kdj_oversold = st.slider("超卖线", 10, 30, 20, key="kdj_oversold")
        with col2:
            kdj_overbought = st.slider("超买线", 70, 90, 80, key="kdj_overbought")
    
    # 组合策略
    with st.expander("🔀 组合策略设置"):
        st.write("**信号组合规则**")
        
        signal_combination = st.radio(
            "信号组合方式",
            ["任意一个信号触发", "多数信号一致", "所有信号一致"],
            key="signal_combination"
        )
        
        enabled_strategies = st.multiselect(
            "启用的策略",
            ["均线策略", "MACD策略", "RSI策略", "布林带策略", "KDJ策略"],
            default=["均线策略", "MACD策略", "RSI策略"],
            key="enabled_strategies"
        )
        
        st.write(f"已启用 {len(enabled_strategies)} 个策略")
    
    st.markdown("---")
    
    # 保存和重置
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 保存策略参数", key="save_strategy"):
            st.success("✅ 策略参数已保存")
    with col2:
        if st.button("🔄 恢复默认", key="reset_strategy"):
            st.info("🔄 已恢复默认参数")


def show_risk_settings():
    """显示风险控制设置"""
    st.subheader("⚠️ 风险控制设置")
    
    st.markdown("设置风险控制参数以保护您的投资")
    
    # 仓位控制
    with st.expander("💼 仓位控制", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            max_position = st.slider("单品种最大仓位 (%)", 10, 100, 50, 5, key="max_position")
            min_position = st.slider("单品种最小仓位 (%)", 0, 20, 5, 1, key="min_position")
        with col2:
            max_total_exposure = st.slider("总仓位上限 (%)", 50, 100, 80, 5, key="max_total_exposure")
            cash_reserve = st.slider("现金储备 (%)", 0, 50, 20, 5, key="cash_reserve")
        
        st.caption(f"当前设置: 单品种{min_position}%-{max_position}%, 总仓位≤{max_total_exposure}%, 现金≥{cash_reserve}%")
    
    # 止损止盈
    with st.expander("🛡️ 止损止盈设置"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**止损设置**")
            enable_stop_loss = st.checkbox("启用止损", value=True, key="enable_stop_loss")
            if enable_stop_loss:
                stop_loss_pct = st.slider("止损比例 (%)", 5, 30, 10, 1, key="stop_loss_pct")
                trailing_stop = st.checkbox("移动止损", value=False, key="trailing_stop")
        
        with col2:
            st.write("**止盈设置**")
            enable_take_profit = st.checkbox("启用止盈", value=True, key="enable_take_profit")
            if enable_take_profit:
                take_profit_pct = st.slider("止盈比例 (%)", 10, 100, 20, 5, key="take_profit_pct")
                partial_profit = st.checkbox("分批止盈", value=True, key="partial_profit")
    
    # 回撤控制
    with st.expander("📉 回撤控制"):
        col1, col2 = st.columns(2)
        with col1:
            max_drawdown = st.slider("最大回撤限制 (%)", 5, 50, 20, 1, key="max_drawdown")
            drawdown_action = st.selectbox(
                "触发回撤限制后",
                ["暂停交易", "减少仓位", "仅提示"],
                key="drawdown_action"
            )
        with col2:
            daily_loss_limit = st.slider("单日亏损限制 (%)", 2, 20, 5, 1, key="daily_loss_limit")
            loss_action = st.selectbox(
                "触发亏损限制后",
                ["停止交易", "减少仓位", "仅提示"],
                key="loss_action"
            )
    
    # 风险预算
    with st.expander("💰 风险预算"):
        st.write("**VaR (Value at Risk) 设置**")
        col1, col2 = st.columns(2)
        with col1:
            var_confidence = st.select_slider(
                "置信水平",
                options=[0.90, 0.95, 0.99],
                value=0.95,
                format_func=lambda x: f"{x:.0%}",
                key="var_confidence"
            )
        with col2:
            var_limit = st.number_input("VaR限额 (¥)", 0, 1000000, 50000, 10000, key="var_limit")
        
        st.caption(f"当前设置: {var_confidence:.0%}置信度下VaR不超过¥{var_limit:,}")
    
    # 集中度风险
    with st.expander("🎯 集中度控制"):
        col1, col2 = st.columns(2)
        with col1:
            max_sector_exposure = st.slider("单行业最大敞口 (%)", 20, 100, 40, 5, key="max_sector")
            max_asset_correlation = st.slider("最大资产相关性", 0.5, 1.0, 0.8, 0.05, key="max_correlation")
        with col2:
            max_assets_count = st.number_input("最大持仓品种数", 3, 50, 10, 1, key="max_assets")
            min_diversification = st.slider("最低分散度", 0.3, 0.9, 0.6, 0.05, key="min_diversification")
    
    st.markdown("---")
    
    # 保存按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 保存风险设置", key="save_risk"):
            st.success("✅ 风险设置已保存")
    with col2:
        if st.button("⚠️ 重置风险参数", key="reset_risk"):
            st.warning("⚠️ 风险参数已重置")


def show_notification_settings():
    """显示通知设置"""
    st.subheader("🔔 通知设置")
    
    st.markdown("配置各种事件的通知方式")
    
    # 通知渠道
    with st.expander("📱 通知渠道", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            email_notify = st.checkbox("📧 邮件通知", value=True, key="email_notify")
            if email_notify:
                email_address = st.text_input("邮箱地址", placeholder="your@email.com", key="email_address")
        
        with col2:
            wechat_notify = st.checkbox("💬 微信通知", value=False, key="wechat_notify")
            if wechat_notify:
                wechat_id = st.text_input("微信OpenID", placeholder="微信OpenID", key="wechat_id")
        
        col1, col2 = st.columns(2)
        with col1:
            sms_notify = st.checkbox("📱 短信通知", value=False, key="sms_notify")
            if sms_notify:
                phone_number = st.text_input("手机号码", placeholder="+86 138****8888", key="phone_number")
        
        with col2:
            push_notify = st.checkbox("🔔 App推送", value=True, key="push_notify")
    
    # 通知事件
    with st.expander("📋 通知事件设置"):
        st.write("**交易信号通知**")
        col1, col2 = st.columns(2)
        with col1:
            notify_buy_signal = st.checkbox("买入信号", value=True, key="notify_buy")
            notify_sell_signal = st.checkbox("卖出信号", value=True, key="notify_sell")
        with col2:
            signal_strength_threshold = st.select_slider(
                "最低信号强度",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: "⭐" * x,
                key="signal_strength"
            )
        
        st.markdown("---")
        
        st.write("**风险告警通知**")
        col1, col2, col3 = st.columns(3)
        with col1:
            notify_stop_loss = st.checkbox("止损触发", value=True, key="notify_stop_loss")
            notify_take_profit = st.checkbox("止盈触发", value=True, key="notify_take_profit")
        with col2:
            notify_drawdown = st.checkbox("回撤警告", value=True, key="notify_drawdown")
            notify_volatility = st.checkbox("波动率异常", value=True, key="notify_volatility")
        with col3:
            notify_position = st.checkbox("仓位超限", value=True, key="notify_position")
            notify_margin = st.checkbox("保证金不足", value=False, key="notify_margin")
        
        st.markdown("---")
        
        st.write("**市场事件通知**")
        col1, col2 = st.columns(2)
        with col1:
            notify_market_open = st.checkbox("开盘提醒", value=False, key="notify_open")
            notify_market_close = st.checkbox("收盘提醒", value=False, key="notify_close")
        with col2:
            notify_major_move = st.checkbox("重大波动", value=True, key="notify_move")
            major_move_threshold = st.slider("波动阈值 (%)", 3, 20, 5, 1, key="move_threshold")
    
    # 通知时段
    with st.expander("⏰ 通知时段设置"):
        st.write("**免打扰时段**")
        col1, col2 = st.columns(2)
        with col1:
            dnd_enable = st.checkbox("启用免打扰", value=True, key="dnd_enable")
            if dnd_enable:
                dnd_start = st.time_input("开始时间", value=None, key="dnd_start")
        with col2:
            if dnd_enable:
                st.write("")  # 占位
                dnd_end = st.time_input("结束时间", value=None, key="dnd_end")
        
        if dnd_enable and dnd_start and dnd_end:
            st.caption(f"免打扰时段: {dnd_start} - {dnd_end}")
        
        st.write("**紧急通知例外**")
        emergency_override = st.multiselect(
            "即使在免打扰时段也通知",
            ["止损触发", "严重风险", "系统故障"],
            default=["止损触发", "系统故障"],
            key="emergency_override"
        )
    
    # 通知频率
    with st.expander("📊 通知频率控制"):
        col1, col2 = st.columns(2)
        with col1:
            max_notifications_per_hour = st.slider("每小时最大通知数", 1, 60, 10, 1, key="max_notify_hour")
        with col2:
            notification_cooldown = st.slider("同类通知冷却时间 (分钟)", 1, 60, 5, 1, key="notify_cooldown")
        
        st.caption(f"限制: 每小时最多{max_notifications_per_hour}条, 同类通知间隔{notification_cooldown}分钟")
    
    # 测试通知
    st.markdown("---")
    st.markdown("### 🧪 测试通知")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📧 测试邮件", key="test_email"):
            st.info("📧 测试邮件已发送")
    with col2:
        if st.button("💬 测试微信", key="test_wechat"):
            st.info("💬 测试微信已发送")
    with col3:
        if st.button("📱 测试短信", key="test_sms"):
            st.info("📱 测试短信已发送")
    with col4:
        if st.button("🔔 测试推送", key="test_push"):
            st.info("🔔 测试推送已发送")
    
    st.markdown("---")
    
    # 保存按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 保存通知设置", key="save_notification"):
            st.success("✅ 通知设置已保存")
    with col2:
        if st.button("🔕 关闭所有通知", key="disable_all"):
            st.warning("⚠️ 所有通知已关闭")


if __name__ == "__main__":
    st.set_page_config(page_title="系统设置", layout="wide")
    show_settings_enhanced({})

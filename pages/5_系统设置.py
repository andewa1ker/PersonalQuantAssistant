"""
⚙️ 系统设置
"""
import streamlit as st
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, form_row, pill_badge
from utils.system_config_manager import SystemConfigManager

inject_css()

# 初始化配置管理器
@st.cache_resource
def init_config_manager():
    return SystemConfigManager()

config_mgr = init_config_manager()

st.title('⚙️ 系统设置')
st.caption('个性化配置 · 安全管理')

st.divider()

# 账户信息
section_header('settings', '账户信息', '个人资料与偏好设置')

with st.expander('👤 个人资料', expanded=True):
    # 加载当前配置
    user_config = config_mgr.get_section('user')
    
    username = st.text_input('用户名', value=user_config.get('username', ''), key='username')
    email = st.text_input('邮箱', value=user_config.get('email', ''), key='email')
    risk_pref = st.select_slider('风险偏好', 
                                   options=['保守', '稳健', '平衡', '进取', '激进'], 
                                   value=user_config.get('risk_preference', '平衡'), 
                                   key='risk_pref')
    
    if st.button('💾 保存资料', type='primary'):
        if config_mgr.update_section('user', {
            'username': username,
            'email': email,
            'risk_preference': risk_pref
        }):
            st.success('✅ 资料已更新并保存')
            st.rerun()
        else:
            st.error('❌ 保存失败')

st.divider()

# 交易设置
section_header('sliders-vertical', '交易设置', '默认参数与自动化配置')

with st.expander('🎯 默认参数', expanded=False):
    # 加载当前配置
    trading_config = config_mgr.get_section('trading')
    
    default_stop_loss = st.slider('默认止损 (%)', 0.0, 20.0, 
                                    trading_config.get('default_stop_loss', 0.05) * 100, 
                                    0.5, key='default_stop_loss')
    default_take_profit = st.slider('默认止盈 (%)', 0.0, 50.0, 
                                      trading_config.get('default_take_profit', 0.15) * 100, 
                                      1.0, key='default_take_profit')
    max_position = st.slider('单资产最大仓位 (%)', 0, 100, 
                              int(trading_config.get('max_position_per_asset', 0.30) * 100), 
                              5, key='max_position')
    auto_rebalance = st.toggle('启用自动再平衡', 
                                value=trading_config.get('auto_rebalance', False), 
                                key='auto_rebalance')
    
    if st.button('💾 保存设置', type='primary'):
        if config_mgr.update_section('trading', {
            'default_stop_loss': default_stop_loss / 100,
            'default_take_profit': default_take_profit / 100,
            'max_position_per_asset': max_position / 100,
            'auto_rebalance': auto_rebalance
        }):
            st.success('✅ 交易设置已保存')
            st.rerun()
        else:
            st.error('❌ 保存失败')

st.divider()

# 数据源配置
section_header('database-export', '数据源', '接入外部数据服务')

# 获取真实数据源状态
data_config = config_mgr.get_section('data_sources')

# 显示数据源状态
data_sources_info = [
    {'name': 'CoinGecko', 'key': 'coingecko', 'desc': '加密货币数据'},
    {'name': 'Tushare', 'key': 'tushare', 'desc': 'A股和ETF数据'},
    {'name': 'AKShare', 'key': 'akshare', 'desc': '备用数据源'},
]

for ds in data_sources_info:
    ds_config = data_config.get(ds['key'], {})
    enabled = ds_config.get('enabled', False)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div style="font-weight:500;padding:0.5rem 0">{ds["name"]}</div>', unsafe_allow_html=True)
        st.caption(ds['desc'])
    with col2:
        status = "已启用" if enabled else "已禁用"
        tone = "success" if enabled else "neutral"
        st.markdown(pill_badge(status, tone), unsafe_allow_html=True)
    with col3:
        if st.toggle('启用', value=enabled, key=f'enable_{ds["key"]}'):
            ds_config['enabled'] = True
        else:
            ds_config['enabled'] = False
        data_config[ds['key']] = ds_config

config_mgr.update_section('data_sources', data_config)

st.divider()

# 通知设置
section_header('bell', '通知偏好', '消息推送与提醒')

notif_config = config_mgr.get_section('notifications')

col1, col2 = st.columns(2)
with col1:
    email_notif = st.checkbox('📧 邮件通知', value=notif_config.get('email', False), key='email_notif')
    signal_alert = st.checkbox('🔔 信号提醒', value=notif_config.get('signal_alert', True), key='signal_alert')
with col2:
    price_alert = st.checkbox('� 价格提醒', value=notif_config.get('price_alert', True), key='price_alert')
    risk_alert = st.checkbox('⚠️ 风险预警', value=notif_config.get('risk_alert', True), key='risk_alert')

if st.button('💾 保存通知设置', type='primary'):
    if config_mgr.update_section('notifications', {
        'email': email_notif,
        'signal_alert': signal_alert,
        'price_alert': price_alert,
        'risk_alert': risk_alert
    }):
        st.success('✅ 通知设置已保存')
        st.rerun()
    else:
        st.error('❌ 保存失败')

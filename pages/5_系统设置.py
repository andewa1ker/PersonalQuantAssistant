"""
⚙️ 系统设置
"""
import streamlit as st
from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, form_row, pill_badge

inject_css()

st.title('⚙️ 系统设置')
st.caption('个性化配置 · 安全管理')

st.divider()

# 账户信息
section_header('settings', '账户信息', '个人资料与偏好设置')

with st.expander('👤 个人资料', expanded=True):
    form_row('用户名', lambda: st.text_input('', value='张三', key='username', label_visibility='collapsed'))
    form_row('邮箱', lambda: st.text_input('', value='zhangsan@example.com', key='email', label_visibility='collapsed'))
    form_row('风险偏好', lambda: st.select_slider('', options=['保守', '稳健', '平衡', '进取', '激进'], value='平衡', key='risk_pref', label_visibility='collapsed'))
    
    if st.button('💾 保存资料', use_container_width=True):
        st.success('✅ 资料已更新')

st.divider()

# 交易设置
section_header('sliders-vertical', '交易设置', '默认参数与自动化配置')

with st.expander('🎯 默认参数', expanded=False):
    form_row('默认止损', lambda: st.slider('', 0.0, 20.0, 5.0, 0.5, key='default_stop_loss', label_visibility='collapsed', format='%g%%'))
    form_row('默认止盈', lambda: st.slider('', 0.0, 50.0, 15.0, 1.0, key='default_take_profit', label_visibility='collapsed', format='%g%%'))
    form_row('单笔最大仓位', lambda: st.slider('', 0, 100, 20, 5, key='max_position', label_visibility='collapsed', format='%g%%'))
    form_row('启用自动交易', lambda: st.toggle('', value=False, key='auto_trade'))
    
    if st.button('💾 保存设置', use_container_width=True):
        st.success('✅ 设置已更新')

st.divider()

# 数据源配置
section_header('database-export', '数据源', '接入外部数据服务')

data_sources = [
    {'name': 'Tushare', 'status': '已连接', 'tone': 'success'},
    {'name': 'Wind', 'status': '未配置', 'tone': 'neutral'},
    {'name': 'AKShare', 'status': '已连接', 'tone': 'success'},
    {'name': 'BaoStock', 'status': '连接失败', 'tone': 'danger'},
]

for ds in data_sources:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div style="font-weight:500;padding:0.5rem 0">{ds["name"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(pill_badge(ds['status'], ds['tone']), unsafe_allow_html=True)
    with col3:
        st.button('配置', key=f'config_{ds["name"]}', use_container_width=True)

st.divider()

# 安全设置
section_header('shield-check', '安全设置', '密码与验证')

with st.expander('🔒 修改密码', expanded=False):
    form_row('当前密码', lambda: st.text_input('', type='password', key='old_pwd', label_visibility='collapsed'))
    form_row('新密码', lambda: st.text_input('', type='password', key='new_pwd', label_visibility='collapsed'))
    form_row('确认密码', lambda: st.text_input('', type='password', key='confirm_pwd', label_visibility='collapsed'))
    
    if st.button('🔐 修改密码', use_container_width=True):
        st.success('✅ 密码已更新')

st.divider()

# 通知设置
section_header('bell', '通知偏好', '消息推送与提醒')

col1, col2 = st.columns(2)
with col1:
    st.checkbox('📧 邮件通知', value=True)
    st.checkbox('🔔 信号提醒', value=True)
with col2:
    st.checkbox('📱 短信通知', value=False)
    st.checkbox('⚠️ 风险预警', value=True)

if st.button('💾 保存通知设置', use_container_width=True):
    st.success('✅ 通知设置已更新')

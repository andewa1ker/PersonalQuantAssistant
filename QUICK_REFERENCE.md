# Premium UI 快速参考

## 🎨 颜色系统

```python
from styles_premium import DESIGN_TOKENS

# 背景色
DESIGN_TOKENS['bg_primary']      # #0B0B0F
DESIGN_TOKENS['bg_secondary']    # #14141A
DESIGN_TOKENS['bg_card']         # #1E1E26

# 主高光
DESIGN_TOKENS['primary_solid']   # #FF7A29
DESIGN_TOKENS['primary_start']   # #FF6A00
DESIGN_TOKENS['primary_end']     # #FFA54C

# 文本色
DESIGN_TOKENS['text_primary']    # #FFFFFF
DESIGN_TOKENS['text_secondary']  # rgba(255, 255, 255, 0.78)
DESIGN_TOKENS['text_tertiary']   # rgba(255, 255, 255, 0.56)

# 功能色
DESIGN_TOKENS['success']         # #4CAF50
DESIGN_TOKENS['error']           # #EF5350
DESIGN_TOKENS['warning']         # #FFA726
DESIGN_TOKENS['info']            # #42A5F5
```

## 📦 常用组件

### 1. 账户卡
```python
from components_premium import render_balance_card

balance = {
    "total": 27802.05,
    "change_pct": 0.15,
    "change_amount": 412.50
}
render_balance_card(balance)
```

### 2. 收益曲线
```python
from components_premium import render_profit_chart

chart_data = {
    "dates": ["2024-01", "2024-02", "2024-03"],
    "values": [10000, 12000, 15000]
}
render_profit_chart(chart_data, "月度收益")
```

### 3. 交易列表
```python
from components_premium import render_transaction_list

transactions = [
    {
        "title": "工资收入",
        "tag": "月薪",
        "amount": 5000,
        "time": "今天",
        "icon": "wallet"
    }
]
render_transaction_list(transactions)
```

### 4. KPI 卡
```python
from components_premium import render_kpi_card

render_kpi_card("总资产", "¥50,000", "+12%", "wallet")
```

### 5. 环形图
```python
from components_premium import render_donut_chart

render_donut_chart(0.75, "完成率", '#FF7A29')
```

## 🎯 图标使用

```python
from icons import icon, icon_html, get_icon_group

# 获取 SVG
svg = icon('wallet', size=24, color='#FF7A29')

# HTML 包装
html = icon_html('trending_up', size=20)

# 预定义组合
buy_icon = get_icon_group('trade_buy')    # 买入 橙色
sell_icon = get_icon_group('trade_sell')   # 卖出 灰青
```

### 常用图标
- **金融**: wallet, credit_card, dollar_sign, trending_up, trending_down
- **图表**: line_chart, bar_chart, pie_chart, activity
- **操作**: calendar, settings, refresh, download, upload, search, filter
- **状态**: check_circle, alert_triangle, shield_check, info

## 🎬 动画类

```python
# HTML 中使用动画类
<div class="fade-in">淡入</div>
<div class="float-in">浮入</div>
<div class="slide-in-right">右滑入</div>
<div class="glow">发光脉冲</div>
<div class="hover-float">Hover 上浮</div>
```

## 💅 常用样式

### Premium 卡片
```python
st.markdown('''
<div class="premium-card">
    你的内容
</div>
''', unsafe_allow_html=True)
```

### 玻璃卡片
```python
st.markdown('''
<div class="glass-card">
    你的内容
</div>
''', unsafe_allow_html=True)
```

### 徽章
```python
st.markdown('''
<span class="badge badge-success">成功</span>
<span class="badge badge-error">错误</span>
<span class="badge badge-warning">警告</span>
<span class="badge badge-primary">主要</span>
''', unsafe_allow_html=True)
```

### KPI 卡片
```python
st.markdown('''
<div class="kpi-card">
    <div class="kpi-label">标签</div>
    <div class="kpi-value">1,234</div>
    <div class="kpi-change positive">+12%</div>
</div>
''', unsafe_allow_html=True)
```

## 📊 Plotly 图表模板

```python
import plotly.graph_objects as go

fig = go.Figure()

# 添加线条
fig.add_trace(go.Scatter(
    x=dates,
    y=values,
    mode='lines',
    line=dict(color='#FF7A29', width=3, shape='spline'),
    fill='tozeroy',
    fillcolor='rgba(255, 122, 41, 0.15)',
))

# 深色主题布局
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='rgba(255,255,255,0.78)'),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.05)',
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.05)',
    ),
)

st.plotly_chart(fig, use_container_width=True)
```

## 🎭 Lottie 动画

```python
from lottie_animations import (
    show_lottie_animation,
    show_loading_state,
    show_empty_state,
    show_success_animation
)

# 显示加载动画
show_lottie_animation('loading', height=150)

# 加载状态
show_loading_state("正在加载数据...")

# 空态
show_empty_state("暂无数据", "请添加一些交易记录")

# 成功
show_success_animation("操作成功！")
```

## 📱 响应式布局

```python
# 自适应列
col1, col2, col3 = st.columns([1, 2, 1])

# 移动端单列
col1, col2 = st.columns([1, 1])
```

## 🎯 最佳实践

### 1. 页面初始化
```python
import streamlit as st
from styles_premium import inject_premium_styles

st.set_page_config(
    page_title="我的页面",
    layout="wide"
)

inject_premium_styles()
```

### 2. 标题样式
```python
from icons import icon
from styles_premium import DESIGN_TOKENS

st.markdown(f"""
<div style="font-size: 2rem; font-weight: 700;">
    {icon('home', 28, DESIGN_TOKENS['primary_solid'])} 我的页面
</div>
""", unsafe_allow_html=True)
```

### 3. 分割线
```python
from styles_premium import create_divider

create_divider(gradient=True)
```

### 4. Toast 通知
```python
from components_premium import show_toast

show_toast("操作成功", "success")
show_toast("注意", "warning")
show_toast("错误", "error")
show_toast("提示", "info")
```

## 🔧 调试技巧

### 查看 Design Tokens
```python
from styles_premium import DESIGN_TOKENS
import json

st.json(DESIGN_TOKENS)
```

### 测试所有图标
```python
from icons import ICONS

for name in ICONS.keys():
    st.markdown(f"{icon(name)} {name}", unsafe_allow_html=True)
```

### 测试所有动画
```python
from lottie_animations import demo_lottie_animations

demo_lottie_animations()
```

## 📚 完整示例

```python
import streamlit as st
import pandas as pd
from styles_premium import inject_premium_styles, DESIGN_TOKENS, create_divider
from components_premium import (
    render_balance_card,
    render_profit_chart,
    render_transaction_list,
    render_kpi_card,
)
from icons import icon, icon_html

# 页面配置
st.set_page_config(page_title="Dashboard", layout="wide")
inject_premium_styles()

# 标题
st.markdown(f"""
<div style="font-size: 2rem; font-weight: 700;">
    {icon('home', 28, DESIGN_TOKENS['primary_solid'])} 投资仪表板
</div>
""", unsafe_allow_html=True)

create_divider()

# 数据
balance = {"total": 50000, "change_pct": 0.12, "change_amount": 5000}
chart_data = {
    "dates": ["1月", "2月", "3月"],
    "values": [40000, 45000, 50000]
}

# 布局
col1, col2 = st.columns([1, 2])

with col1:
    render_balance_card(balance)

with col2:
    render_profit_chart(chart_data)

# KPI
st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card("总资产", "¥50,000", "+12%", "wallet")
with col2:
    render_kpi_card("本月收益", "¥5,000", "+15%", "trending_up")
with col3:
    render_kpi_card("胜率", "68%", "+3%", "target")
with col4:
    render_kpi_card("夏普比率", "1.52", "+0.08", "shield_check")
```

## 🎉 开始使用

复制上面的任意代码片段到你的 Streamlit 应用中，立即获得 Premium 深色金融风格！

---

**提示**: 所有组件都支持自定义参数，详见各函数的 docstring。

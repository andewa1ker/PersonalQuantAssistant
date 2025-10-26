# Premium UI 升级完成指南

## 🎉 升级概览

您的个人量化助手已成功升级为 **Premium 深色金融风格** UI！

### ✨ 新增特性

1. **深色金融风格主题**
   - 炭黑背景渐变 (#0B0B0F → #14141A)
   - 琥珀橙高光 (#FF6A00 → #FFA54C)
   - 圆角卡片 (18px) + 玻璃质感
   - 丝滑动画 (200-250ms cubic-bezier)

2. **统一图标系统**
   - 40+ Lucide 风格 SVG 图标
   - 可自定义尺寸和颜色
   - 响应式设计

3. **高级组件库**
   - 账户总览卡 (余额 + 涨跌徽章)
   - 收益曲线图 (Plotly 平滑曲线 + 面积渐变)
   - 最近交易列表 (Hover 动效)
   - KPI 统计卡 (数字计数动画)
   - 环形进度图
   - 策略信号表格
   - Upcoming 待办卡

4. **全局样式系统**
   - Design Tokens (颜色、间距、圆角等)
   - CSS 动画 (fadeIn, floatIn, pulseGlow)
   - 响应式布局 (移动端友好)
   - 焦点可访问性 (AA 级对比度)

---

## 📁 新增文件

### 1. `.streamlit/config.toml` (已更新)
深色金融主题配置：

```toml
[theme]
base = "dark"
primaryColor = "#FF7A29"
backgroundColor = "#0B0B0F"
secondaryBackgroundColor = "#15151C"
textColor = "#FFFFFF"
font = "sans serif"
```

### 2. `icons.py`
SVG 图标字典，包含：
- 图表图标: line_chart, trending_up, trending_down, bar_chart, pie_chart
- 金融图标: wallet, credit_card, dollar_sign, arrow_up_right, arrow_down_right
- 操作图标: calendar, settings, bell, refresh, download, upload, filter, search
- 状态图标: shield_check, alert_triangle, check_circle, info
- 导航图标: home, activity, layers, target, user

**使用示例：**
```python
from icons import icon, icon_html, get_icon_group

# 获取 SVG 字符串
svg = icon('wallet', size=24, color='#FF7A29')

# 获取包装的 HTML
html = icon_html('trending_up', size=20)

# 获取预定义图标组合
trade_icon = get_icon_group('trade_buy', size=20)
```

### 3. `styles_premium.py`
全局样式系统，包含：
- **Design Tokens**: 颜色、间距、圆角、阴影等
- **CSS 注入函数**: `inject_premium_styles()`
- **动画定义**: fadeIn, floatIn, pulseGlow, slideInRight, shimmer
- **组件样式**: 卡片、按钮、输入框、表格、Tab、Metric 等

**使用示例：**
```python
from styles_premium import inject_premium_styles, DESIGN_TOKENS, create_divider

# 注入全局样式 (在页面配置后调用)
inject_premium_styles()

# 使用 Design Tokens
primary_color = DESIGN_TOKENS['primary_solid']  # '#FF7A29'

# 创建分割线
create_divider(gradient=True)
```

### 4. `components_premium.py`
Premium 组件库，包含：

#### a) 账户总览卡
```python
from components_premium import render_balance_card

balance = {"total": 27802.05, "change_pct": 0.15, "change_amount": 412.50}
user = {"name": "张三"}
render_balance_card(balance, user)
```

#### b) 收益曲线图
```python
from components_premium import render_profit_chart

chart_data = {
    "dates": ["2024-05-01", "2024-06-01", "2024-07-01"],
    "values": [12000, 15000, 17000]
}
render_profit_chart(chart_data, "收益走势")
```

#### c) 最近交易列表
```python
from components_premium import render_transaction_list

transactions = [
    {"title": "工资", "tag": "月薪", "amount": 2010, "time": "今天 14:02", "icon": "wallet"},
    {"title": "投资", "tag": "ETF", "amount": 12010, "time": "昨天", "icon": "trending_up"},
]
render_transaction_list(transactions, "最近交易")
```

#### d) KPI 统计卡
```python
from components_premium import render_kpi_card

render_kpi_card("储蓄率", "75%", "+5%", "wallet")
```

#### e) 环形进度图
```python
from components_premium import render_donut_chart

render_donut_chart(0.75, "储蓄率", '#FF7A29')
```

#### f) 策略信号表格
```python
from components_premium import render_signal_table
import pandas as pd

signals = pd.DataFrame([
    {"资产": "BTC", "信号": "买入", "价格": "¥65,432", "时间": "10:30"},
])
render_signal_table(signals)
```

#### g) Upcoming 待办卡
```python
from components_premium import render_upcoming_card

upcoming = [
    {"name": "域名续费", "amount": 120},
    {"name": "旅行预算", "amount": 2500}
]
render_upcoming_card(upcoming)
```

#### h) Toast 通知
```python
from components_premium import show_toast

show_toast("已同步最新交易", "success")  # success/warning/error/info
```

---

## 🚀 使用指南

### 1. 安装依赖
```powershell
pip install streamlit-lottie
```

或者完整安装：
```powershell
pip install -r requirements.txt
```

### 2. 启动应用
```powershell
streamlit run main.py
```

### 3. 在你的页面中集成 Premium UI

**示例：创建自定义页面**

```python
import streamlit as st
from styles_premium import inject_premium_styles, DESIGN_TOKENS
from components_premium import render_balance_card, render_profit_chart
from icons import icon

# 注入样式
inject_premium_styles()

def my_custom_page():
    """自定义页面"""
    
    # 标题
    st.markdown(f"""
    <div style="font-size: 2rem; font-weight: 700;">
        {icon('home', 28, DESIGN_TOKENS['primary_solid'])} 我的页面
    </div>
    """, unsafe_allow_html=True)
    
    # 使用组件
    col1, col2 = st.columns([1, 2])
    
    with col1:
        balance = {"total": 50000, "change_pct": 0.08, "change_amount": 3200}
        render_balance_card(balance)
    
    with col2:
        chart_data = {
            "dates": ["1月", "2月", "3月"],
            "values": [40000, 45000, 50000]
        }
        render_profit_chart(chart_data)
```

---

## 🎨 定制化

### 修改颜色主题

编辑 `styles_premium.py` 中的 `DESIGN_TOKENS`：

```python
DESIGN_TOKENS = {
    'primary_solid': '#YOUR_COLOR',  # 主高光色
    'bg_primary': '#YOUR_BG',        # 背景色
    # ... 其他配置
}
```

### 添加新图标

在 `icons.py` 的 `ICONS` 字典中添加：

```python
ICONS = {
    'my_icon': '''<svg xmlns="http://www.w3.org/2000/svg" ...></svg>''',
}
```

### 创建新组件

参考 `components_premium.py` 中的组件模式：

```python
def render_my_component(data: dict):
    """自定义组件"""
    html = f"""
    <div class="premium-card">
        <!-- 你的 HTML -->
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
```

---

## 📊 数据绑定

所有组件都使用演示数据，请替换为真实数据：

```python
# 示例：绑定真实数据
def show_premium_dashboard(data_manager, signal_gen, config):
    # 获取真实余额
    portfolio = data_manager.get_portfolio_data()
    balance = {
        "total": portfolio['total_value'],
        "change_pct": portfolio['daily_change_pct'],
        "change_amount": portfolio['daily_change_amount']
    }
    
    # 获取真实收益曲线
    history = data_manager.get_profit_history()
    chart_data = {
        "dates": history['dates'].tolist(),
        "values": history['values'].tolist()
    }
    
    # 渲染组件
    render_balance_card(balance)
    render_profit_chart(chart_data)
```

---

## 🔧 故障排除

### 样式不生效
确保在页面顶部调用：
```python
from styles_premium import inject_premium_styles
inject_premium_styles()
```

### 图标不显示
检查 `icons.py` 是否正确导入：
```python
from icons import icon, icon_html
```

### Lottie 动画报错
如果不使用 Lottie，可以忽略，代码已做兼容处理。要使用，需安装：
```powershell
pip install streamlit-lottie
```

---

## 📱 响应式支持

所有组件都支持响应式布局：
- ≥1280px: 三列布局
- 1024-1279px: 两列布局
- ≤768px: 单列布局（移动端）

---

## ♿ 可访问性

- 焦点环: `outline: 2px solid #FFA54C`
- 对比度: 符合 WCAG AA 标准
- 语义化 HTML: 适当的 `aria-label`

---

## 🎯 最佳实践

1. **性能优化**
   - 使用 `@st.cache_data` 缓存数据
   - 避免频繁重绘
   - 动画仅对交互元素

2. **一致性**
   - 统一使用 `DESIGN_TOKENS` 中的颜色
   - 统一使用 `icons.py` 中的图标
   - 遵循组件命名规范

3. **可维护性**
   - 组件化开发
   - 分离样式和逻辑
   - 注释清晰

---

## 📚 参考资源

- Streamlit 文档: https://docs.streamlit.io
- Plotly 文档: https://plotly.com/python/
- Lucide Icons: https://lucide.dev/
- CSS 动画: https://animista.net/

---

## 🎉 开始使用

现在就运行 `streamlit run main.py`，体验全新的 Premium 深色金融风格 UI！

如有问题，请参考各文件中的注释和文档字符串。

---

**版本**: Premium UI v1.0  
**更新日期**: 2025-10-27  
**维护者**: Personal Quant Assistant Team

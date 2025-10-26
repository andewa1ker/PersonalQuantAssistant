# 🚀 Premium UI 启动指南

## 一、快速开始

### 1. 安装依赖
```powershell
# 方式一：安装完整依赖
pip install -r requirements.txt

# 方式二：仅安装新增依赖
pip install streamlit-lottie
```

### 2. 启动应用
```powershell
streamlit run main.py
```

### 3. 访问应用
浏览器会自动打开，或手动访问：
```
http://localhost:8501
```

---

## 二、新增文件说明

升级后，项目新增以下文件：

| 文件 | 说明 |
|------|------|
| `.streamlit/config.toml` | 深色金融主题配置 (已更新) |
| `icons.py` | SVG 图标系统 (40+ 图标) |
| `styles_premium.py` | 全局样式与 Design Tokens |
| `components_premium.py` | Premium 组件库 |
| `lottie_animations.py` | Lottie 动画工具 (可选) |
| `PREMIUM_UI_GUIDE.md` | 完整使用指南 |
| `QUICK_REFERENCE.md` | 快速参考手册 |
| `README_PREMIUM.md` | 本文档 |

---

## 三、核心功能

### 🎨 1. 深色金融主题
- **背景**: 炭黑渐变 (#0B0B0F → #14141A)
- **高光**: 琥珀橙 (#FF6A00 → #FFA54C)
- **圆角**: 18px 卡片 + 玻璃质感
- **动画**: 200-250ms 丝滑过渡

### 📦 2. 组件库
- **账户总览卡**: 余额 + 涨跌徽章 + 操作按钮
- **收益曲线图**: Plotly 平滑曲线 + 面积渐变
- **交易列表**: Hover 动效 + 图标 + 金额正负色
- **KPI 统计卡**: 数字计数动画 + 变化指示
- **环形进度图**: 三色主题 (橙/绿/黄)
- **策略信号表**: 可排序筛选
- **Upcoming 待办**: 日历图标 + 金额提示

### 🎯 3. 图标系统
- **数量**: 40+ Lucide 风格线性图标
- **分类**: 金融、图表、操作、状态、导航
- **特性**: 可自定义尺寸、颜色、响应式

### 🎬 4. 动画系统
- **CSS 动画**: fadeIn, floatIn, pulseGlow, slideInRight
- **Lottie 动画**: 加载、成功、空态、错误 (可选)
- **微交互**: Hover 上浮、Active 回落、发光效果

---

## 四、使用示例

### 示例 1: 基础页面
```python
import streamlit as st
from styles_premium import inject_premium_styles
from components_premium import render_balance_card
from icons import icon, DESIGN_TOKENS

st.set_page_config(page_title="Dashboard", layout="wide")
inject_premium_styles()

st.markdown(f"""
<div style="font-size: 2rem; font-weight: 700;">
    {icon('home', 28, DESIGN_TOKENS['primary_solid'])} 我的页面
</div>
""", unsafe_allow_html=True)

balance = {"total": 50000, "change_pct": 0.12, "change_amount": 5000}
render_balance_card(balance)
```

### 示例 2: 完整 Dashboard
```python
from styles_premium import inject_premium_styles, create_divider
from components_premium import (
    render_balance_card,
    render_profit_chart,
    render_kpi_card,
)

inject_premium_styles()

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

create_divider()

# KPI
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("总资产", "¥50,000", "+12%", "wallet")
```

---

## 五、数据绑定

所有组件使用演示数据，请替换为真实数据：

### 1. 账户余额
```python
# 获取真实数据
portfolio = data_manager.get_portfolio_data()

# 绑定到组件
balance = {
    "total": portfolio['total_value'],
    "change_pct": portfolio['daily_change_pct'],
    "change_amount": portfolio['daily_change_amount']
}

render_balance_card(balance)
```

### 2. 收益曲线
```python
# 获取历史数据
history = data_manager.get_profit_history()

# 绑定到组件
chart_data = {
    "dates": history['dates'].tolist(),
    "values": history['values'].tolist()
}

render_profit_chart(chart_data)
```

### 3. 交易列表
```python
# 获取交易记录
transactions = data_manager.get_recent_transactions(limit=5)

# 转换格式
formatted_txs = []
for tx in transactions:
    formatted_txs.append({
        "title": tx['description'],
        "tag": tx['category'],
        "amount": tx['amount'],
        "time": tx['datetime'].strftime('%Y-%m-%d %H:%M'),
        "icon": "wallet" if tx['amount'] > 0 else "credit_card"
    })

render_transaction_list(formatted_txs)
```

---

## 六、自定义主题

### 修改颜色
编辑 `styles_premium.py`:

```python
DESIGN_TOKENS = {
    'primary_solid': '#YOUR_COLOR',  # 主色
    'bg_primary': '#YOUR_BG',        # 背景
    # ... 其他
}
```

### 修改字体
编辑 `.streamlit/config.toml`:

```toml
[theme]
font = "monospace"  # 或其他字体
```

### 添加新图标
编辑 `icons.py`:

```python
ICONS = {
    'my_icon': '''<svg ...></svg>''',
}
```

---

## 七、故障排除

### 问题 1: 样式不生效
**解决**: 确保调用 `inject_premium_styles()`
```python
from styles_premium import inject_premium_styles
inject_premium_styles()
```

### 问题 2: 图标不显示
**解决**: 检查导入
```python
from icons import icon, icon_html
```

### 问题 3: Lottie 动画报错
**解决**: 安装依赖或禁用
```powershell
pip install streamlit-lottie
```
或者不使用 Lottie（代码已做兼容）

### 问题 4: 数据不显示
**解决**: 检查数据格式
```python
# 正确格式
balance = {
    "total": 50000,          # 数字
    "change_pct": 0.12,      # 小数
    "change_amount": 5000    # 数字
}
```

---

## 八、性能优化

### 1. 缓存数据
```python
@st.cache_data(ttl=300)
def get_data():
    return expensive_operation()
```

### 2. 减少重绘
```python
# 使用 session_state
if 'data' not in st.session_state:
    st.session_state.data = load_data()
```

### 3. 延迟加载
```python
with st.spinner("加载中..."):
    data = load_heavy_data()
```

---

## 九、移动端适配

所有组件已自动适配移动端：
- **≥1280px**: 三列布局
- **1024-1279px**: 两列布局
- **≤768px**: 单列布局

测试方法：
1. 浏览器按 F12 打开开发者工具
2. 切换到设备模拟模式
3. 选择移动设备查看

---

## 十、部署

### Streamlit Cloud
```yaml
# requirements.txt 已包含所有依赖
streamlit>=1.29.0
streamlit-lottie>=0.0.5
# ... 其他依赖
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "main.py"]
```

---

## 十一、更多资源

- **完整指南**: `PREMIUM_UI_GUIDE.md`
- **快速参考**: `QUICK_REFERENCE.md`
- **组件文档**: 查看各 `.py` 文件的 docstring
- **Streamlit 文档**: https://docs.streamlit.io
- **Plotly 文档**: https://plotly.com/python/

---

## 十二、反馈与支持

如有问题或建议，请：
1. 查阅文档中的故障排除部分
2. 检查代码注释和 docstring
3. 参考示例代码

---

## 🎉 开始使用

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run main.py

# 3. 浏览器访问
# http://localhost:8501
```

祝您使用愉快！🚀

---

**版本**: Premium UI v1.0  
**日期**: 2025-10-27  
**团队**: Personal Quant Assistant

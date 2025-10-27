# 🎨 Google Finance UI 完全复刻开发规范

> **目标**：100%还原Google Finance的视觉设计和交互体验
> **网址**：https://www.google.com/finance/
> **分析日期**：2025-10-27

---

## 📐 一、精确配色系统

### 1.1 基础色板（通过浏览器审查元素精确提取）

```css
/* ========== 背景色 ========== */
--gf-bg-primary: #FFFFFF;           /* 主背景 */
--gf-bg-secondary: #F1F3F4;         /* 次级背景、悬停状态 */
--gf-bg-divider: #E8EAED;           /* 分割线 */

/* ========== 文字色 ========== */
--gf-text-primary: #202124;         /* 主文字，87% opacity */
--gf-text-secondary: #5F6368;       /* 次要文字，60% opacity */
--gf-text-disabled: #80868B;        /* 禁用/辅助文字，38% opacity */

/* ========== 功能色 ========== */
--gf-blue: #1A73E8;                 /* 链接、操作按钮 */
--gf-blue-hover: #1765CC;           /* 蓝色悬停 */
--gf-blue-bg: #E8F0FE;              /* 蓝色背景 */

--gf-green: #0F9D58;                /* 涨幅 */
--gf-green-dark: #0D8043;           /* 深绿 */
--gf-green-bg: #E6F4EA;             /* 绿色背景 */

--gf-red: #D93025;                  /* 跌幅 */
--gf-red-dark: #B31412;             /* 深红 */
--gf-red-bg: #FCE8E6;               /* 红色背景 */

/* ========== 边框阴影 ========== */
--gf-border: #DADCE0;               /* 标准边框 */
--gf-border-light: #E8EAED;         /* 浅边框 */
--gf-shadow-sm: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
--gf-shadow-md: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
```

---

## 📏 二、精确尺寸系统

### 2.1 间距系统（4px基准）

```css
/* Material Design 4dp Grid */
--spacing-1: 4px;
--spacing-2: 8px;
--spacing-3: 12px;
--spacing-4: 16px;
--spacing-5: 20px;
--spacing-6: 24px;
--spacing-8: 32px;
--spacing-10: 40px;
--spacing-12: 48px;
```

### 2.2 圆角系统

```css
--radius-none: 0px;
--radius-sm: 4px;      /* 按钮、标签 */
--radius-md: 8px;      /* 卡片、输入框 */
--radius-lg: 16px;     /* 大卡片 */
--radius-full: 9999px; /* 圆形头像、胶囊按钮 */
```

### 2.3 字体系统

```css
/* 字体族 */
font-family: 'Google Sans', 'Roboto', Arial, sans-serif;

/* 字号 */
--font-size-10: 10px;  /* 极小标签 */
--font-size-11: 11px;  /* 小标签 */
--font-size-12: 12px;  /* 辅助信息 */
--font-size-13: 13px;  /* */
--font-size-14: 14px;  /* 正文 */
--font-size-16: 16px;  /* 小标题 */
--font-size-20: 20px;  /* 中标题 */
--font-size-22: 22px;  /* 大标题 */
--font-size-28: 28px;  /* 主标题 */
--font-size-32: 32px;  /* 超大价格 */

/* 字重 */
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* 行高 */
--line-height-tight: 1.2;
--line-height-normal: 1.5;
--line-height-relaxed: 1.75;
```

---

## 🎯 三、核心组件精确复刻

### 3.1 顶部导航栏（Header）

```html
<!-- 高度：64px，固定顶部，白底 -->
<header style="
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #E8EAED;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  padding: 0 24px;
">
  <!-- Logo -->
  <div style="
    font-size: 22px;
    font-weight: 400;
    color: #5F6368;
    margin-right: 48px;
  ">
    Google 财经
  </div>
  
  <!-- 搜索框 -->
  <div style="
    flex: 1;
    max-width: 720px;
  ">
    <input type="text" placeholder="搜索股票、ETF 等" style="
      width: 100%;
      height: 48px;
      background: #F1F3F4;
      border: none;
      border-radius: 24px;
      padding: 0 20px;
      font-size: 14px;
      color: #202124;
    ">
  </div>
  
  <!-- 用户头像 -->
  <div style="
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #1A73E8;
    margin-left: 24px;
  "></div>
</header>
```

**关键参数**：
- 高度：`64px` 固定
- Logo字号：`22px`，`#5F6368`
- 搜索框：`48px`高，`24px`圆角（胶囊状）
- 搜索框背景：`#F1F3F4`
- 边框：`1px solid #E8EAED`

---

### 3.2 价格卡片（Quote Card）

```html
<!-- 
  完全还原Google Finance的股票卡片
  实际尺寸：宽度自适应，最小高度280px
-->
<div class="quote-card" style="
  background: #FFFFFF;
  border: 1px solid #DADCE0;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
">
  <!-- 标题行 -->
  <div style="
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
  ">
    <div>
      <h3 style="
        font-size: 22px;
        font-weight: 400;
        color: #202124;
        margin: 0 0 4px 0;
      ">比特币</h3>
      <div style="
        font-size: 12px;
        color: #5F6368;
      ">BTC · 加密货币</div>
    </div>
    <button style="
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
    ">⋮</button>
  </div>
  
  <!-- 价格和涨跌 -->
  <div style="
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin: 16px 0;
  ">
    <div style="
      font-size: 32px;
      font-weight: 400;
      color: #202124;
      letter-spacing: -0.5px;
    ">$67,234.56</div>
    <div style="
      font-size: 16px;
      font-weight: 400;
      color: #0F9D58;
    ">+1,234.78 (1.87%)</div>
  </div>
  
  <!-- 迷你图表（无边框） -->
  <div style="
    height: 120px;
    margin: 16px -4px;
  ">
    <!-- SVG 图表，无边框，无坐标轴标签 -->
  </div>
  
  <!-- 详细数据（2列网格） -->
  <div style="
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px 24px;
    margin-top: 16px;
  ">
    <div style="display: flex; justify-content: space-between;">
      <span style="color: #5F6368; font-size: 12px;">开盘价</span>
      <span style="color: #202124; font-size: 12px; font-weight: 500;">$66,000.00</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
      <span style="color: #5F6368; font-size: 12px;">最高价</span>
      <span style="color: #202124; font-size: 12px; font-weight: 500;">$67,500.00</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
      <span style="color: #5F6368; font-size: 12px;">前收盘价</span>
      <span style="color: #202124; font-size: 12px; font-weight: 500;">$65,999.78</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
      <span style="color: #5F6368; font-size: 12px;">最低价</span>
      <span style="color: #202124; font-size: 12px; font-weight: 500;">$65,800.00</span>
    </div>
  </div>
</div>
```

**关键参数**：
- 卡片圆角：`8px`
- 内边距：`20px`
- 边框：`1px solid #DADCE0`
- 标题字号：`22px`，字重 `400`
- 价格字号：`32px`，字重 `400`，字间距 `-0.5px`
- 涨跌字号：`16px`
- 详细数据字号：`12px`
- 数据行间距：`12px`

---

### 3.3 图表组件（Chart）

```css
/* Google Finance 图表的精确样式 */
.gf-chart {
  /* 容器 */
  width: 100%;
  height: 400px;
  background: transparent;
  position: relative;
}

.gf-chart-canvas {
  /* 画布 */
  width: 100%;
  height: 100%;
}

.gf-chart-grid {
  /* 网格线 */
  stroke: #F1F3F4;
  stroke-width: 1px;
  stroke-dasharray: 2, 2;
}

.gf-chart-line {
  /* 主折线 */
  stroke: #1A73E8;
  stroke-width: 2px;
  fill: none;
}

.gf-chart-area {
  /* 面积填充 */
  fill: url(#gradient);
  /* 渐变：rgba(26,115,232,0.15) -> rgba(26,115,232,0.0) */
}

.gf-chart-tooltip {
  /* 工具提示 */
  position: absolute;
  background: #FFFFFF;
  border: 1px solid #DADCE0;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
  font-size: 12px;
  pointer-events: none;
}

.gf-chart-timerange {
  /* 时间范围选择器 */
  display: flex;
  gap: 4px;
  margin-top: 16px;
}

.gf-chart-timerange button {
  background: transparent;
  border: none;
  color: #5F6368;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.gf-chart-timerange button:hover {
  background: #F1F3F4;
}

.gf-chart-timerange button.active {
  background: #E8F0FE;
  color: #1A73E8;
}
```

**关键特点**：
- ✅ 无边框，无外框
- ✅ 网格线极淡（`#F1F3F4`）
- ✅ 虚线网格（`2px dash, 2px gap`）
- ✅ 主线：`#1A73E8`，`2px` 宽
- ✅ 渐变填充：从 15% 透明度到 0%
- ✅ 工具提示：白底，圆角 `8px`，Material 阴影
- ✅ 时间按钮：无边框，悬停灰底，选中蓝底

---

### 3.4 数据表格（Table）

```html
<!-- Google Finance 表格精确样式 -->
<table style="
  width: 100%;
  border-collapse: collapse;
  background: #FFFFFF;
">
  <!-- 表头 -->
  <thead style="
    position: sticky;
    top: 64px;
    background: #FFFFFF;
    z-index: 10;
  ">
    <tr style="
      border-bottom: 1px solid #E8EAED;
    ">
      <th style="
        text-align: left;
        font-size: 11px;
        font-weight: 500;
        color: #5F6368;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 12px 16px;
      ">股票代码</th>
      <th style="text-align: left; font-size: 11px; font-weight: 500; color: #5F6368; text-transform: uppercase; padding: 12px 16px;">名称</th>
      <th style="text-align: right; font-size: 11px; font-weight: 500; color: #5F6368; text-transform: uppercase; padding: 12px 16px;">价格</th>
      <th style="text-align: right; font-size: 11px; font-weight: 500; color: #5F6368; text-transform: uppercase; padding: 12px 16px;">涨跌幅</th>
    </tr>
  </thead>
  
  <!-- 表体 -->
  <tbody>
    <tr style="
      border-bottom: 1px solid #F1F3F4;
      transition: background 0.15s;
    " onmouseover="this.style.background='#F1F3F4'" onmouseout="this.style.background='transparent'">
      <td style="
        padding: 16px;
        font-size: 14px;
        color: #202124;
        font-weight: 500;
      ">AAPL</td>
      <td style="padding: 16px; font-size: 14px; color: #5F6368;">Apple Inc.</td>
      <td style="
        padding: 16px;
        text-align: right;
        font-size: 14px;
        color: #202124;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
      ">$175.43</td>
      <td style="
        padding: 16px;
        text-align: right;
      ">
        <span style="
          display: inline-block;
          background: #E6F4EA;
          color: #0D8043;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        ">+1.35%</span>
      </td>
    </tr>
    <!-- 更多行... -->
  </tbody>
</table>
```

**关键参数**：
- 表头：
  - 字号：`11px`
  - 字重：`500`
  - 颜色：`#5F6368`
  - 大写：`text-transform: uppercase`
  - 字间距：`0.8px`
  - 内边距：`12px 16px`
  - 粘性定位：`position: sticky; top: 64px;`
  
- 表体：
  - 行高：`48px`（16px padding * 2 + 14px font + 2px）
  - 字号：`14px`
  - 悬停背景：`#F1F3F4`
  - 边框：`1px solid #F1F3F4`
  - 数字：等宽字体 `tabular-nums`

- 涨跌标签：
  - 背景：涨 `#E6F4EA`，跌 `#FCE8E6`
  - 文字：涨 `#0D8043`，跌 `#B31412`
  - 圆角：`4px`
  - 内边距：`4px 8px`
  - 字号：`12px`

---

### 3.5 按钮系统（Buttons）

```css
/* ========== 主按钮（Primary） ========== */
.gf-btn-primary {
  background: #1A73E8;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
}

.gf-btn-primary:hover {
  background: #1765CC;
  box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
}

.gf-btn-primary:active {
  background: #1557B0;
  box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15);
}

/* ========== 次级按钮（Secondary） ========== */
.gf-btn-secondary {
  background: #FFFFFF;
  color: #1A73E8;
  border: 1px solid #DADCE0;
  border-radius: 4px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.gf-btn-secondary:hover {
  background: #F8F9FA;
  border-color: #DADCE0;
}

/* ========== 文字按钮（Text） ========== */
.gf-btn-text {
  background: transparent;
  color: #1A73E8;
  border: none;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}

.gf-btn-text:hover {
  background: #F1F3F4;
}

/* ========== 图标按钮（Icon） ========== */
.gf-btn-icon {
  background: transparent;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}

.gf-btn-icon:hover {
  background: #F1F3F4;
}
```

---

### 3.6 标签/徽章（Badges）

```css
/* ========== 涨幅标签 ========== */
.gf-badge-up {
  display: inline-block;
  background: #E6F4EA;
  color: #0D8043;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

/* ========== 跌幅标签 ========== */
.gf-badge-down {
  display: inline-block;
  background: #FCE8E6;
  color: #B31412;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

/* ========== 状态标签 ========== */
.gf-badge-status {
  display: inline-block;
  background: #E8F0FE;
  color: #1A73E8;
  padding: 4px 8px;
  border-radius: 12px; /* 胶囊状 */
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

---

## 📱 四、页面布局规范

### 4.1 整体布局结构

```
┌─────────────────────────────────────────────────────────┐
│ [顶部导航栏] 64px 固定顶部                               │
├─────────────────────────────────────────────────────────┤
│ ← 24px →                                       ← 24px → │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 内容区域                                         │   │
│ │ max-width: 1440px                              │   │
│ │ margin: 0 auto                                 │   │
│ │                                                 │   │
│ │ [KPI卡片] [KPI卡片] [KPI卡片] [KPI卡片]        │   │
│ │ ↑ 16px 间距                                     │   │
│ │                                                 │   │
│ │ ┌──────────────────┐ ┌─────────────┐          │   │
│ │ │                  │ │             │          │   │
│ │ │  主图表区        │ │  侧边信息   │          │   │
│ │ │  (2/3 宽度)      │ │  (1/3 宽度) │          │   │
│ │ │                  │ │             │          │   │
│ │ └──────────────────┘ └─────────────┘          │   │
│ │ ↑ 16px 间距                                     │   │
│ │                                                 │   │
│ │ [数据表格]                                      │   │
│ │                                                 │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**关键参数**：
- 顶部导航栏高度：`64px`
- 页面左右内边距：`24px`
- 内容最大宽度：`1440px`
- 卡片间距：`16px`
- 主内容区比例：`2:1` (主图表 vs 侧边栏)

### 4.2 响应式断点

```css
/* 超大屏（Desktop） */
@media (min-width: 1280px) {
  .container { max-width: 1440px; }
  .grid-cols { grid-template-columns: repeat(4, 1fr); }
}

/* 大屏（Laptop） */
@media (min-width: 1024px) and (max-width: 1279px) {
  .container { max-width: 1200px; }
  .grid-cols { grid-template-columns: repeat(3, 1fr); }
}

/* 平板（Tablet） */
@media (min-width: 768px) and (max-width: 1023px) {
  .container { max-width: 100%; padding: 0 16px; }
  .grid-cols { grid-template-columns: repeat(2, 1fr); }
  .sidebar { display: none; } /* 隐藏侧边栏 */
}

/* 手机（Mobile） */
@media (max-width: 767px) {
  .container { padding: 0 12px; }
  .grid-cols { grid-template-columns: 1fr; }
  .header { padding: 0 12px; }
  .search-box { max-width: 100%; }
}
```

---

## 🎬 五、交互动画规范

### 5.1 过渡时长

```css
/* Google Material Design Duration */
--duration-shortest: 75ms;   /* 微小状态变化 */
--duration-shorter: 150ms;   /* 按钮悬停、卡片悬停 */
--duration-short: 200ms;     /* 下拉菜单、工具提示 */
--duration-standard: 300ms;  /* 页面过渡、模态框 */
--duration-long: 400ms;      /* 大型动画 */
```

### 5.2 缓动函数

```css
/* Material Design Easing */
--easing-standard: cubic-bezier(0.4, 0, 0.2, 1);    /* 标准 */
--easing-decelerate: cubic-bezier(0, 0, 0.2, 1);   /* 减速 */
--easing-accelerate: cubic-bezier(0.4, 0, 1, 1);   /* 加速 */
--easing-sharp: cubic-bezier(0.4, 0, 0.6, 1);      /* 锐利 */
```

### 5.3 典型动画示例

```css
/* 卡片悬停 */
.card {
  transition: 
    box-shadow 150ms cubic-bezier(0.4, 0, 0.2, 1),
    transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
  transform: translateY(-2px);
}

/* 按钮点击 */
.button {
  transition: 
    background 150ms cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 150ms cubic-bezier(0.4, 0, 0.2, 1);
}

.button:active {
  transform: translateY(1px);
  box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
}

/* 展开/收起动画 */
.expandable {
  transition: 
    max-height 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 🔍 六、细节还原清单

### 6.1 必须100%还原的细节

- [ ] **颜色**：使用精确的十六进制颜色值
- [ ] **字体**：Roboto/Google Sans + Noto Sans SC
- [ ] **圆角**：4px/8px，不能随意修改
- [ ] **阴影**：Material Design 标准阴影
- [ ] **间距**：严格使用 4px 基准
- [ ] **字号**：12px/14px/16px/22px/32px
- [ ] **行高**：1.2/1.5/1.75
- [ ] **过渡**：150ms 标准时长
- [ ] **边框**：1px solid #DADCE0
- [ ] **悬停态**：#F1F3F4 背景
- [ ] **激活态**：微下沉动画

### 6.2 图表细节

- [ ] 无边框、无外框
- [ ] 网格线：#F1F3F4，虚线
- [ ] 主线颜色：#1A73E8
- [ ] 主线宽度：2px
- [ ] 渐变填充：15% → 0% 透明度
- [ ] 工具提示：白底 + Material 阴影
- [ ] 时间按钮：12px 字号，4px 圆角

### 6.3 表格细节

- [ ] 表头粘性定位
- [ ] 表头大写 + 字间距 0.8px
- [ ] 行高 48px
- [ ] 悬停背景 #F1F3F4
- [ ] 数字右对齐 + tabular-nums
- [ ] 涨跌标签：4px 圆角，4px 8px 内边距

---

## 🚀 七、实施计划

### Phase 1: 设计系统基础（1天）
```
✅ 创建新的 design_system_google.py
✅ 定义精确的颜色变量
✅ 定义字体、间距、圆角系统
✅ 创建 CSS 注入函数
```

### Phase 2: 核心组件（2天）
```
✅ 实现价格卡片组件
✅ 实现图表组件（Plotly配置）
✅ 实现数据表格组件
✅ 实现按钮系统
✅ 实现标签/徽章组件
```

### Phase 3: 页面重构（2-3天）
```
✅ 重构 Home.py（首页）
✅ 重构 1_Dashboard.py
✅ 重构其他6个页面
✅ 统一导航栏
```

### Phase 4: 细节打磨（1天）
```
✅ 调整所有间距为4px基准
✅ 统一所有字号
✅ 添加悬停动画
✅ 测试响应式布局
```

---

## 📸 八、视觉对比检查表

在完成每个组件后，使用以下清单对比：

```
组件：_____________

[ ] 颜色值完全一致
[ ] 字体字号完全一致
[ ] 间距精确匹配（误差<2px）
[ ] 圆角精确匹配
[ ] 阴影效果一致
[ ] 悬停效果一致
[ ] 动画时长一致
[ ] 响应式断点一致
[ ] 细节装饰一致（如箭头、图标等）
[ ] 在不同屏幕尺寸下测试通过
```

---

## 🎯 九、关键差异总结

| 项目 | 当前暗色风格 | Google Finance 白色风格 |
|------|------------|------------------------|
| **主背景** | #0B0B0F | #FFFFFF |
| **卡片背景** | #16161D | #FFFFFF |
| **卡片边框** | rgba(255,255,255,0.06) | #DADCE0 |
| **主文字** | #FFFFFF | #202124 |
| **次要文字** | rgba(255,255,255,0.78) | #5F6368 |
| **强调色** | #FF7A29 橙色 | #1A73E8 蓝色 |
| **圆角** | 18px 大圆角 | 8px 小圆角 |
| **阴影** | 发光效果 | 微妙阴影 |
| **字体** | Inter | Roboto |
| **按钮** | 渐变背景 | 纯色背景 |

---

## ✅ 十、验收标准

**完成条件**：

1. ✅ 打开应用后，与 Google Finance 在视觉上无法区分
2. ✅ 所有颜色值精确匹配（使用取色器验证）
3. ✅ 所有字号、间距精确匹配（使用浏览器开发工具验证）
4. ✅ 悬停、点击动画效果一致
5. ✅ 响应式布局在各种屏幕下表现一致
6. ✅ 无额外装饰或个性化设计

**禁止事项**：

- ❌ 不能添加 Google Finance 没有的装饰
- ❌ 不能修改 Google 的标准颜色
- ❌ 不能使用大于 8px 的卡片圆角（除非特殊说明）
- ❌ 不能使用发光效果或非标准阴影
- ❌ 不能使用渐变按钮（Google 使用纯色）

---

**此文档是实施的唯一标准，所有设计决策必须严格遵循！**


# Premium UI 设计规范

## 🎨 设计原则

### 1. 深色金融风格
- **专业性**: 深色背景营造专业、沉稳的金融氛围
- **对比度**: 橙色高光与深色背景形成强烈对比，突出关键信息
- **可读性**: 精心调配的文本不透明度确保长时间阅读舒适

### 2. 轻量与性能
- **CSS 优先**: 使用 CSS3 实现动画，避免 JS 性能开销
- **缓存策略**: 数据缓存减少重复请求
- **按需加载**: 大型组件延迟渲染

### 3. 信息层级
- **视觉权重**: 关键数据使用大字号 + 橙色高光
- **空间留白**: 适当间距提升阅读体验
- **卡片分组**: 相关信息组合在卡片内

---

## 🎨 颜色体系

### 主色调 (Primary)
```css
/* 橙色渐变 - 主高光 */
--primary-start: #FF6A00;  /* 起始 */
--primary-end: #FFA54C;    /* 结束 */
--primary-solid: #FF7A29;  /* 实色 */

/* 使用场景 */
- 主按钮背景
- 关键数字（正收益）
- 图表曲线
- 图标高光
- 交互焦点
```

### 背景色 (Background)
```css
/* 渐变背景 */
--bg-primary: #0B0B0F;     /* 主背景 */
--bg-secondary: #14141A;   /* 次级背景 */

/* 卡片背景 */
--bg-card: #1E1E26;        /* 默认 */
--bg-card-hover: #23232D;  /* Hover */
--bg-elevated: #2B2B36;    /* 高层级 */

/* 使用场景 */
- 页面背景: primary
- 侧边栏: secondary
- 卡片: card
- 输入框: elevated
```

### 文本色 (Text)
```css
--text-primary: #FFFFFF;               /* 主文本 - 100% */
--text-secondary: rgba(255,255,255,0.78);  /* 次级 - 78% */
--text-tertiary: rgba(255,255,255,0.56);   /* 弱提示 - 56% */
--text-disabled: rgba(255,255,255,0.38);   /* 禁用 - 38% */

/* 使用场景 */
- 标题、金额: primary
- 描述、标签: secondary
- 时间、提示: tertiary
- 禁用按钮: disabled
```

### 功能色 (Functional)
```css
/* 成功 - 绿色 */
--success: #4CAF50;
--success-bg: rgba(76, 175, 80, 0.12);

/* 错误 - 红色 */
--error: #EF5350;
--error-bg: rgba(239, 83, 80, 0.12);

/* 警告 - 橙黄色 */
--warning: #FFA726;
--warning-bg: rgba(255, 167, 38, 0.12);

/* 信息 - 蓝色 */
--info: #42A5F5;
--info-bg: rgba(66, 165, 245, 0.12);

/* 使用场景 */
- 正收益: success
- 负收益: error
- 提醒: warning
- 说明: info
```

### 边框与分割
```css
--border: rgba(255, 255, 255, 0.08);       /* 默认边框 */
--border-hover: rgba(255, 255, 255, 0.16); /* Hover边框 */
--divider: rgba(255, 255, 255, 0.06);      /* 分割线 */
```

---

## 📐 间距系统

### 间距标准
```css
--spacing-xs: 4px;    /* 极小间距 */
--spacing-sm: 8px;    /* 小间距 */
--spacing-md: 16px;   /* 中等间距（默认） */
--spacing-lg: 24px;   /* 大间距 */
--spacing-xl: 32px;   /* 超大间距 */
--spacing-2xl: 48px;  /* 巨大间距 */
```

### 使用建议
- **卡片内边距**: 1.5rem (24px)
- **元素间距**: 1rem (16px)
- **区块间距**: 2rem (32px)
- **页面边距**: 2-3rem (32-48px)

---

## 🔘 圆角系统

```css
--radius-card: 18px;     /* 卡片 */
--radius-button: 12px;   /* 按钮 */
--radius-input: 12px;    /* 输入框 */
--radius-badge: 999px;   /* 徽章（全圆角） */
--radius-small: 8px;     /* 小元素 */
```

---

## 🌈 阴影与发光

### 阴影
```css
/* 卡片阴影 */
--shadow-card: 0 8px 40px rgba(0, 0, 0, 0.45);

/* 高层级阴影 */
--shadow-elevated: 0 16px 60px rgba(0, 0, 0, 0.55);
```

### 发光
```css
/* 橙色发光 - 主按钮 */
--glow-primary: 0 0 24px rgba(255, 140, 64, 0.35);

/* 强发光 - 焦点/激活 */
--glow-strong: 0 0 40px rgba(255, 122, 41, 0.5);
```

---

## ✍️ 字体系统

### 字体族
```css
/* 主字体 */
font-family: -apple-system, BlinkMacSystemFont, 
             "Segoe UI", "Noto Sans SC", 
             "Microsoft YaHei", sans-serif;

/* 等宽字体（数字） */
font-family: "SF Mono", "Consolas", "Monaco", monospace;
```

### 字号标准
```css
/* 标题 */
h1: 2rem (32px)
h2: 1.5rem (24px)
h3: 1.25rem (20px)

/* 正文 */
body: 1rem (16px)
small: 0.875rem (14px)
xs: 0.75rem (12px)

/* 数字 */
kpi-value: 2.5rem (40px)
metric-value: 2rem (32px)
```

### 字重
```css
--font-light: 300;
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* 使用场景 */
- 标题: 700
- KPI数字: 700
- 按钮: 600
- 标签: 500
- 正文: 400
```

---

## 🎬 动画规范

### 时长
```css
--duration-fast: 150ms;    /* 快速 */
--duration-normal: 200ms;  /* 标准 */
--duration-slow: 250ms;    /* 缓慢 */
```

### 缓动函数
```css
/* 丝滑过渡 */
--transition-smooth: cubic-bezier(0.22, 1, 0.36, 1);

/* 标准使用 */
transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
```

### 关键帧动画
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes floatIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 122, 41, 0.3); }
  50% { box-shadow: 0 0 40px rgba(255, 122, 41, 0.6); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

### 微交互
```css
/* 按钮 Hover */
transform: translateY(-2px);
box-shadow: 0 6px 24px rgba(255, 106, 0, 0.4);
transition: 0.25s;

/* 卡片 Hover */
transform: translateY(-3px);
box-shadow: var(--shadow-card), var(--glow-primary);
transition: 0.25s;

/* 列表项 Hover */
background: var(--bg-card-hover);
transform: translateY(-2px);
transition: 0.2s;
```

---

## 📦 组件规范

### 1. Premium 卡片
```css
.premium-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  transition: all 0.25s var(--transition-smooth);
}

.premium-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-hover);
  transform: translateY(-3px);
  box-shadow: var(--shadow-card), var(--glow-primary);
}
```

### 2. 按钮
```css
/* 主按钮 */
.primary-button {
  background: linear-gradient(135deg, #FF6A00, #FFA54C);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(255, 106, 0, 0.3);
}

/* 次按钮 */
.secondary-button {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}
```

### 3. 徽章
```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}
```

### 4. KPI 卡
```css
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: 1.5rem;
  text-align: center;
}

.kpi-value {
  font-size: 2.5rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}
```

---

## 📱 响应式设计

### 断点
```css
/* 手机 */
@media (max-width: 768px) {
  .block-container { padding: 1rem; }
  .premium-card { padding: 1rem; }
}

/* 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  /* 两列布局 */
}

/* 桌面 */
@media (min-width: 1025px) {
  /* 三列布局 */
}
```

### 布局策略
- **移动端**: 单列，上下堆叠
- **平板**: 两列，关键信息优先
- **桌面**: 三列，充分利用空间

---

## ♿ 可访问性

### 对比度
- **主文本**: 21:1 (AAA 级)
- **次级文本**: 7:1 (AA 级)
- **交互元素**: 4.5:1 (AA 级)

### 焦点环
```css
*:focus-visible {
  outline: 2px solid #FFA54C;
  outline-offset: 2px;
}
```

### 语义化
```html
<!-- 使用 aria-label -->
<button aria-label="刷新数据">
  <svg>...</svg>
</button>

<!-- 使用语义标签 -->
<nav>, <main>, <aside>, <article>
```

---

## 🎯 设计检查清单

### 颜色
- [ ] 使用 Design Tokens 中的颜色
- [ ] 对比度符合 AA 标准
- [ ] 功能色使用正确（成功/错误/警告/信息）

### 间距
- [ ] 卡片内边距 1.5rem
- [ ] 元素间距 1rem
- [ ] 区块间距 2rem

### 圆角
- [ ] 卡片 18px
- [ ] 按钮 12px
- [ ] 徽章 999px

### 动画
- [ ] 时长 200-250ms
- [ ] 使用 cubic-bezier(0.22, 1, 0.36, 1)
- [ ] 避免布局抖动（只用 transform/opacity）

### 响应式
- [ ] 移动端测试
- [ ] 平板测试
- [ ] 桌面测试

### 可访问性
- [ ] 焦点环可见
- [ ] 语义化标签
- [ ] 键盘可操作

---

## 📚 参考资源

- **Material Design**: https://material.io/design
- **Apple Human Interface**: https://developer.apple.com/design/
- **Stripe Design**: https://stripe.com/docs/design
- **Ant Design**: https://ant.design/

---

**制定者**: Personal Quant Assistant Design Team  
**版本**: v1.0  
**更新**: 2025-10-27

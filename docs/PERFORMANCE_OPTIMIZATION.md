# 性能优化 - 缓存系统使用指南

## 问题说明
用户反馈: "加载数据太慢,每次切换界面都要差不多等一分钟"

**根本原因**:
- 每次页面切换都重新调用API获取数据
- 没有缓存机制,导致重复请求
- 外部API有速率限制和超时问题

## 解决方案

### 1. 缓存系统架构

#### 三层缓存策略:
1. **Streamlit @st.cache_data**: 跨会话缓存(TTL控制)
2. **Session State**: 单会话缓存(页面切换间共享)
3. **预加载**: 后台静默加载常用数据

#### 缓存层级:
```
实时数据: TTL=5分钟
历史数据: TTL=30分钟  
市场概览: TTL=10分钟
交易信号: TTL=10分钟
```

### 2. 使用方法

#### 在页面模块中使用缓存:

```python
# 旧方法 (慢 - 每次都调用API)
from data_fetcher.data_manager import DataManager

def show_my_page(config, data_manager):
    # 这会直接调用API,没有缓存
    data = data_manager.get_asset_data('etf', '513500', 'realtime')
```

```python
# 新方法 (快 - 使用缓存)
from utils.cache_helper import get_realtime_with_cache, get_history_with_cache

def show_my_page(config, data_manager):
    # 带缓存获取实时数据(5分钟TTL)
    data = get_realtime_with_cache(data_manager, 'etf', '513500')
    
    # 带缓存获取历史数据(30分钟TTL)
    history = get_history_with_cache(data_manager, 'etf', '513500', '1y')
```

#### 批量获取数据:

```python
from utils.cache_helper import batch_get_realtime, batch_get_history

def show_portfolio_page(config, data_manager):
    # 定义资产列表
    assets = [
        ('etf', '513500'),
        ('etf', '159915'),
        ('crypto', 'bitcoin'),
    ]
    
    # 批量获取实时数据(带进度显示和缓存)
    realtime_data = batch_get_realtime(data_manager, assets)
    
    # 批量获取历史数据(带进度条)
    history_data = batch_get_history(data_manager, assets, period='1y')
```

#### 获取市场概览:

```python
from utils.cache_helper import get_market_overview_cache

def show_dashboard(config, data_manager):
    # 获取缓存的市场数据(包含crypto/etf/stocks)
    market_data = get_market_overview_cache(data_manager)
    
    # 使用数据
    crypto_data = market_data['crypto']
    etf_data = market_data['etf']
```

#### 获取交易信号:

```python
from utils.cache_helper import get_signals_with_cache

def show_signals_page(config, data_manager, signal_gen):
    # 定义监控资产
    assets = [
        ('etf', '513500'),
        ('crypto', 'bitcoin'),
    ]
    
    # 获取缓存的信号(10分钟TTL)
    signals = get_signals_with_cache(signal_gen, data_manager, assets)
```

### 3. 缓存管理

#### 自动管理:
- 缓存已集成到`main.py`的`main()`函数中
- 侧边栏自动显示缓存管理工具
- 用户可以手动刷新或清除缓存

#### 手动控制:
```python
from utils.cache_helper import clear_cache, get_cache_info

# 清除特定缓存
clear_cache('etf_513500_realtime')

# 清除所有缓存
clear_cache()

# 获取缓存信息
info = get_cache_info()
print(f"缓存项数: {info['total_items']}")
```

### 4. 性能监控

缓存系统自动记录性能指标:
- 平均加载时间
- 最慢操作
- 缓存命中率

在侧边栏可以看到实时性能数据。

### 5. 需要更新的模块

#### 优先级高 (数据密集型页面):
- ✅ `main.py` - 已集成缓存系统
- ⚠️ `overview_enhanced.py` - 需要更新
- ⚠️ `analysis_enhanced.py` - 需要更新  
- ⚠️ `dashboard_page.py` - 需要更新
- ⚠️ `signals_enhanced.py` - 需要更新

#### 优先级中:
- `risk_enhanced.py` - 部分使用mock数据
- `export_module.py` - 导出时才加载

#### 优先级低:
- `strategy_viz.py` - 主要用mock数据
- `settings_enhanced.py` - 无数据获取

### 6. 更新步骤

对于每个需要更新的模块:

1. **添加导入**:
```python
from utils.cache_helper import (
    get_realtime_with_cache,
    get_history_with_cache,
    batch_get_realtime,
    batch_get_history
)
```

2. **替换数据获取调用**:
```python
# 旧: data = data_manager.get_asset_data('etf', code, 'realtime')
# 新: data = get_realtime_with_cache(data_manager, 'etf', code)
```

3. **测试验证**:
- 第一次加载应该较慢(从API获取)
- 后续加载应该瞬间完成(从缓存读取)
- 缓存过期后自动刷新

### 7. 预期效果

**优化前**:
- 页面切换: ~60秒
- 大量API超时和429错误
- 用户体验差

**优化后**:
- 首次加载: ~10-15秒(预加载)
- 后续切换: <2秒(缓存)
- API调用减少90%+
- 用户体验显著提升

### 8. 注意事项

1. **TTL设置**:
   - 实时数据: 5分钟足够(价格变化不大)
   - 历史数据: 30分钟(日K线不常变)
   - 根据实际需求调整

2. **缓存失效**:
   - 用户可以点击"刷新数据"强制更新
   - 切换资产代码会自动获取新数据
   - 缓存键包含资产标识,不会混淆

3. **内存管理**:
   - Session State只保留当前会话数据
   - 缓存自动过期清理
   - 不会无限增长

4. **错误处理**:
   - API失败时不会崩溃
   - 显示友好警告信息
   - 可以使用旧缓存数据

## 快速检查清单

更新模块时检查:
- [ ] 导入了cache_helper函数
- [ ] 所有`get_asset_data`调用改为`get_xxx_with_cache`
- [ ] 批量操作使用`batch_get_xxx`
- [ ] 测试首次加载和缓存加载
- [ ] 验证缓存过期后自动刷新
- [ ] 检查侧边栏显示缓存状态

## 示例: 完整页面更新

```python
# 文件: overview_enhanced.py
import streamlit as st
from utils.cache_helper import (
    get_realtime_with_cache,
    batch_get_realtime,
    get_market_overview_cache
)

def show_overview_enhanced(config, data_manager):
    st.header("📈 总览面板")
    
    # 使用缓存的市场数据
    market_data = get_market_overview_cache(data_manager)
    
    # 显示加密货币
    st.subheader("💰 加密货币")
    for crypto in market_data['crypto']:
        st.metric(
            crypto.get('name', 'Unknown'),
            f"${crypto.get('price', 0):,.2f}",
            f"{crypto.get('change_24h', 0):.2f}%"
        )
    
    # 显示ETF
    st.subheader("📊 ETF")
    etf_codes = ['513500', '159915', '512690']
    etf_data = batch_get_realtime(data_manager, [('etf', code) for code in etf_codes])
    
    for code, data in etf_data.items():
        if data:
            st.metric(
                data.get('name', code),
                f"¥{data.get('price', 0):.2f}",
                f"{data.get('change', 0):.2f}%"
            )
```

## 故障排查

### 问题: 缓存不生效
- 检查TTL设置是否合理
- 确认使用了正确的缓存函数
- 查看Streamlit缓存状态(`st.cache_data.clear()`)

### 问题: 数据不更新
- 用户点击"刷新数据"按钮
- 检查缓存TTL是否过长
- 确认资产代码正确(缓存键包含代码)

### 问题: 内存占用高
- 减少缓存TTL
- 限制预加载资产数量
- 定期清理旧缓存

## 更多信息

查看源码:
- `src/utils/cache_helper.py` - 缓存辅助函数
- `main.py` - 缓存系统集成
- 各个页面模块 - 实际使用示例

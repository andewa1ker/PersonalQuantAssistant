# Stage 5: 风险管理模块 - 完成报告

## 📋 概述

Stage 5实现了全方位的风险管理系统，包括风险度量、仓位管理、止损止盈和实时监控告警功能。

**完成时间**: 2025年10月27日  
**模块数量**: 5个核心模块 + 1个Web界面  
**代码行数**: ~2,500行  
**测试覆盖**: 14个单元测试，100%通过率

---

## 🎯 核心功能

### 1. 风险度量计算 (risk_measurement.py)

**功能**: 计算全面的风险指标

**关键指标**:
- **VaR (Value at Risk)**: 95%置信水平的最大损失
- **CVaR (条件VaR)**: 极端损失的期望值
- **最大回撤**: 历史最大峰值到谷底的跌幅
- **夏普比率**: 风险调整后收益 = (收益 - 无风险利率) / 波动率
- **索提诺比率**: 仅考虑下行波动的风险调整收益
- **卡玛比率**: 收益 / 最大回撤
- **胜率**: 正收益天数占比
- **盈亏比**: 平均盈利 / 平均亏损

**风险等级评估**:
```python
风险评分 = (
    回撤权重 * 回撤得分 +
    波动率权重 * 波动率得分 +
    VaR权重 * VaR得分 +
    夏普权重 * 夏普得分
)

风险等级:
- low (低风险): 评分 < 30
- medium (中风险): 30 <= 评分 < 50
- high (高风险): 50 <= 评分 < 70
- extreme (极端风险): 评分 >= 70
```

**使用示例**:
```python
from risk_management import RiskMeasurement

risk_measurement = RiskMeasurement({
    'confidence_level': 0.95,
    'risk_free_rate': 0.03
})

metrics = risk_measurement.calculate_metrics(data, asset_symbol='513500')
print(f"波动率: {metrics.volatility:.2%}")
print(f"夏普比率: {metrics.sharpe_ratio:.2f}")
print(f"风险等级: {metrics.risk_level}")
```

---

### 2. 仓位管理 (position_manager.py)

**功能**: 基于风险收益特征智能计算建议仓位

**四种计算方法**:

#### a) 凯利公式 (Kelly Criterion)
```
f* = (p * b - q) / b
其中:
- p = 胜率
- q = 1 - p (败率)
- b = 盈亏比
```

**分数凯利**: `实际仓位 = f* × kelly_fraction (默认0.25)`

#### b) 波动率调整
```
建议仓位 = 目标波动率 / 实际波动率
```
- 目标波动率默认: 15%
- 低波动资产 → 增加仓位
- 高波动资产 → 降低仓位

#### c) 固定风险
```
建议仓位 = 单笔风险 / 止损幅度
```
- 单笔风险默认: 2% (每次交易最多亏损总资金的2%)
- 止损幅度: 5%
- 建议仓位 = 2% / 5% = 40%

#### d) 综合方法
```
综合仓位 = 
    0.4 × 凯利仓位 +
    0.4 × 波动率仓位 +
    0.2 × 固定风险仓位
```

**使用示例**:
```python
from risk_management import PositionManager

position_manager = PositionManager()

# 凯利公式
position = position_manager.calculate_position_kelly(
    win_rate=0.55,
    profit_loss_ratio=2.0
)

# 综合方法
position = position_manager.calculate_position_综合(
    data,
    win_rate=0.55,
    profit_loss_ratio=2.0
)

print(f"建议仓位: {position.recommended_position:.1%}")
print(f"风险等级: {position.risk_level}")
```

---

### 3. 止损止盈管理 (stop_loss_manager.py)

**功能**: 动态计算止损止盈点位

**三种方法**:

#### a) 固定百分比
```python
做多:
  止损价 = 当前价 × (1 - 止损%)
  止盈价 = 当前价 × (1 + 止盈%)

做空:
  止损价 = 当前价 × (1 + 止损%)
  止盈价 = 当前价 × (1 - 止盈%)
```

#### b) ATR动态止损
```
ATR (Average True Range) = MA(True Range, period=14)

True Range = max(
    high - low,
    |high - prev_close|,
    |low - prev_close|
)

做多:
  止损价 = 当前价 - ATR × 止损倍数 (默认2.0)
  止盈价 = 当前价 + ATR × 止盈倍数 (默认3.0)
```

#### c) 支撑阻力
```python
支撑位 = min(recent_lows[-lookback:])  # 最近低点
阻力位 = max(recent_highs[-lookback:])  # 最近高点

做多:
  止损价 = 支撑位 × 0.98  # 支撑位下方2%
  止盈价 = 阻力位 × 1.02  # 阻力位上方2%
```

**使用示例**:
```python
from risk_management import StopLossManager

stop_loss_manager = StopLossManager()

# 固定止损
target = stop_loss_manager.calculate_fixed_stop_loss(
    current_price=100.0,
    direction='long',
    stop_loss_pct=0.05,
    take_profit_pct=0.15
)

# ATR止损
target = stop_loss_manager.calculate_atr_stop_loss(
    data,
    direction='long'
)

print(f"止损价: {target.stop_loss_price:.2f}")
print(f"止盈价: {target.take_profit_price:.2f}")
print(f"风险收益比: 1:{target.take_profit_pct/target.stop_loss_pct:.2f}")
```

---

### 4. 风险监控告警 (risk_monitor.py)

**功能**: 实时监控风险指标并生成告警

**监控指标阈值** (可配置):
```python
默认配置 = {
    'max_drawdown_threshold': 0.20,    # 最大回撤20%
    'volatility_threshold': 0.40,      # 波动率40%
    'var_threshold': 0.05,             # VaR 5%
    'min_sharpe_threshold': 0.5,       # 最低夏普0.5
    'max_position_threshold': 0.30,    # 单品种最大仓位30%
    'min_diversification': 3           # 至少3个资产
}
```

**告警类型**:
- `info`: 提示信息 (严重度1-2)
- `warning`: 警告 (严重度3)
- `critical`: 严重告警 (严重度4-5)

**告警场景**:
1. **回撤告警**: 最大回撤超过阈值
2. **波动率告警**: 波动率超过阈值
3. **VaR告警**: VaR超过阈值
4. **夏普告警**: 夏普比率低于阈值
5. **风险等级告警**: 整体风险评分过高
6. **集中度告警**: 单品种仓位过重
7. **分散度告警**: 资产数量不足

**使用示例**:
```python
from risk_management import RiskMonitor

risk_monitor = RiskMonitor({
    'max_drawdown_threshold': 0.20,
    'volatility_threshold': 0.40
})

# 监控单个资产
metrics, alerts = risk_monitor.monitor_asset_risk(
    data,
    asset_symbol='513500',
    current_position=0.20
)

# 监控投资组合
portfolio_alerts = risk_monitor.monitor_portfolio_risk(
    portfolio_positions={
        '513500': 0.30,
        'BTC': 0.25,
        'ETH': 0.25
    }
)

for alert in alerts:
    print(f"{alert.alert_type.upper()}: {alert.message}")
    print(f"建议: {alert.suggested_action}")
```

---

### 5. Web界面 (risk_page.py)

**功能**: 可视化风险管理工具

**四大功能模块**:

#### 📊 风险指标分析
- 输入资产代码和分析周期
- 展示全面风险指标
- 风险等级可视化
- 详细数据统计

#### 💼 仓位管理
- 选择计算方法 (凯利/波动率/固定/综合)
- 输入胜率、盈亏比等参数
- 显示建议仓位和金额
- 风险等级评估

#### 🛡️ 止损止盈
- 选择止损方法 (固定/ATR/支撑阻力)
- 输入交易方向
- 计算止损止盈价格
- 展示风险收益比

#### 🚨 风险监控告警
- 实时风险监控
- 告警列表展示
- 关键指标概览
- 告警详情和建议操作

**访问方式**:
```
主菜单 → ⚠️ 风险管理 → 选择功能标签
```

---

## 📊 测试结果

### 单元测试统计
```
运行测试: 14
成功: 14
失败: 0
错误: 0
成功率: 100%
```

### 测试覆盖

**风险度量测试** (3个):
- ✅ test_calculate_metrics: 基础指标计算
- ✅ test_high_volatility: 高波动场景
- ✅ test_downtrend: 下跌趋势

**仓位管理测试** (4个):
- ✅ test_kelly_position: 凯利公式
- ✅ test_volatility_position: 波动率调整
- ✅ test_fixed_risk_position: 固定风险
- ✅ test_综合_position: 综合方法

**止损止盈测试** (4个):
- ✅ test_fixed_stop_loss_long: 固定止损做多
- ✅ test_fixed_stop_loss_short: 固定止损做空
- ✅ test_atr_stop_loss: ATR动态止损
- ✅ test_support_resistance: 支撑阻力止损

**风险监控测试** (3个):
- ✅ test_monitor_asset_risk: 资产监控
- ✅ test_high_risk_alerts: 高风险告警
- ✅ test_portfolio_monitoring: 组合监控

### 测试输出示例
```
风险指标计算完成: TEST 
  收益: -7.32% 
  波动: 30.75% 
  夏普: -0.34 
  最大回撤: 31.50%

凯利仓位计算: KELLY_TEST 
  建议仓位: 8.1% 
  胜率: 55.0% 
  盈亏比: 2.00

ATR止损计算: ATR_TEST 
  ATR: 2.6161 
  止损: 88.40 
  止盈: 101.48

风险监控: HIGH_RISK 
  风险等级: extreme 
  告警数: 5
```

---

## 🗂️ 文件结构

```
PersonalQuantAssistant/
├── src/
│   └── risk_management/
│       ├── __init__.py                    # 模块导出
│       ├── base_risk.py                   # 基础框架 (302行)
│       ├── risk_measurement.py            # 风险度量 (421行)
│       ├── position_manager.py            # 仓位管理 (467行)
│       ├── stop_loss_manager.py           # 止损止盈 (365行)
│       └── risk_monitor.py                # 风险监控 (348行)
├── risk_page.py                           # Web界面 (602行)
├── test_stage5.py                         # 单元测试 (464行)
├── STAGE5_COMPLETE.md                     # 本文档
└── main.py                                # 主应用 (已集成)
```

---

## 🔧 配置说明

### 风险度量配置
```python
risk_measurement_config = {
    'confidence_level': 0.95,         # VaR/CVaR置信水平
    'risk_free_rate': 0.03,           # 无风险利率 (年化)
    'min_data_points': 30             # 最小数据点数
}
```

### 仓位管理配置
```python
position_config = {
    'kelly_fraction': 0.25,           # 分数凯利系数
    'target_volatility': 0.15,        # 目标波动率
    'risk_per_trade': 0.02,           # 单笔风险比例
    'max_position': 0.30,             # 最大仓位
    'min_position': 0.05              # 最小仓位
}
```

### 止损止盈配置
```python
stop_loss_config = {
    'default_stop_loss_pct': 0.05,    # 默认止损5%
    'default_take_profit_pct': 0.15,  # 默认止盈15%
    'risk_reward_ratio': 3.0,         # 风险收益比
    'atr_period': 14,                 # ATR周期
    'atr_stop_multiplier': 2.0,       # ATR止损倍数
    'atr_profit_multiplier': 3.0,     # ATR止盈倍数
    'support_resistance_lookback': 20 # 支撑阻力回溯期
}
```

### 风险监控配置
```python
risk_monitor_config = {
    'max_drawdown_threshold': 0.20,   # 最大回撤阈值
    'volatility_threshold': 0.40,     # 波动率阈值
    'var_threshold': 0.05,            # VaR阈值
    'min_sharpe_threshold': 0.5,      # 最低夏普阈值
    'max_position_threshold': 0.30,   # 单品种最大仓位
    'min_diversification': 3          # 最少资产数量
}
```

---

## 📚 使用最佳实践

### 1. 风险度量
- 建议至少3个月历史数据 (约60个交易日)
- 定期重新计算 (每周或每月)
- 不同市场环境需要调整无风险利率

### 2. 仓位管理
- 新手建议使用分数凯利 (0.25)
- 高波动资产降低仓位
- 综合方法最稳健，适合大多数场景

### 3. 止损止盈
- 固定百分比适合稳定市场
- ATR方法适合波动市场
- 支撑阻力适合技术分析

### 4. 风险监控
- 设置合理阈值，避免过度告警
- 严重告警需立即处理
- 定期回顾历史告警

---

## 🚀 后续优化方向

### 功能增强
- [ ] 多资产组合VaR计算
- [ ] 压力测试和情景分析
- [ ] 动态调整仓位 (根据市场状态)
- [ ] 机器学习预测风险

### 性能优化
- [ ] 异步计算大规模组合
- [ ] 缓存历史计算结果
- [ ] 增量更新风险指标

### 用户体验
- [ ] 风险报告PDF导出
- [ ] 历史告警记录
- [ ] 风险指标趋势图
- [ ] 移动端推送告警

---

## 📝 变更日志

### v1.0.0 (2025-10-27)
- ✅ 实现完整风险管理框架
- ✅ 风险度量 (12+指标)
- ✅ 仓位管理 (4种方法)
- ✅ 止损止盈 (3种方法)
- ✅ 风险监控告警系统
- ✅ Web界面集成
- ✅ 14个单元测试 (100%通过)

---

## 🎓 参考资料

### 学术文献
1. Kelly, J. L. (1956). "A New Interpretation of Information Rate"
2. Sharpe, W. F. (1966). "Mutual Fund Performance"
3. Sortino, F. A. (1994). "Downside Risk"
4. Artzner et al. (1999). "Coherent Measures of Risk"

### 实践指南
- 风险管理最佳实践 (CFA Institute)
- 量化投资风险控制 (国内券商研报)
- ATR指标应用 (Wilder, 1978)

---

## 👥 贡献者

**开发**: GitHub Copilot  
**测试**: 自动化单元测试  
**文档**: 完整中文文档

---

## 📞 支持

如有问题或建议，请查阅:
- 代码注释 (详细的函数文档)
- 单元测试 (使用示例)
- 配置文件 (config.yaml)

---

**Stage 5 完成标志**: ✅ 风险管理系统全面上线

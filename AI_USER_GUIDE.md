# AI智能投资系统 - 用户使用指南

## 📚 目录

1. [系统概览](#系统概览)
2. [AI预测模块](#ai预测模块)
3. [因子挖掘](#因子挖掘)
4. [情感分析](#情感分析)
5. [深度学习](#深度学习)
6. [使用示例](#使用示例)

---

## 系统概览

PersonalQuantAssistant 已升级为完整的AI量化投资系统，集成了以下核心功能：

### 🎯 核心AI模块

| 模块 | 功能 | 文件位置 |
|------|------|----------|
| **ML预测器** | 收益率/方向/波动率预测 | `src/ai/ml_predictor.py` |
| **因子挖掘** | 遗传编程自动发现Alpha因子 | `src/ai/factor_mining.py` |
| **深度学习** | LSTM/GRU/Transformer时序预测 | `src/ai/dl_framework.py` |
| **情感分析** | 中文金融文本情感识别 | `src/ai/nlp_sentiment.py` |
| **回测增强** | 真实市场约束模拟 | `src/strategy/event_driven_backtest.py` |

---

## AI预测模块

### 1. 收益率预测 (ReturnPredictor)

**功能**: 预测未来N天的收益率

#### 使用代码
```python
from src.ai.ml_predictor import ReturnPredictor
import pandas as pd

# 1. 加载数据（OHLCV格式）
data = pd.read_csv("stock_data.csv", parse_dates=['date'])
data.set_index('date', inplace=True)

# 2. 创建预测器
predictor = ReturnPredictor(
    prediction_days=5,      # 预测5天后收益率
    model_type='random_forest',  # 可选: gbdt, ridge, lasso
    use_ensemble=True       # 启用集成学习
)

# 3. 训练模型
predictor.train(data)

# 4. 预测
prediction = predictor.predict(data)
print(f"预测收益率: {prediction.value:.2%}")
print(f"预测信心: {prediction.confidence:.2%}")
```

#### 特征工程
系统自动创建 **31个技术指标特征**:
- 移动平均线 (MA): 5/10/20/60日
- RSI, MACD, 布林带, ATR
- 成交量指标: OBV, 量价比
- 波动率: 5/10/20日
- 滞后特征: 1/2/3/5/10期

### 2. 方向预测 (DirectionPredictor)

**功能**: 预测涨跌方向（上涨=1，下跌=-1）

```python
from src.ai.ml_predictor import DirectionPredictor

predictor = DirectionPredictor(
    prediction_days=5,
    model_type='random_forest'
)
predictor.train(data)

prediction = predictor.predict(data)
print(f"预测方向: {'上涨' if prediction.value > 0 else '下跌'}")
print(f"预测信心: {prediction.confidence:.2%}")
```

### 3. 批量预测（用于回测）

```python
# 获取历史预测序列
predictions = predictor.predict_batch(data, start_date='2024-01-01')

# 转换为DataFrame
pred_df = pd.DataFrame([
    {'date': pred.timestamp, 'value': pred.value, 'confidence': pred.confidence}
    for pred in predictions
])
```

---

## 因子挖掘

### 遗传编程自动发现Alpha因子

**原理**: 使用遗传算法自动生成和优化因子表达式，通过IC（信息系数）评估因子有效性。

#### 使用代码
```python
from src.ai.factor_mining import FactorMiner

# 1. 创建挖掘器
miner = FactorMiner()

# 2. 准备数据（需包含returns列）
data['returns'] = data['close'].pct_change()

# 3. 配置挖掘参数
config = {
    'population_size': 50,      # 种群大小
    'generations': 10,           # 进化代数
    'tournament_size': 5,        # 锦标赛选择大小
    'crossover_prob': 0.8,       # 交叉概率
    'mutation_prob': 0.2,        # 变异概率
    'min_ic': 0.02               # 最小IC阈值
}

# 4. 开始挖掘
results = miner.mine_factors(data, config)

# 5. 查看结果
best_factor = results['best_factor']
print(f"最佳因子表达式: {best_factor['expression']}")
print(f"IC: {best_factor['ic']:.4f}")
print(f"IC_IR: {best_factor['ic_ir']:.4f}")

# 6. 使用因子预测
factor_values = best_factor['values']
```

#### IC评价标准
- **IC > 0.03**: 优秀因子
- **IC > 0.02**: 良好因子
- **IC > 0.01**: 可用因子
- **IC_IR > 1.0**: 稳定性好

#### 因子表达式示例
```
最佳因子: ((high sub low) mul rank(volume))
解释: (最高价 - 最低价) * volume排名
IC: 0.0523, IC_IR: 2.15
```

---

## 情感分析

### 中文金融文本情感分析

**功能**: 分析财经新闻、公告、社交媒体文本的情感倾向。

#### 1. 单文本分析

```python
from src.ai.nlp_sentiment import ChineseSentimentAnalyzer

# 创建分析器
analyzer = ChineseSentimentAnalyzer()

# 分析文本
text = "公司业绩大幅增长，市场前景看好，投资价值凸显"
result = analyzer.analyze(text)

print(f"情感得分: {result['sentiment_score']:.2f}")  # -1到1
print(f"情感标签: {result['sentiment_label']}")      # positive/negative/neutral
print(f"正向词: {result['positive_words']}")
print(f"负向词: {result['negative_words']}")
```

#### 2. 批量新闻分析

```python
from src.ai.nlp_sentiment import FinancialSentimentAggregator

# 创建聚合器
aggregator = FinancialSentimentAggregator()

# 准备新闻数据
news_list = [
    {'date': '2024-10-01', 'text': '公司业绩超预期...'},
    {'date': '2024-10-02', 'text': '市场担忧经济放缓...'},
    {'date': '2024-10-03', 'text': '政策利好出台...'}
]

# 批量分析
results = aggregator.analyze_batch(news_list)

# 查看结果
for r in results:
    print(f"{r['date']}: 情感={r['sentiment']:.2f}, 标签={r['label']}")
```

#### 3. 情感指数（0-100）

```python
# 计算每日情感指数
sentiment_index = aggregator.calculate_sentiment_index(news_list)

for idx in sentiment_index:
    print(f"{idx['date']}: 指数={idx['index']:.1f}, 信心={idx['confidence']:.2%}")

# 指数解读
# 70-100: 极度乐观（强烈买入信号）
# 60-70:  乐观（买入信号）
# 40-60:  中性
# 30-40:  悲观（卖出信号）
# 0-30:   极度悲观（强烈卖出信号）
```

#### 4. 生成交易信号

```python
signals = aggregator.generate_sentiment_signal(news_list)

for signal in signals:
    print(f"{signal['date']}: {signal['signal']} (强度={signal['strength']:.2%})")
    print(f"  原因: {signal['reason']}")

# 信号类型:
# 🔴 强烈卖出 (sentiment < 30 或 突然下降)
# 🟡 卖出 (sentiment 30-40)
# ⚪ 持有 (sentiment 40-60)
# 🟢 买入 (sentiment 60-70)
# 🔵 强烈买入 (sentiment > 70 或 突然上升)
```

---

## 深度学习

### LSTM/GRU/Transformer 时序预测

**依赖**: 需要安装 PyTorch
```bash
pip install torch
```

#### 1. LSTM预测

```python
from src.ai.dl_framework import DLFramework

# 创建框架
framework = DLFramework(
    model_type='lstm',
    input_size=5,           # 输入特征数（OHLCV）
    hidden_size=64,         # 隐藏层大小
    num_layers=2,           # LSTM层数
    dropout=0.2,            # Dropout比例
    learning_rate=0.001
)

# 准备序列数据
X, y = framework.prepare_sequence_data(
    data[['open', 'high', 'low', 'close', 'volume']],
    target=data['close'].shift(-1),  # 预测下一个收盘价
    sequence_length=20               # 使用20天历史
)

# 训练模型
history = framework.train(
    X, y,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    early_stopping=True,    # 启用早停
    patience=10
)

# 预测
predictions = framework.predict(X[-1:])
print(f"预测下一个收盘价: {predictions[0][0]:.2f}")
```

#### 2. Transformer预测

```python
# 创建Transformer模型
framework = DLFramework(
    model_type='transformer',
    input_size=5,
    hidden_size=128,
    num_layers=3,
    num_heads=4,            # 多头注意力头数
    dropout=0.1
)

# 训练和预测流程相同
framework.train(X, y, epochs=50)
predictions = framework.predict(X[-1:])
```

#### 3. 快速LSTM预测（一行代码）

```python
from src.ai.dl_framework import quick_lstm_predict

predictions = quick_lstm_predict(
    data=data[['close']],
    epochs=30,
    sequence_length=20
)
```

---

## 使用示例

### 完整投资决策流程

```python
import pandas as pd
from src.ai.ml_predictor import ReturnPredictor, DirectionPredictor
from src.ai.factor_mining import FactorMiner
from src.ai.nlp_sentiment import FinancialSentimentAggregator

# ========== 1. 加载数据 ==========
stock_data = pd.read_csv("stock.csv", parse_dates=['date'])
stock_data.set_index('date', inplace=True)
stock_data['returns'] = stock_data['close'].pct_change()

news_data = pd.read_csv("news.csv", parse_dates=['date'])

# ========== 2. ML预测 ==========
return_pred = ReturnPredictor(prediction_days=5, use_ensemble=True)
return_pred.train(stock_data)
ml_prediction = return_pred.predict(stock_data)

print(f"\n📊 ML预测:")
print(f"  预测收益率: {ml_prediction.value:.2%}")
print(f"  预测信心: {ml_prediction.confidence:.2%}")

# ========== 3. 因子挖掘 ==========
miner = FactorMiner()
factors = miner.mine_factors(stock_data, {
    'population_size': 50,
    'generations': 10,
    'min_ic': 0.02
})

print(f"\n🔍 因子挖掘:")
print(f"  发现 {len(factors['factors'])} 个有效因子")
print(f"  最佳IC: {factors['best_factor']['ic']:.4f}")

# ========== 4. 情感分析 ==========
aggregator = FinancialSentimentAggregator()
sentiment = aggregator.calculate_sentiment_index(news_data.to_dict('records'))

latest_sentiment = sentiment[-1] if sentiment else {'index': 50}
print(f"\n💬 情感分析:")
print(f"  情感指数: {latest_sentiment['index']:.1f}/100")

# ========== 5. 综合决策 ==========
ml_score = ml_prediction.value * ml_prediction.confidence
factor_score = factors['best_factor']['ic'] if factors['factors'] else 0
sentiment_score = (latest_sentiment['index'] - 50) / 50  # 归一化到-1到1

# 加权综合（可调整权重）
final_score = (
    0.4 * ml_score +
    0.3 * sentiment_score +
    0.3 * factor_score
)

print(f"\n🎯 综合投资决策:")
print(f"  ML贡献: {ml_score:.3f} (权重40%)")
print(f"  情感贡献: {sentiment_score:.3f} (权重30%)")
print(f"  因子贡献: {factor_score:.3f} (权重30%)")
print(f"  最终得分: {final_score:.3f}")

# 生成建议
if final_score > 0.2:
    decision = "🔵 强烈买入"
elif final_score > 0.05:
    decision = "🟢 买入"
elif final_score > -0.05:
    decision = "➖ 中性"
elif final_score > -0.2:
    decision = "🟡 卖出"
else:
    decision = "🔴 强烈卖出"

print(f"  投资建议: {decision}")
```

---

## UI界面使用

### 启动系统
```bash
cd PersonalQuantAssistant
streamlit run main.py
```

### AI预测页面

1. **左侧菜单** → 选择 "🤖 AI智能预测"

2. **四个标签页**:
   - **收益率预测**: 输入股票代码，选择预测天数，查看预测收益率和信心度
   - **方向预测**: 预测涨跌方向，显示准确率和混淆矩阵
   - **因子挖掘**: 配置遗传算法参数，查看因子进化过程和最佳因子
   - **模型对比**: 对比Random Forest、GBDT、Ridge等模型性能

### 情感分析页面

1. **左侧菜单** → 选择 "💬 情感分析"

2. **四个标签页**:
   - **单文本分析**: 输入文本，查看情感得分和关键词
   - **批量新闻分析**: 上传CSV文件，批量分析新闻情感
   - **情感指数**: 查看每日情感指数时间序列
   - **交易信号**: 基于情感变化生成买卖信号

---

## 数据格式要求

### 股票数据格式
```csv
date,open,high,low,close,volume
2024-01-01,100.5,102.3,99.8,101.2,1500000
2024-01-02,101.5,103.1,101.0,102.5,1800000
...
```

### 新闻数据格式
```csv
date,text
2024-01-01,公司发布Q4财报，营收同比增长25%...
2024-01-02,市场担忧美联储加息...
...
```

---

## 性能优化建议

### 1. ML模型选择
- **Random Forest**: 平衡性能和速度，默认推荐
- **GBDT**: 精度最高，训练时间较长
- **Ridge/Lasso**: 速度最快，适合快速迭代

### 2. 因子挖掘参数
- **小数据集** (<1000条): population=30, generations=5
- **中等数据集** (1000-5000): population=50, generations=10
- **大数据集** (>5000): population=100, generations=20

### 3. 深度学习参数
- **LSTM**: 适合长期依赖，sequence_length=20-60
- **GRU**: 速度更快，性能接近LSTM
- **Transformer**: 最先进，但需要更多数据（>5000条）

---

## 常见问题

### Q1: 预测准确率不高怎么办？
**A**: 
1. 增加训练数据量（建议>500条）
2. 调整prediction_days（推荐3-10天）
3. 启用use_ensemble=True
4. 尝试不同的model_type

### Q2: 因子挖掘没有发现有效因子？
**A**:
1. 降低min_ic阈值（如0.01）
2. 增加generations和population_size
3. 检查数据质量，确保returns列正确

### Q3: 情感分析全是中性？
**A**:
1. 安装jieba: `pip install jieba`
2. 检查文本是否为中文
3. 确保文本长度足够（>10字）

### Q4: 深度学习报错？
**A**:
1. 安装PyTorch: `pip install torch`
2. 检查数据长度 > sequence_length
3. 确保GPU驱动正确（如使用GPU）

---

## 技术支持

### 日志查看
所有日志保存在 `logs/` 目录：
- `quant_system.log`: 系统运行日志
- 包含模型训练进度、错误信息、性能指标

### 模型保存
训练的模型自动保存在 `data/models/` 目录：
- `return_main_YYYYMMDD_HHMMSS.pkl`: 收益率预测主模型
- `direction_main_YYYYMMDD_HHMMSS.pkl`: 方向预测主模型

### 重新训练模型
```python
# 删除旧模型，重新训练
import os
import shutil
shutil.rmtree('data/models/ml_predictor', ignore_errors=True)

# 重新训练
predictor = ReturnPredictor()
predictor.train(data)
```

---

## 更新日志

### Phase 4 (2025-10-27)
- ✅ 新增 ML预测器（收益率、方向、波动率）
- ✅ 新增 因子挖掘（遗传编程）
- ✅ 新增 深度学习框架（LSTM/GRU/Transformer）
- ✅ 新增 NLP情感分析（中文支持）
- ✅ 新增 AI预测UI页面
- ✅ 新增 情感分析UI页面
- ✅ 完善 集成测试覆盖

---

## 下一步扩展方向

### 计划中功能
1. **强化学习**: 自动策略优化
2. **集成更多数据源**: 财务数据、宏观数据
3. **实时预警**: Webhook通知、邮件告警
4. **多资产支持**: 期货、期权、加密货币
5. **组合优化**: 马科维茨、Black-Litterman

---

**祝您投资顺利！** 📈✨

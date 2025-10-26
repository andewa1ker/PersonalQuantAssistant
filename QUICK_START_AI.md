# 🚀 AI功能快速启动指南

## 5分钟快速上手

### 1️⃣ 启动系统
```bash
cd PersonalQuantAssistant
streamlit run main.py
```

浏览器自动打开 `http://localhost:8501`

---

## 🤖 AI预测功能

### 左侧菜单选择 "🤖 AI智能预测"

#### 📈 收益率预测（推荐首次使用）
1. **输入股票代码**: 如 `000001`（平安银行）
2. **选择预测天数**: 推荐 `5天`
3. **点击"开始预测"**

**查看结果**:
- 📊 预测收益率: `+2.5%` （正值=上涨）
- 🎯 预测信心: `85%` （越高越可靠）
- 📉 特征重要性柱状图（哪些指标最关键）
- 📈 历史预测回测曲线

#### 🎯 方向预测
1. 选择"方向预测"标签页
2. 输入股票代码，点击预测
3. 查看涨跌方向（🔺上涨 / 🔻下跌）
4. 准确率和混淆矩阵

#### 🔍 因子挖掘（高级功能）
1. 选择"因子挖掘"标签页
2. 调整参数（新手使用默认值）:
   - 种群大小: `30`
   - 进化代数: `5`
3. 点击"开始挖掘"
4. 等待1-2分钟，查看发现的Alpha因子

**示例输出**:
```
最佳因子: ((high - low) * rank(volume))
IC: 0.0523
IC_IR: 2.15
```

---

## 💬 情感分析功能

### 左侧菜单选择 "💬 情感分析"

#### 📝 单文本分析（最简单）
1. 在文本框输入新闻:
   ```
   公司业绩大幅增长，市场前景看好，投资价值凸显
   ```
2. 点击"分析"
3. 查看:
   - 🎨 情感仪表盘（-1到+1）
   - ✅ 正向关键词: 增长、看好、价值
   - ❌ 负向关键词: 无

#### 📰 批量新闻分析
1. 准备CSV文件（格式见下）:
   ```csv
   date,text
   2024-10-01,公司发布Q4财报超预期
   2024-10-02,市场担忧美联储加息
   ```
2. 上传文件，查看批量结果
3. 情感分布直方图

#### 📊 情感指数（交易信号）
1. 上传多日新闻CSV
2. 查看情感指数时间序列（0-100）
3. 获取交易信号:
   - 🔵 **强烈买入** (指数>70)
   - 🟢 **买入** (指数60-70)
   - ⚪ **持有** (指数40-60)
   - 🟡 **卖出** (指数30-40)
   - 🔴 **强烈卖出** (指数<30)

---

## 💡 实战案例

### 案例1: 短期收益预测
**目标**: 预测某股票未来5天收益率

```python
# 在Jupyter或Python脚本中运行
from src.ai.ml_predictor import ReturnPredictor
import pandas as pd

# 加载数据
data = pd.read_csv("stock_data.csv", parse_dates=['date'])
data.set_index('date', inplace=True)

# 创建预测器
predictor = ReturnPredictor(prediction_days=5, use_ensemble=True)

# 训练
predictor.train(data)

# 预测
result = predictor.predict(data)
print(f"预测收益率: {result.value:.2%}")
print(f"预测信心: {result.confidence:.2%}")
```

**预期输出**:
```
预测收益率: +2.34%
预测信心: 87.50%
```

---

### 案例2: 发现Alpha因子

**目标**: 自动挖掘有效的交易因子

```python
from src.ai.factor_mining import FactorMiner

# 创建挖掘器
miner = FactorMiner()

# 挖掘配置（小规模测试）
config = {
    'population_size': 30,
    'generations': 5,
    'min_ic': 0.02
}

# 开始挖掘
results = miner.mine_factors(data, config)

# 查看结果
print(f"发现 {len(results['factors'])} 个有效因子")
print(f"最佳IC: {results['best_factor']['ic']:.4f}")
```

**预期输出**:
```
发现 3 个有效因子
最佳IC: 0.0523
最佳因子: ((high sub low) mul rank(volume))
```

---

### 案例3: 情感驱动交易

**目标**: 根据新闻情感生成交易信号

```python
from src.ai.nlp_sentiment import FinancialSentimentAggregator

# 创建聚合器
aggregator = FinancialSentimentAggregator()

# 准备新闻数据
news = [
    {'date': '2024-10-01', 'text': '公司业绩超预期，利好不断'},
    {'date': '2024-10-02', 'text': '市场恐慌情绪蔓延，风险加大'},
    {'date': '2024-10-03', 'text': '政策利好出台，行业迎来春天'}
]

# 计算情感指数
sentiment_index = aggregator.calculate_sentiment_index(news)

# 生成交易信号
signals = aggregator.generate_sentiment_signal(news)

for signal in signals:
    print(f"{signal['date']}: {signal['signal']} (强度={signal['strength']:.1%})")
```

**预期输出**:
```
2024-10-01: 🟢 买入 (强度=75.0%)
2024-10-02: 🟡 卖出 (强度=35.0%)
2024-10-03: 🔵 强烈买入 (强度=95.0%)
```

---

### 案例4: 综合决策系统

**目标**: 融合ML预测、因子挖掘、情感分析的完整决策

```python
from src.ai.ml_predictor import ReturnPredictor
from src.ai.factor_mining import FactorMiner
from src.ai.nlp_sentiment import FinancialSentimentAggregator

# ========== 1. ML预测 ==========
ml_pred = ReturnPredictor(prediction_days=5, use_ensemble=True)
ml_pred.train(stock_data)
ml_result = ml_pred.predict(stock_data)

ml_score = ml_result.value * ml_result.confidence
print(f"ML得分: {ml_score:.3f}")

# ========== 2. 因子挖掘 ==========
miner = FactorMiner()
factors = miner.mine_factors(stock_data, {'population_size': 30, 'generations': 5})

factor_score = factors['best_factor']['ic'] if factors['factors'] else 0
print(f"因子得分: {factor_score:.3f}")

# ========== 3. 情感分析 ==========
aggregator = FinancialSentimentAggregator()
sentiment = aggregator.calculate_sentiment_index(news_data)

sentiment_score = (sentiment[-1]['index'] - 50) / 50  # 归一化
print(f"情感得分: {sentiment_score:.3f}")

# ========== 4. 综合决策 ==========
final_score = 0.4 * ml_score + 0.3 * sentiment_score + 0.3 * factor_score

print(f"\n综合得分: {final_score:.3f}")

if final_score > 0.2:
    print("投资建议: 🔵 强烈买入")
elif final_score > 0.05:
    print("投资建议: 🟢 买入")
elif final_score > -0.05:
    print("投资建议: ➖ 中性")
elif final_score > -0.2:
    print("投资建议: 🟡 卖出")
else:
    print("投资建议: 🔴 强烈卖出")
```

**预期输出**:
```
ML得分: 0.020
因子得分: 0.052
情感得分: 0.400

综合得分: 0.149
投资建议: 🟢 买入
```

---

## 📊 数据格式要求

### 股票数据 (CSV格式)
```csv
date,open,high,low,close,volume
2024-01-01,100.5,102.3,99.8,101.2,1500000
2024-01-02,101.5,103.1,101.0,102.5,1800000
2024-01-03,102.0,104.5,101.5,104.0,2000000
```

**必需列**:
- `date`: 日期（YYYY-MM-DD）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量

### 新闻数据 (CSV格式)
```csv
date,text
2024-01-01,公司发布Q4财报，营收同比增长25%，超市场预期
2024-01-02,行业分析师下调评级，担忧竞争加剧影响利润率
2024-01-03,监管部门发布利好政策，板块估值有望修复
```

**必需列**:
- `date`: 日期（YYYY-MM-DD）
- `text`: 新闻文本（中文）

---

## ⚡ 性能优化建议

### 小数据集 (<500条)
```python
# 因子挖掘
config = {
    'population_size': 20,
    'generations': 3,
    'min_ic': 0.01
}

# ML预测
predictor = ReturnPredictor(
    model_type='ridge',  # 最快
    use_ensemble=False
)
```

### 中等数据集 (500-2000条)
```python
# 因子挖掘
config = {
    'population_size': 30,
    'generations': 5,
    'min_ic': 0.02
}

# ML预测
predictor = ReturnPredictor(
    model_type='random_forest',  # 默认
    use_ensemble=True
)
```

### 大数据集 (>2000条)
```python
# 因子挖掘
config = {
    'population_size': 50,
    'generations': 10,
    'min_ic': 0.02
}

# ML预测
predictor = ReturnPredictor(
    model_type='gbdt',  # 最精确
    use_ensemble=True
)
```

---

## 🔧 常见问题解决

### Q1: 运行报错 "模块未找到"
```bash
# 解决方案: 安装依赖
pip install -r requirements.txt
```

### Q2: 预测信心度很低 (<50%)
**原因**: 数据不足或市场噪声大  
**解决**:
1. 增加训练数据量（建议>500条）
2. 调整`prediction_days`（推荐3-7天）
3. 启用`use_ensemble=True`

### Q3: 因子挖掘没有发现有效因子
**原因**: IC阈值过高或数据质量差  
**解决**:
1. 降低`min_ic`（如0.01）
2. 增加`generations`（如10-20）
3. 检查数据完整性（无缺失值）

### Q4: 情感分析全是中性
**原因**: jieba未安装或文本太短  
**解决**:
```bash
pip install jieba
```
或确保文本长度>10字

### Q5: UI加载很慢
**原因**: 大数据集特征工程耗时  
**解决**:
1. 减少历史数据量（如只用最近1年）
2. 关闭不必要的技术指标
3. 使用`model_type='ridge'`（最快）

---

## 📈 进阶功能

### 深度学习（需安装PyTorch）
```bash
pip install torch
```

```python
from src.ai.dl_framework import DLFramework

# 创建LSTM模型
framework = DLFramework(
    model_type='lstm',
    input_size=5,
    hidden_size=64,
    num_layers=2
)

# 准备序列数据
X, y = framework.prepare_sequence_data(
    data[['open', 'high', 'low', 'close', 'volume']],
    target=data['close'].shift(-1),
    sequence_length=20
)

# 训练
framework.train(X, y, epochs=50)

# 预测
predictions = framework.predict(X[-1:])
```

---

## 🎯 最佳实践

1. **数据准备**:
   - 至少500条历史数据
   - 无缺失值
   - 日期连续

2. **模型选择**:
   - 快速测试: `ridge`
   - 日常使用: `random_forest`
   - 追求精度: `gbdt` + `use_ensemble=True`

3. **因子挖掘**:
   - 小规模探索: 30种群 × 5代
   - 生产环境: 50种群 × 10代
   - 定期重新挖掘（每月）

4. **情感分析**:
   - 多源新闻（至少3个渠道）
   - 每日更新
   - 结合技术指标

5. **风险控制**:
   - 预测信心<60%时谨慎交易
   - 综合得分>0.2才强烈买入
   - 设置止损（如-5%）

---

## 📞 技术支持

### 查看日志
```bash
# Windows
type logs\quant_system.log | more

# Linux/Mac
tail -f logs/quant_system.log
```

### 重新训练模型
```python
import shutil
shutil.rmtree('data/models/ml_predictor', ignore_errors=True)

# 重新训练
predictor = ReturnPredictor()
predictor.train(data)
```

### 运行测试
```bash
python tests/test_integration.py
```

---

## 🚀 下一步学习

1. 阅读完整文档: `AI_USER_GUIDE.md`
2. 查看项目完成度: `PROJECT_COMPLETION_REPORT.md`
3. 探索源码: `src/ai/` 目录
4. 自定义策略: 继承`BaseStrategy`类

---

**祝您使用愉快！** 📈✨

如有问题，请查看日志或运行测试诊断问题。

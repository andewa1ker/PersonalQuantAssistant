# PersonalQuantAssistant 📊

> 个人AI量化金融分析师 - 智能投资决策助手

一个专为个人投资者设计的量化分析系统,支持A股ETF、加密货币、美股等多资产类别的数据获取、技术分析、策略回测和风险管理。

---

## 📋 项目状态

**完整的项目状态、路线图和版本历史请查看** → [PROJECT_STATUS.md](PROJECT_STATUS.md)

这是唯一维护的项目状态文档,包含:
- ✅ 当前功能完成度 (75%)
- 🗺️ 未来发展路线图
- 📝 版本更新历史
- ⚠️ 已知限制
- 🔧 技术栈详情

---

## ✨ 核心特性

### 🎯 多资产支持
- **513500（标普500 ETF）** - A股市场标普500指数ETF
- **加密货币** - BTC、ETH等主流数字货币
- **美股** - AAPL、TSLA等美国股票（可扩展）

### 📊 技术分析
- 趋势指标：MA、EMA、MACD
- 动量指标：RSI、Stochastic、CCI
- 波动率指标：Bollinger Bands、ATR
- 成交量指标：OBV、Volume MA

### 🎲 智能策略
- **ETF估值策略** - 基于PE/PB历史分位数
- **趋势跟踪** - 双均线 + MACD信号
- **智能定投** - 基于波动率的动态定投
- **加密货币策略** - 恐惧贪婪指数 + 动量反转
- **资产再平衡** - 自动化投资组合管理

### ⚠️ 风险管理
- 最大回撤监控
- 动态止损止盈
- 仓位风险控制
- 实时警报系统

### 🌐 Web界面
- 基于Streamlit的友好界面
- 实时数据监控
- 交互式图表
- 策略信号展示

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows / macOS / Linux

### 安装步骤

1. **克隆项目**
```bash
cd Desktop/Kris/PersonalQuantAssistant
```

2. **创建虚拟环境（推荐）**
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# 如果遇到权限问题，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
# 复制模板文件
cp config/api_keys.yaml.template config/api_keys.yaml

# 编辑 config/api_keys.yaml，填入你的API密钥
```

5. **运行应用**
```bash
streamlit run main.py
```

应用将在浏览器中自动打开 `http://localhost:8501`

## 📁 项目结构

```
PersonalQuantAssistant/
├── config/                     # 配置文件
│   ├── config.yaml            # 主配置文件
│   ├── api_keys.yaml          # API密钥（需自行创建）
│   └── api_keys.yaml.template # API密钥模板
├── data/                       # 数据存储
│   ├── market_data/           # 市场数据
│   ├── portfolio/             # 持仓数据
│   ├── cache/                 # 缓存数据
│   └── logs/                  # 日志文件
├── src/                        # 源代码
│   ├── data_fetcher/          # 数据获取模块
│   │   ├── stock_data.py     # 股票/ETF数据
│   │   ├── crypto_data.py    # 加密货币数据
│   │   └── data_manager.py   # 统一数据管理
│   ├── analysis/              # 分析引擎
│   │   ├── technical_analyzer.py  # 技术分析
│   │   └── market_status.py      # 市场状态判断
│   ├── strategy/              # 策略模块
│   │   ├── etf_strategy.py   # ETF策略
│   │   ├── crypto_strategy.py # 加密货币策略
│   │   ├── portfolio_strategy.py # 组合策略
│   │   └── position_manager.py   # 仓位管理
│   ├── risk_management/       # 风险管理
│   │   ├── risk_calculator.py    # 风险计算
│   │   ├── alert_system.py       # 警报系统
│   │   └── stop_loss.py         # 止损机制
│   └── utils/                 # 工具函数
│       ├── config_loader.py  # 配置加载
│       ├── logger.py         # 日志管理
│       ├── visualization.py  # 图表工具
│       └── report_generator.py # 报告生成
├── tests/                     # 测试文件
├── main.py                    # Streamlit主程序
├── requirements.txt           # Python依赖
└── README.md                  # 项目文档
```

## ⚙️ 配置说明

### 主配置文件 (config/config.yaml)

主配置文件包含所有系统设置，包括：

- **资产配置** - 启用/禁用特定资产，设置更新频率
- **技术分析参数** - 指标周期、阈值等
- **策略参数** - 各种策略的具体配置
- **风险管理** - 止损止盈、仓位限制等
- **警报规则** - 触发条件和通知方式

关键配置项：

```yaml
assets:
  etf_513500:
    enabled: true              # 是否启用
    position_limit: 0.5        # 最大仓位50%
    
  crypto:
    enabled: true
    symbols: ["bitcoin", "ethereum"]
    position_limit: 0.3

strategy:
  etf_513500:
    trend_following:
      ma_short: 20            # 短期均线
      ma_long: 60             # 长期均线
```

### API密钥配置 (config/api_keys.yaml)

配置各数据源的API密钥：

```yaml
tushare:
  token: "your_tushare_token"

coingecko:
  api_key: null  # 免费版无需密钥

telegram:
  bot_token: "your_bot_token"
  chat_id: "your_chat_id"
```

**⚠️ 安全提示：**
- 不要将包含真实密钥的文件上传到Git
- 定期更换API密钥
- 使用只读权限的API密钥

## 🎓 使用指南

### 1. 数据获取

系统支持多种数据源：

- **AKShare** - 免费的A股、ETF数据（无需API密钥）
- **Tushare** - 专业金融数据（需注册获取token）
- **CoinGecko** - 免费加密货币数据
- **yfinance** - 免费美股数据

### 2. 技术分析

在"品种分析"页面：
- 查看K线图和价格走势
- 查看各种技术指标
- 分析买卖信号

### 3. 策略信号

在"策略信号"页面：
- 查看当前所有品种的交易信号
- 了解信号强度和理由
- 获取操作建议

### 4. 风险管理

在"风险管理"页面：
- 监控投资组合风险指标
- 查看风险警报
- 设置止损位置

### 5. 系统设置

在"设置"页面：
- 调整策略参数
- 修改风险限制
- 配置通知方式

## 🔌 API获取指南

### Tushare（推荐用于A股数据）

1. 访问 https://tushare.pro/register
2. 注册账户
3. 获取token
4. 填入 `config/api_keys.yaml`

积分规则：
- 注册即有120积分
- 签到、分享可获得更多积分
- 积分越高，可获取的数据越多

### CoinGecko（加密货币数据）

免费版无需API密钥，直接使用。

Pro版：
1. 访问 https://www.coingecko.com/
2. 注册Pro账户
3. 获取API密钥

### Telegram通知（可选）

1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 创建机器人
3. 获取bot token
4. 获取你的chat_id（可通过 @userinfobot）

## 📈 开发路线图

### 第一阶段 ✅（当前）
- [x] 项目架构搭建
- [x] 配置系统
- [x] Web界面框架

### 第二阶段 🚧（进行中）
- [ ] 数据获取模块
- [ ] 数据缓存机制
- [ ] 数据库设计

### 第三阶段
- [ ] 技术分析引擎
- [ ] 指标计算优化
- [ ] 信号生成逻辑

### 第四阶段
- [ ] 策略模块实现
- [ ] 回测引擎
- [ ] 参数优化

### 第五阶段
- [ ] 风险管理系统
- [ ] 警报通知
- [ ] 自动化任务

### 第六阶段
- [ ] 完整Web界面
- [ ] 数据可视化
- [ ] 报告生成

### 第七阶段
- [ ] Docker部署
- [ ] 性能优化
- [ ] 文档完善

## 🛠️ 技术栈

- **前端** - Streamlit
- **数据处理** - Pandas, NumPy
- **技术分析** - pandas-ta, ta-lib
- **可视化** - Plotly, Matplotlib
- **数据源** - AKShare, yfinance, CoinGecko
- **任务调度** - APScheduler
- **日志** - Loguru
- **配置** - PyYAML, Pydantic

## 📝 注意事项

1. **数据延迟** - 免费API存在数据延迟，不适合高频交易
2. **API限制** - 注意各数据源的调用频率限制
3. **历史数据** - 部分数据源的历史数据有限
4. **仅供参考** - 本系统提供的分析和建议仅供参考，投资有风险

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交Issue
- 发送邮件

---

**⚠️ 风险提示：本系统仅用于学习和研究目的，不构成投资建议。投资有风险，入市需谨慎。**

**Made with ❤️ for Personal Investors**

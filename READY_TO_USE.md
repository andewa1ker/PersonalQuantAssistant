# PersonalQuantAssistant - 个人AI量化金融分析师

## ✅ 系统状态

**最后修复**: 2025-10-27  
**核心功能测试**: ✅ 100% 通过  
**应用状态**: ✅ 可正常运行

---

## 🚀 快速启动

### 方法1: 使用启动脚本 (推荐)
```powershell
.\start.ps1
```

### 方法2: 使用命令行
```powershell
streamlit run Home.py
```

### 方法3: 双击启动
双击 `启动应用.ps1` 文件

---

## 📊 核心功能

### ✅ 已实现并可用

#### 1. 数据获取 (90%)
- ✅ 多源加密货币数据 (CoinGecko + 缓存)
- ✅ 多源ETF数据 (Tushare + 新浪 + 东财)
- ✅ 智能降级和重试机制
- ✅ SQLite 本地缓存

#### 2. 技术分析 (100%)
- ✅ MA, EMA, MACD
- ✅ RSI, KDJ, 布林带
- ✅ ATR, OBV
- ✅ 综合信号生成

#### 3. 趋势分析 (100%)
- ✅ 趋势识别 (上升/下降/震荡)
- ✅ 支撑位/阻力位识别
- ✅ ADX 趋势强度
- ✅ 背离检测

#### 4. 波动率分析 (100%)
- ✅ 历史波动率
- ✅ Parkinson 波动率
- ✅ 布林带挤压检测
- ✅ 风险指标 (回撤、夏普)

#### 5. 回测系统 (85%)
- ✅ 高仿真回测 (滑点、佣金、印花税)
- ✅ 订单管理系统
- ✅ 持仓管理
- ✅ 绩效统计

#### 6. 风险管理 (85%)
- ✅ 风险监控
- ✅ 风险指标计算
- ✅ 告警系统

#### 7. AI功能 (70%)
- ✅ AI助手 (DeepSeek)
- ✅ 机器学习预测
- ✅ 因子挖掘 (遗传编程)
- ⚠️ 深度学习 (需安装PyTorch)

#### 8. UI界面 (90%)
- ✅ 主控面板
- ✅ 策略信号中心
- ✅ 投资策略中心
- ✅ 风险管理中心
- ✅ 系统设置
- ✅ 数据导出

---

## 🧪 测试

运行核心功能测试:
```powershell
python test_core.py
```

**预期结果**:
```
测试通过率: 100%
- 配置加载: ✅
- 数据管理器: ✅
- 信号生成器: ✅
- 回测引擎: ✅
- 风险监控: ✅
- AI助手: ✅
```

---

## ⚙️ 配置

### API密钥配置 (可选)

编辑 `config/api_keys.yaml`:
```yaml
deepseek:
  api_key: "your-api-key-here"

tushare:
  token: "your-tushare-token"
```

### 应用配置

编辑 `config/config.yaml`:
```yaml
app:
  name: Personal Quant Assistant
  version: 1.0.0
  cache_ttl: 300

assets:
  crypto:
    enabled: true
    symbols: [bitcoin, ethereum, binancecoin]
```

---

## 📖 使用指南

### 1. 查看市场概览
访问主页查看核心指标和市场数据

### 2. 获取交易信号
进入"策略信号中心"查看实时信号

### 3. 配置策略
在"投资策略中心"创建和管理策略

### 4. 风险监控
在"风险管理中心"查看风险指标

### 5. 系统设置
在"系统设置"中配置参数和API密钥

---

## ⚠️ 重要说明

### 当前功能范围
- ✅ **量化研究和回测**
- ✅ **交易信号生成**
- ✅ **风险分析和监控**
- ✅ **学习和研究使用**
- ❌ **实盘自动交易** (未实现)

### 免责声明
本系统仅用于研究和学习目的，不构成投资建议。
投资有风险，入市需谨慎。

---

## 🐛 问题排查

### Streamlit 不启动
```powershell
# 检查端口占用
netstat -ano | findstr :8501

# 杀死占用进程
taskkill /PID <进程ID> /F

# 重新启动
streamlit run Home.py
```

### 数据获取失败
- 检查网络连接
- 系统会自动使用缓存数据
- 缓存有效期: 5分钟

### 测试失败
```powershell
# 重新安装依赖
pip install -r requirements.txt

# 清理缓存
rd /s /q __pycache__
rd /s /q src\__pycache__
```

---

## 📞 技术支持

查看详细文档:
- `CODE_FIX_REPORT.md` - 修复报告
- `ARCHITECTURE.md` - 架构设计
- `DEVELOPMENT_GUIDE.md` - 开发指南

---

## 📝 更新日志

### v1.0.0 (2025-10-27)
- ✅ 修复main.py代码混乱问题
- ✅ 修复数据管理器重复定义
- ✅ 修复配置加载器Unicode问题
- ✅ 创建核心功能测试脚本
- ✅ 所有核心功能测试通过

---

**版本**: v1.0.0  
**最后更新**: 2025-10-27  
**状态**: ✅ 生产就绪

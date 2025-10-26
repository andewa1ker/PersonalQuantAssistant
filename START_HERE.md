# 🚀 立即开始使用

## 快速启动 (3步)

### 步骤1: 安装依赖（首次使用）

```powershell
cd c:\Users\andewa1ker\Desktop\Kris\PersonalQuantAssistant
pip install streamlit pandas numpy akshare requests plotly pyyaml pathlib
```

### 步骤2: 启动应用

```powershell
streamlit run main.py
```

### 步骤3: 打开浏览器

应用会自动打开浏览器，或手动访问：
```
http://localhost:8501
```

---

## 📊 功能说明

### 📈 总览面板
- **513500 ETF**: 实时价格和涨跌幅
- **BTC/ETH**: 加密货币价格
- **恐惧贪婪指数**: 市场情绪
- **详细数据表**: 完整市场信息

### 🔍 品种分析  
- **ETF分析**: K线图、历史数据、估值指标
- **加密货币**: 价格走势、历史数据

### 其他功能
- 🎯 策略信号 (开发中)
- ⚠️ 风险管理 (开发中)
- ⚙️ 系统设置

---

## ⚡ 快捷命令

```powershell
# 完整测试
.\test_run.ps1

# 快速启动
.\start.ps1

# 手动启动
streamlit run main.py

# 指定端口
streamlit run main.py --server.port 8502
```

---

## 🔧 配置文件

### 主配置
`config/config.yaml` - 所有系统参数

### API密钥
`config/api_keys.yaml` - 已配置以下服务：
- ✅ Tushare (A股数据)
- ✅ Binance (加密货币)
- ✅ Alpha Vantage (美股)
- ✅ Telegram (通知)
- ✅ DeepSeek (AI分析)

---

## 📝 注意事项

### 网络要求
- 需要互联网连接
- 首次加载可能较慢(下载数据)
- 某些API可能需要翻墙

### 数据更新
- ETF数据: 实时(有延迟)
- 加密货币: 实时
- 恐惧贪婪指数: 每小时更新

### 缓存
- 数据会缓存1-5分钟
- 点击"🔄 刷新数据"清除缓存
- 缓存文件位于 `data/cache/`

---

## ❓ 常见问题

### Q: 数据显示"获取中..."
**A**: 等待几秒或检查网络连接

### Q: 出现连接错误
**A**: 可能是网络问题或API限制，稍后重试

### Q: K线图不显示
**A**: 确保安装了plotly: `pip install plotly`

### Q: 如何更换数据源
**A**: 编辑 `config/config.yaml` 中的 `data_source` 参数

---

## 🎯 下一步

1. ✅ **第一阶段**: 项目架构 - 已完成
2. ✅ **第二阶段**: 数据获取 - 已完成  
3. 🔜 **第三阶段**: 技术分析 - 即将开始
4. 🔜 **第四阶段**: 投资策略
5. 🔜 **第五阶段**: 风险管理
6. 🔜 **第六阶段**: 界面完善
7. 🔜 **第七阶段**: 部署优化

**当前进度: 28.6%** (2/7 完成)

---

## 📚 更多文档

- `README.md` - 完整项目文档
- `QUICKSTART.md` - 快速开始指南  
- `PROJECT_STATUS.md` - 项目状态追踪
- `STAGE2_COMPLETE.md` - 第二阶段总结
- `DEVELOPMENT_GUIDE.md` - 开发规范

---

## 💡 使用建议

1. **首次使用**: 先在总览面板查看数据
2. **深入分析**: 切换到品种分析页面
3. **数据刷新**: 使用刷新按钮获取最新数据
4. **自定义**: 修改 `config/config.yaml` 调整参数

---

**开始你的量化投资之旅！** 📈💰

有问题？查看文档或运行测试脚本。

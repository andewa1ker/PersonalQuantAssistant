# 快速开始指南

## 🎯 5分钟快速启动

### 步骤1：安装Python环境

确保已安装Python 3.8或更高版本：

```powershell
python --version
```

### 步骤2：创建虚拟环境

```powershell
# 进入项目目录
cd PersonalQuantAssistant

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows PowerShell）
.\venv\Scripts\Activate.ps1

# 如果遇到权限错误，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 步骤3：安装依赖

```powershell
pip install -r requirements.txt
```

**注意：** ta-lib安装可能失败，如果失败可以跳过，系统会使用pandas-ta作为替代。

Windows用户可以从这里下载预编译的whl文件：
https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### 步骤4：配置API密钥（可选）

```powershell
# 复制模板
copy config\api_keys.yaml.template config\api_keys.yaml

# 使用记事本或VS Code编辑
notepad config\api_keys.yaml
```

最基础的配置（使用免费数据源，无需API密钥）：
```yaml
akshare:
  api_key: null

coingecko:
  api_key: null
```

### 步骤5：运行应用

```powershell
streamlit run main.py
```

浏览器会自动打开 http://localhost:8501

## 📚 详细配置说明

### 配置文件位置

- `config/config.yaml` - 主配置文件
- `config/api_keys.yaml` - API密钥文件（需自行创建）

### 启用/禁用资产

编辑 `config/config.yaml`：

```yaml
assets:
  etf_513500:
    enabled: true    # 改为 false 可禁用
    
  crypto:
    enabled: true
    symbols:
      - "bitcoin"
      - "ethereum"
      # 添加更多币种...
```

### 调整策略参数

```yaml
strategy:
  etf_513500:
    trend_following:
      ma_short: 20    # 短期均线周期
      ma_long: 60     # 长期均线周期
```

## 🔑 获取API密钥

### Tushare（推荐用于A股数据）

1. 访问 https://tushare.pro/register
2. 注册并登录
3. 在"个人中心" -> "接口TOKEN"获取
4. 将token填入 `config/api_keys.yaml`

```yaml
tushare:
  token: "你的token"
```

### CoinGecko（加密货币）

免费版无需密钥，直接使用即可。

## 🐛 常见问题

### 问题1：PowerShell无法运行脚本

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题2：ta-lib安装失败

ta-lib是可选的，失败不影响使用。系统会自动使用pandas-ta替代。

### 问题3：端口8501已被占用

```powershell
streamlit run main.py --server.port 8502
```

### 问题4：找不到模块

确保虚拟环境已激活，重新安装依赖：

```powershell
pip install -r requirements.txt --upgrade
```

### 问题5：数据获取失败

- 检查网络连接
- 确认API密钥配置正确
- 查看日志文件 `data/logs/`

## 📊 下一步

1. **第二阶段** - 实现数据获取模块
2. **第三阶段** - 添加技术分析功能
3. **第四阶段** - 实现交易策略
4. **第五阶段** - 完善风险管理

参考README.md了解完整开发路线图。

## 💡 使用技巧

1. **定时更新** - 在配置文件中启用定时任务
2. **数据缓存** - 首次运行会下载历史数据，请耐心等待
3. **参数调优** - 根据实际使用调整策略参数
4. **风险控制** - 设置合理的止损止盈点

## 📞 需要帮助？

- 查看 README.md
- 查看项目Wiki（开发中）
- 提交Issue

祝投资顺利！📈

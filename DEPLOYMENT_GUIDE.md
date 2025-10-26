# 🌐 部署到云端 - 完整指南

## 📋 部署前准备

### 1️⃣ 简化依赖（避免云端超限）

已创建 `requirements_cloud.txt`（轻量版依赖），移除了：
- ❌ PyTorch（太大，约2GB）
- ❌ ta-lib（需要C编译）
- ✅ 保留核心功能（ML预测、因子挖掘、情感分析简化版）

### 2️⃣ 配置文件已创建
- ✅ `.streamlit/config.toml` - Streamlit配置
- ✅ `packages.txt` - 系统依赖（可选）
- ✅ `requirements_cloud.txt` - 云端专用依赖

---

## 🚀 方案1: Streamlit Cloud（推荐，免费）

### 步骤详解

#### Step 1: 推送到GitHub
```powershell
# 在 PersonalQuantAssistant 目录下
cd PersonalQuantAssistant

# 初始化Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "准备部署到Streamlit Cloud"

# 创建GitHub仓库后，关联并推送
git remote add origin https://github.com/你的用户名/PersonalQuantAssistant.git
git branch -M main
git push -u origin main
```

#### Step 2: 部署到Streamlit Cloud
1. **访问**: https://share.streamlit.io
2. **登录GitHub账号**
3. **点击 "New app"**
4. **填写信息**:
   - Repository: `你的用户名/PersonalQuantAssistant`
   - Branch: `main`
   - Main file path: `main.py`
   - Python version: `3.10`
   - **Advanced settings** → Requirements file: `requirements_cloud.txt`
5. **点击 "Deploy"**
6. **等待3-5分钟**，获得公网地址

#### Step 3: 分享地址
```
你的网站地址: https://你的用户名-personalquantassistant.streamlit.app
```

### ⚠️ 云端限制
- 内存: 1GB（已优化依赖）
- 休眠: 7天不访问自动休眠
- 流量: 无限制（但有并发限制）

---

## 🌐 方案2: 局域网访问（同一WiFi）

### 启动命令
```powershell
cd PersonalQuantAssistant
streamlit run main.py --server.address 0.0.0.0 --server.port 8501
```

### 查看本机IP
```powershell
ipconfig
# 找到 "IPv4 地址"，如: 192.168.1.100
```

### 朋友访问
```
浏览器打开: http://192.168.1.100:8501
```

### 防火墙设置（可能需要）
```powershell
# 允许端口8501
netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
```

---

## 🐳 方案3: Docker部署（推荐给有服务器的用户）

### 创建 Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_cloud.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_cloud.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0"]
```

### 构建和运行
```bash
# 构建镜像
docker build -t quant-assistant .

# 运行容器
docker run -p 8501:8501 quant-assistant
```

### 使用 docker-compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

---

## 🌍 方案4: 其他云平台

### Hugging Face Spaces（免费）
1. **访问**: https://huggingface.co/spaces
2. **创建Space** → 选择 Streamlit
3. **上传代码**
4. **获得地址**: `https://huggingface.co/spaces/你的用户名/app名`

### Render（免费tier）
1. **访问**: https://render.com
2. **New** → **Web Service**
3. **连接GitHub仓库**
4. **选择**: Python 3
5. **Start Command**: `streamlit run main.py --server.port $PORT`

### Railway（免费$5额度）
1. **访问**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **自动检测Streamlit配置**

---

## 📱 方案5: 内网穿透（临时分享）

### 使用 ngrok（免费）
```bash
# 1. 下载 ngrok: https://ngrok.com/download

# 2. 启动Streamlit
streamlit run main.py

# 3. 在另一个终端运行ngrok
ngrok http 8501

# 4. 获得临时地址（如）
# https://abc123.ngrok.io
```

### 使用 localtunnel
```bash
# 安装
npm install -g localtunnel

# 启动Streamlit
streamlit run main.py

# 创建隧道
lt --port 8501

# 获得地址: https://random-name.loca.lt
```

---

## 🎯 推荐部署流程（最优方案）

### 对于不同场景

#### 1. **临时演示**（1-2小时）
→ **ngrok / localtunnel**
- ✅ 最快（1分钟）
- ✅ 无需注册
- ❌ 地址临时

#### 2. **长期免费使用**
→ **Streamlit Cloud**
- ✅ 完全免费
- ✅ 永久地址
- ✅ 自动更新（推送GitHub即更新）
- ⚠️ 内存限制1GB

#### 3. **同事/朋友局域网**
→ **局域网访问**
- ✅ 最快速度
- ✅ 无需配置
- ❌ 仅限同一网络

#### 4. **公司内部/生产环境**
→ **Docker + 云服务器**
- ✅ 完全控制
- ✅ 无限制
- ❌ 需要服务器（约$5/月）

---

## 🔧 云端部署优化建议

### 1. 减少依赖大小
```python
# requirements_cloud.txt 已优化
# - 移除 torch（2GB）
# - 移除 ta-lib（编译依赖）
# - 使用 pandas-ta 替代
```

### 2. 数据缓存
```python
# 在代码中添加缓存
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")
```

### 3. 禁用不必要功能
```python
# 云端环境检测
import os
IS_CLOUD = os.getenv("STREAMLIT_CLOUD") == "true"

if not IS_CLOUD:
    # 仅本地启用深度学习
    from src.ai.dl_framework import DLFramework
```

---

## 📊 各方案对比

| 方案 | 难度 | 费用 | 速度 | 限制 | 推荐度 |
|------|------|------|------|------|--------|
| Streamlit Cloud | ⭐ | 免费 | 中 | 1GB内存 | ⭐⭐⭐⭐⭐ |
| 局域网 | ⭐ | 免费 | 快 | 同一网络 | ⭐⭐⭐⭐ |
| ngrok | ⭐ | 免费 | 中 | 临时地址 | ⭐⭐⭐ |
| Docker | ⭐⭐⭐ | $5/月 | 快 | 无 | ⭐⭐⭐⭐ |
| Hugging Face | ⭐⭐ | 免费 | 慢 | 较慢 | ⭐⭐⭐ |

---

## 🚀 快速开始（推荐）

### 最快方案：局域网访问（30秒）
```powershell
# 1. 启动服务
streamlit run main.py --server.address 0.0.0.0

# 2. 查看IP
ipconfig

# 3. 分享地址给朋友
# http://你的IP:8501
```

### 最佳方案：Streamlit Cloud（5分钟）
```powershell
# 1. 推送到GitHub
git init
git add .
git commit -m "部署准备"
git remote add origin https://github.com/你的用户名/PersonalQuantAssistant.git
git push -u origin main

# 2. 访问 https://share.streamlit.io
# 3. 选择仓库，点击Deploy
# 4. 5分钟后获得永久地址
```

---

## 📞 常见问题

### Q1: Streamlit Cloud部署失败？
**原因**: 依赖包太大或不兼容  
**解决**: 
```bash
# 使用轻量版依赖
git add requirements_cloud.txt
git commit -m "使用云端依赖"
git push

# 在Streamlit Cloud设置中：
# Advanced settings → Requirements file → requirements_cloud.txt
```

### Q2: 朋友访问显示"无法连接"？
**原因**: 防火墙阻止  
**解决**:
```powershell
# Windows防火墙添加规则
netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
```

### Q3: ngrok速度太慢？
**原因**: 免费版服务器在国外  
**解决**: 
- 使用国内替代品：https://natapp.cn
- 或升级ngrok付费版

### Q4: 云端运行报错"内存不足"？
**原因**: 免费tier内存限制1GB  
**解决**:
- 减少数据加载量
- 使用 `@st.cache_data` 缓存
- 限制历史数据范围（如最近1年）

---

**选择最适合你的方案开始部署吧！** 🚀✨

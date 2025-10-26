# 🚀 Streamlit Cloud 部署步骤

## ✅ Git准备已完成

代码已提交到本地Git仓库：
- ✅ Git仓库初始化
- ✅ 所有文件已添加（125个文件）
- ✅ 提交消息："准备部署到Streamlit Cloud - AI量化投资系统v2.0"

---

## 📋 接下来的步骤（需要手动操作）

### 第1步：创建GitHub仓库

1. **访问GitHub**: https://github.com/new
2. **填写信息**:
   - Repository name: `PersonalQuantAssistant`
   - Description: `AI量化投资系统 - ML预测/因子挖掘/情感分析`
   - 选择: **Public** 或 **Private**（推荐Public，便于分享）
   - ❌ 不要勾选 "Initialize this repository with..."

3. **点击 "Create repository"**

### 第2步：推送代码到GitHub

复制并执行以下命令（替换你的GitHub用户名）：

```powershell
# 在 PersonalQuantAssistant 目录下执行
cd c:\Users\andewa1ker\Desktop\Kris\PersonalQuantAssistant

# 关联GitHub仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/andewa1ker/PersonalQuantAssistant.git

# 推送代码
git branch -M main
git push -u origin main
```

如果遇到认证问题，使用Personal Access Token：
```powershell
# 推送时会提示输入用户名和密码
# 用户名：你的GitHub用户名
# 密码：使用Personal Access Token（不是GitHub密码）
# 创建Token：https://github.com/settings/tokens
```

---

### 第3步：部署到Streamlit Cloud

1. **访问**: https://share.streamlit.io

2. **登录GitHub账号**

3. **点击 "New app"**

4. **填写部署信息**:
   ```
   Repository: andewa1ker/PersonalQuantAssistant
   Branch: main
   Main file path: main.py
   App URL (可选): your-app-name
   ```

5. **点击 "Advanced settings"**:
   ```
   Python version: 3.10
   Requirements file: requirements_cloud.txt  ⚠️ 重要！
   ```

6. **点击 "Deploy!"**

7. **等待3-5分钟** ⏳

---

## 🎉 部署完成后

你将获得一个永久地址：
```
https://andewa1ker-personalquantassistant.streamlit.app
```

或自定义的：
```
https://your-app-name.streamlit.app
```

### 分享给朋友
直接发送地址即可，无需任何配置！

---

## ⚙️ 部署配置说明

### 使用轻量版依赖（requirements_cloud.txt）
为了避免云端1GB内存限制，我们移除了：
- ❌ PyTorch（约2GB）
- ❌ ta-lib（需要C编译）

保留的核心功能：
- ✅ ML预测（Random Forest, GBDT, Ridge）
- ✅ 因子挖掘（遗传编程）
- ✅ 情感分析（简化版，无jieba）
- ✅ 技术分析（pandas-ta）
- ✅ 数据获取（AKShare）

### 如果需要完整功能
本地运行使用：
```bash
pip install -r requirements.txt
streamlit run main.py
```

---

## 🔧 常见问题

### Q1: 推送到GitHub时提示认证失败？
**解决方案**:
1. 创建Personal Access Token:
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 复制生成的token

2. 推送时使用token作为密码:
   ```powershell
   git push -u origin main
   # 用户名: andewa1ker
   # 密码: 粘贴你的token（不是GitHub密码）
   ```

### Q2: Streamlit Cloud部署失败 - 内存不足？
**原因**: 使用了 `requirements.txt` 而非 `requirements_cloud.txt`

**解决方案**:
1. 在Streamlit Cloud界面
2. 点击右上角 Settings → Advanced settings
3. 修改 `Requirements file` 为 `requirements_cloud.txt`
4. 点击 Save → Reboot

### Q3: 部署后页面报错 "Module not found"？
**原因**: 缺少依赖包

**解决方案**:
检查 `requirements_cloud.txt` 是否包含所需依赖，如果缺失：
```bash
# 本地测试
pip install -r requirements_cloud.txt
python -c "import streamlit; import pandas; import plotly; print('OK')"
```

### Q4: 想要修改代码后自动更新？
**超级简单**:
```powershell
# 修改代码后
git add .
git commit -m "更新说明"
git push

# Streamlit Cloud会自动检测并重新部署！
```

---

## 📊 部署后的优势

### ✅ 永久访问
- 24/7在线
- 无需本地运行
- 自动休眠（7天不访问）

### ✅ 自动更新
- 推送GitHub → 自动部署
- 无需手动操作

### ✅ 免费使用
- 完全免费
- 无流量限制
- 1GB内存（已优化）

### ✅ 易于分享
- 直接发送链接
- 朋友无需安装任何东西
- 全球访问

---

## 🎯 下一步

1. **立即执行上述3个步骤**
2. **测试部署后的网站**
3. **分享链接给朋友**
4. **享受云端AI量化系统！** 🚀

---

**遇到问题？查看完整指南**: `DEPLOYMENT_GUIDE.md`

**GitHub仓库创建后，运行**:
```powershell
cd c:\Users\andewa1ker\Desktop\Kris\PersonalQuantAssistant
git remote add origin https://github.com/andewa1ker/PersonalQuantAssistant.git
git push -u origin main
```

**然后访问**: https://share.streamlit.io 完成部署！✨

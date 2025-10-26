@echo off
chcp 65001 >nul
title 量化投资助手 - Apple风格版

echo ╔════════════════════════════════════════════════════════╗
echo ║     量化投资助手 - Personal Quant Assistant          ║
echo ║              Apple官网级UI体验                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo [1/3] 检测Python环境...

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [✓] Python环境正常
echo.
echo [2/3] 检测依赖包...

python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少依赖包，正在自动安装...
    pip install streamlit plotly pandas akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [✓] 依赖包检测完成
echo.
echo [3/3] 启动应用...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  应用将在浏览器中自动打开
echo  本地访问地址: http://localhost:8503
echo  按 Ctrl+C 停止服务
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

streamlit run main.py --server.port=8503 --server.headless=true

pause

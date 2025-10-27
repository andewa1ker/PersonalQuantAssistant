# 量化投资助手启动脚本 - PowerShell版本
# Apple官网级UI体验

$Host.UI.RawUI.WindowTitle = "量化投资助手 - Apple风格版"

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     量化投资助手 - Personal Quant Assistant          ║" -ForegroundColor Cyan
Write-Host "║              Apple官网级UI体验                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 检测Python
Write-Host "[1/3] 检测Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python环境正常: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检测依赖
Write-Host "`n[2/3] 检测依赖包..." -ForegroundColor Yellow
try {
    python -c "import streamlit" 2>$null
    Write-Host "[✓] 依赖包检测完成" -ForegroundColor Green
} catch {
    Write-Host "[!] 缺少依赖包，正在自动安装..." -ForegroundColor Yellow
    pip install streamlit plotly pandas akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
}

# 启动应用
Write-Host "`n[3/3] 启动应用...`n" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host " 应用将在浏览器中自动打开" -ForegroundColor White
Write-Host " 本地访问地址: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8503" -ForegroundColor Cyan
Write-Host " 按 Ctrl+C 停止服务" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Blue

streamlit run Home.py --server.port=8503 --server.headless=true

Read-Host "`n按回车键退出"

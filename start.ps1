# PersonalQuantAssistant 启动脚本
# Windows PowerShell版本

Write-Host "=" -ForegroundColor Cyan
Write-Host "启动 PersonalQuantAssistant" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✓ 虚拟环境已激活" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "! 未找到虚拟环境，请先运行 install.ps1" -ForegroundColor Red
    Write-Host "  .\install.ps1" -ForegroundColor Gray
    exit 1
}

# 启动Streamlit应用
Write-Host "启动Web应用..." -ForegroundColor Yellow
Write-Host "浏览器将自动打开 http://localhost:8501" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Cyan
Write-Host ""

streamlit run main.py

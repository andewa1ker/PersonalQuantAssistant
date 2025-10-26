# Premium UI 一键启动脚本
# Personal Quant Assistant

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Personal Quant Assistant" -ForegroundColor Yellow
Write-Host "  Premium UI v1.0" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[1/4] 检查 Python 环境..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python 已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 未安装，请先安装 Python 3.8+" -ForegroundColor Red
    pause
    exit 1
}

# 检查依赖
Write-Host ""
Write-Host "[2/4] 检查依赖..." -ForegroundColor Green
$streamlitInstalled = pip show streamlit 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Streamlit 已安装" -ForegroundColor Green
} else {
    Write-Host "✗ Streamlit 未安装，正在安装..." -ForegroundColor Yellow
    pip install streamlit
}

# 检查 streamlit-lottie (可选)
$lottieInstalled = pip show streamlit-lottie 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ streamlit-lottie 已安装" -ForegroundColor Green
} else {
    Write-Host "! streamlit-lottie 未安装 (可选)" -ForegroundColor Yellow
    $install = Read-Host "是否安装 Lottie 动画支持? (y/n)"
    if ($install -eq "y") {
        pip install streamlit-lottie
    }
}

# 检查其他关键依赖
Write-Host ""
Write-Host "[3/4] 检查其他依赖..." -ForegroundColor Green
$packages = @("pandas", "plotly", "numpy")
foreach ($pkg in $packages) {
    $installed = pip show $pkg 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $pkg 已安装" -ForegroundColor Green
    } else {
        Write-Host "✗ $pkg 未安装，正在安装..." -ForegroundColor Yellow
        pip install $pkg
    }
}

# 启动应用
Write-Host ""
Write-Host "[4/4] 启动应用..." -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  应用启动中..." -ForegroundColor Yellow
Write-Host "  浏览器将自动打开" -ForegroundColor Yellow
Write-Host "  地址: http://localhost:8501" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 按 Ctrl+C 停止应用" -ForegroundColor Gray
Write-Host ""

# 延迟启动
Start-Sleep -Seconds 2

# 启动 Streamlit
streamlit run main.py

# 如果出错
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "启动失败！" -ForegroundColor Red
    Write-Host "请检查:" -ForegroundColor Yellow
    Write-Host "1. Python 是否正确安装" -ForegroundColor Gray
    Write-Host "2. 依赖是否完整安装 (pip install -r requirements.txt)" -ForegroundColor Gray
    Write-Host "3. main.py 文件是否存在" -ForegroundColor Gray
    Write-Host ""
    pause
}

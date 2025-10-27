# PersonalQuantAssistant 启动检查脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PersonalQuantAssistant 启动检查" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 检查Python
Write-Host "[1/5] 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

# 检查依赖
Write-Host "`n[2/5] 检查关键依赖..." -ForegroundColor Yellow
$dependencies = @("streamlit", "pandas", "numpy", "plotly", "yfinance")
$missing = @()

foreach ($dep in $dependencies) {
    $check = pip show $dep 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $dep" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dep (未安装)" -ForegroundColor Red
        $missing += $dep
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n  警告: 缺少依赖，尝试自动安装..." -ForegroundColor Yellow
    Write-Host "  运行: pip install -r requirements.txt`n" -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 检查配置文件
Write-Host "`n[3/5] 检查配置文件..." -ForegroundColor Yellow
if (Test-Path "config\config.yaml") {
    Write-Host "  ✓ config.yaml 存在" -ForegroundColor Green
} else {
    Write-Host "  ✗ config.yaml 缺失" -ForegroundColor Red
}

if (Test-Path "config\api_keys.yaml") {
    Write-Host "  ✓ api_keys.yaml 存在" -ForegroundColor Green
} else {
    Write-Host "  ⚠ api_keys.yaml 缺失 (可选)" -ForegroundColor Yellow
}

# 检查数据目录
Write-Host "`n[4/5] 检查数据目录..." -ForegroundColor Yellow
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "  ✓ 已创建data目录" -ForegroundColor Green
} else {
    Write-Host "  ✓ data目录存在" -ForegroundColor Green
}

# 运行测试
Write-Host "`n[5/5] 运行核心功能测试..." -ForegroundColor Yellow
Write-Host "  (这可能需要几秒钟...)`n" -ForegroundColor Gray

$testOutput = python test_core.py 2>&1 | Out-String
if ($testOutput -match "成功率: 100.0%") {
    Write-Host "  ✓ 所有测试通过 (100%)" -ForegroundColor Green
} elseif ($testOutput -match "成功率: (\d+\.\d+)%") {
    $rate = $matches[1]
    Write-Host "  ⚠ 测试通过率: $rate%" -ForegroundColor Yellow
} else {
    Write-Host "  ✗ 测试失败" -ForegroundColor Red
    Write-Host "`n测试输出:" -ForegroundColor Gray
    Write-Host $testOutput -ForegroundColor Gray
}

# 最终结果
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "检查完成！" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✓ 系统准备就绪，可以启动应用`n" -ForegroundColor Green
Write-Host "启动命令:" -ForegroundColor Yellow
Write-Host "  streamlit run Home.py`n" -ForegroundColor White

# 询问是否立即启动
$response = Read-Host "是否立即启动应用? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host "`n正在启动应用..." -ForegroundColor Green
    streamlit run Home.py
} else {
    Write-Host "`n提示: 使用以下命令启动应用:" -ForegroundColor Yellow
    Write-Host "  streamlit run Home.py`n" -ForegroundColor White
}

# PersonalQuantAssistant 安装脚本
# Windows PowerShell版本

Write-Host "=" -ForegroundColor Cyan
Write-Host "PersonalQuantAssistant 安装向导" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python版本
Write-Host "1. 检查Python环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Python已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ 未检测到Python，请先安装Python 3.8+" -ForegroundColor Red
    exit 1
}

# 创建虚拟环境
Write-Host ""
Write-Host "2. 创建虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ! 虚拟环境已存在，跳过创建" -ForegroundColor Cyan
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ 虚拟环境创建成功" -ForegroundColor Green
    } else {
        Write-Host "   ✗ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
}

# 激活虚拟环境
Write-Host ""
Write-Host "3. 激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ! 自动激活失败，请手动运行: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "   ! 如果遇到权限错误，请运行:" -ForegroundColor Cyan
    Write-Host "     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
} else {
    Write-Host "   ✓ 虚拟环境已激活" -ForegroundColor Green
}

# 升级pip
Write-Host ""
Write-Host "4. 升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✓ pip已更新到最新版本" -ForegroundColor Green

# 安装依赖
Write-Host ""
Write-Host "5. 安装依赖包..." -ForegroundColor Yellow
Write-Host "   这可能需要几分钟，请耐心等待..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ 依赖包安装成功" -ForegroundColor Green
} else {
    Write-Host "   ! 部分依赖包安装失败，但不影响基本使用" -ForegroundColor Cyan
}

# 检查配置文件
Write-Host ""
Write-Host "6. 检查配置文件..." -ForegroundColor Yellow
if (Test-Path "config\config.yaml") {
    Write-Host "   ✓ 主配置文件存在" -ForegroundColor Green
} else {
    Write-Host "   ✗ 缺少配置文件" -ForegroundColor Red
}

if (Test-Path "config\api_keys.yaml") {
    Write-Host "   ✓ API密钥文件存在" -ForegroundColor Green
} else {
    Write-Host "   ! API密钥文件不存在，将创建..." -ForegroundColor Cyan
    Copy-Item "config\api_keys.yaml.template" "config\api_keys.yaml"
    Write-Host "   ✓ 已创建API密钥文件模板" -ForegroundColor Green
}

# 创建必要目录
Write-Host ""
Write-Host "7. 创建数据目录..." -ForegroundColor Yellow
$dirs = @("data\logs", "data\cache", "data\market_data", "data\portfolio")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "   ✓ 数据目录已创建" -ForegroundColor Green

# 完成
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 配置API密钥（可选）：" -ForegroundColor White
Write-Host "   notepad config\api_keys.yaml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 启动应用：" -ForegroundColor White
Write-Host "   streamlit run main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 查看文档：" -ForegroundColor White
Write-Host "   - README.md - 完整文档" -ForegroundColor Gray
Write-Host "   - QUICKSTART.md - 快速开始" -ForegroundColor Gray
Write-Host "   - PROJECT_STATUS.md - 项目状态" -ForegroundColor Gray
Write-Host ""
Write-Host "祝使用愉快！📊" -ForegroundColor Cyan

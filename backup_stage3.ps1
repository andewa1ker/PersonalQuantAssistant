# 项目备份脚本
# PersonalQuantAssistant Stage 3 完成备份

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectPath = "c:\Users\andewa1ker\Desktop\Kris\PersonalQuantAssistant"
$backupPath = "c:\Users\andewa1ker\Desktop\Kris\Backup_Stage3_$timestamp"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " PersonalQuantAssistant 项目备份" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "项目路径: $projectPath" -ForegroundColor Yellow
Write-Host "备份路径: $backupPath" -ForegroundColor Yellow
Write-Host ""

# 创建备份目录
Write-Host "[1/5] 创建备份目录..." -ForegroundColor Green
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# 复制源代码
Write-Host "[2/5] 复制源代码..." -ForegroundColor Green
Copy-Item -Path "$projectPath\src" -Destination "$backupPath\src" -Recurse -Force

# 复制配置文件
Write-Host "[3/5] 复制配置文件..." -ForegroundColor Green
Copy-Item -Path "$projectPath\config" -Destination "$backupPath\config" -Recurse -Force

# 复制主文件和文档
Write-Host "[4/5] 复制主文件和文档..." -ForegroundColor Green
$filesToCopy = @(
    "main.py",
    "requirements.txt",
    "README.md",
    "QUICKSTART.md",
    "PROJECT_STATUS.md",
    "ARCHITECTURE.md",
    "DEVELOPMENT_GUIDE.md",
    "CHANGELOG.md",
    "STAGE2_COMPLETE.md",
    "STAGE3_COMPLETE.md",
    "STAGE3_SUMMARY.md",
    "START_HERE.md",
    "test_stage3.py",
    ".gitignore"
)

foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $projectPath $file
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $backupPath -Force
        Write-Host "  ✓ $file" -ForegroundColor Gray
    }
}

# 创建备份信息文件
Write-Host "[5/5] 创建备份信息..." -ForegroundColor Green
$backupInfo = @"
# 备份信息

## 备份时间
$timestamp

## 备份内容
- src/ - 所有源代码
- config/ - 配置文件
- main.py - 主程序
- requirements.txt - 依赖列表
- 所有文档文件

## Stage 3 完成状态
✅ 技术分析引擎 (4个模块, ~1450行)
✅ Web界面集成 (ETF/加密货币技术分析页签)
✅ 策略信号中心 (真实信号生成)
✅ 测试验证 (全部通过)

## 文件统计
- Python文件: $(Get-ChildItem -Path "$backupPath" -Recurse -Filter "*.py" | Measure-Object).Count 个
- 总文件数: $(Get-ChildItem -Path "$backupPath" -Recurse -File | Measure-Object).Count 个
- 备份大小: $((Get-ChildItem -Path "$backupPath" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB) MB

## 恢复方法
1. 复制整个备份文件夹内容
2. 安装依赖: pip install -r requirements.txt
3. 运行应用: streamlit run main.py

## 下一步
Stage 4: 投资策略引擎开发
"@

$backupInfo | Out-File -FilePath "$backupPath\BACKUP_INFO.md" -Encoding UTF8

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " 备份完成！" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "备份位置: $backupPath" -ForegroundColor Yellow
Write-Host ""

# 显示统计信息
$fileCount = (Get-ChildItem -Path "$backupPath" -Recurse -File | Measure-Object).Count
$folderCount = (Get-ChildItem -Path "$backupPath" -Recurse -Directory | Measure-Object).Count
$totalSize = (Get-ChildItem -Path "$backupPath" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "📊 备份统计:" -ForegroundColor Cyan
Write-Host "  文件数量: $fileCount" -ForegroundColor Gray
Write-Host "  目录数量: $folderCount" -ForegroundColor Gray
Write-Host "  总大小: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Gray
Write-Host ""

# 压缩备份（可选）
$compress = Read-Host "是否压缩备份？ (Y/N)"
if ($compress -eq 'Y' -or $compress -eq 'y') {
    Write-Host ""
    Write-Host "正在压缩备份..." -ForegroundColor Green
    $zipPath = "$backupPath.zip"
    Compress-Archive -Path $backupPath -DestinationPath $zipPath -Force
    Write-Host "✓ 压缩完成: $zipPath" -ForegroundColor Green
    
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "  压缩后大小: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ 所有操作完成！" -ForegroundColor Green
Write-Host ""

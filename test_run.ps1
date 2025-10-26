# PersonalQuantAssistant 测试脚本
# 测试各个模块是否能正常工作

Write-Host "=" -ForegroundColor Cyan
Write-Host "PersonalQuantAssistant 模块测试" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 进入项目目录
cd c:\Users\andewa1ker\Desktop\Kris\PersonalQuantAssistant

Write-Host "1. 测试配置模块..." -ForegroundColor Yellow
python -c "from src.utils.config_loader import get_config; config = get_config(); print(f'   ✓ 配置加载成功: {config.app_name}')"

Write-Host ""
Write-Host "2. 测试股票数据模块..." -ForegroundColor Yellow
python -c "from src.data_fetcher.stock_data import StockDataFetcher; f = StockDataFetcher(); print('   ✓ 股票数据模块加载成功')"

Write-Host ""
Write-Host "3. 测试加密货币数据模块..." -ForegroundColor Yellow
python -c "from src.data_fetcher.crypto_data import CryptoDataFetcher; f = CryptoDataFetcher(); print('   ✓ 加密货币数据模块加载成功')"

Write-Host ""
Write-Host "4. 测试数据管理器..." -ForegroundColor Yellow
python -c "from src.data_fetcher.data_manager import DataManager; dm = DataManager(); print('   ✓ 数据管理器加载成功')"

Write-Host ""
Write-Host "5. 测试数据库模块..." -ForegroundColor Yellow
python -c "from src.data_fetcher.database import Database; db = Database(); print('   ✓ 数据库模块加载成功')"

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "所有模块测试完成！" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "准备启动Web应用..." -ForegroundColor Yellow
Write-Host "按任意键启动Streamlit应用，或Ctrl+C退出" -ForegroundColor Cyan
pause

streamlit run main.py

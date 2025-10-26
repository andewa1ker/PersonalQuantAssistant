"""
快速集成测试 - 验证Stage 4策略功能
"""
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_quick_integration():
    """快速集成测试"""
    print("\n" + "="*70)
    print("🚀 Stage 4 快速集成测试")
    print("="*70)
    
    results = []
    
    # 测试1: 导入所有策略模块
    print("\n[1/5] 测试模块导入...")
    try:
        from strategy import (
            BaseStrategy, 
            StrategyResult,
            ETFValuationStrategy,
            CryptoMomentumStrategy,
            DCAStrategy,
            PortfolioManager
        )
        print("  ✅ 所有策略模块导入成功")
        results.append(("模块导入", True))
    except Exception as e:
        print(f"  ❌ 模块导入失败: {e}")
        results.append(("模块导入", False))
        return results
    
    # 生成测试数据
    print("\n[2/5] 生成测试数据...")
    dates = [datetime.now() - timedelta(days=i) for i in range(365)]
    dates.reverse()
    
    np.random.seed(42)
    base_price = 1.200
    returns = np.random.normal(0.0005, 0.015, 365)
    prices = base_price * (1 + returns).cumprod()
    
    test_data = pd.DataFrame({
        'date': dates,
        'close': prices,
        'open': prices * 0.995,
        'high': prices * 1.015,
        'low': prices * 0.985,
        'volume': np.random.uniform(1e6, 5e6, 365),
        'pe': np.random.uniform(12, 25, 365),
        'pb': np.random.uniform(1.5, 4.0, 365)
    })
    print(f"  ✅ 测试数据生成完成: {len(test_data)} 条记录")
    
    # 测试2: ETF估值策略
    print("\n[3/5] 测试ETF估值策略...")
    try:
        strategy = ETFValuationStrategy({'buy_percentile': 30, 'sell_percentile': 70})
        result = strategy.analyze(test_data, asset_symbol='TEST_ETF', capital=100000)
        print(f"  ✅ 策略执行成功")
        print(f"     - 操作建议: {result.action}")
        print(f"     - 信心度: {result.confidence:.0%}")
        print(f"     - 当前价格: ¥{result.current_price:.3f}")
        results.append(("ETF估值策略", True))
    except Exception as e:
        print(f"  ❌ 策略执行失败: {e}")
        results.append(("ETF估值策略", False))
    
    # 测试3: 加密货币动量策略
    print("\n[4/5] 测试加密货币动量策略...")
    try:
        strategy = CryptoMomentumStrategy({'short_window': 10, 'long_window': 30})
        result = strategy.analyze(test_data.head(90), asset_symbol='BTC', capital=50000)
        print(f"  ✅ 策略执行成功")
        print(f"     - 操作建议: {result.action}")
        print(f"     - 信心度: {result.confidence:.0%}")
        results.append(("加密货币动量", True))
    except Exception as e:
        print(f"  ❌ 策略执行失败: {e}")
        results.append(("加密货币动量", False))
    
    # 测试4: 定投策略
    print("\n[5/5] 测试定投策略...")
    try:
        strategy = DCAStrategy({'base_amount': 1000, 'frequency': 7, 'dca_type': 'smart'})
        result = strategy.analyze(test_data, asset_symbol='TEST', valuation_percentile=40)
        print(f"  ✅ 策略执行成功")
        print(f"     - 操作建议: {result.action}")
        if result.action == 'buy':
            dca_amount = result.indicators.get('dca_amount', 1000)
            print(f"     - 定投金额: ¥{dca_amount:.2f}")
        results.append(("定投策略", True))
    except Exception as e:
        print(f"  ❌ 策略执行失败: {e}")
        results.append(("定投策略", False))
    
    return results


def test_web_imports():
    """测试Web页面导入"""
    print("\n" + "="*70)
    print("🌐 测试Web界面集成")
    print("="*70)
    
    try:
        from strategy_page import (
            show_strategy_page,
            show_etf_valuation_strategy,
            show_crypto_momentum_strategy,
            show_dca_strategy,
            show_portfolio_rebalance
        )
        print("\n  ✅ 所有Web页面函数导入成功")
        print("     - show_strategy_page")
        print("     - show_etf_valuation_strategy")
        print("     - show_crypto_momentum_strategy")
        print("     - show_dca_strategy")
        print("     - show_portfolio_rebalance")
        return True
    except Exception as e:
        print(f"\n  ❌ Web页面导入失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "🎯" * 35)
    print("PersonalQuantAssistant - Stage 4 集成测试")
    print("🎯" * 35)
    
    # 运行策略测试
    strategy_results = test_quick_integration()
    
    # 运行Web测试
    web_success = test_web_imports()
    
    # 汇总结果
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    print("\n策略功能测试:")
    for name, success in strategy_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name:<20} {status}")
    
    print("\nWeb界面集成:")
    status = "✅ 通过" if web_success else "❌ 失败"
    print(f"  Web页面导入        {status}")
    
    # 统计
    total_tests = len(strategy_results) + 1
    passed_tests = sum(1 for _, s in strategy_results if s) + (1 if web_success else 0)
    
    print("\n" + "="*70)
    print(f"总计: {passed_tests}/{total_tests} 测试通过")
    print("="*70)
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！Stage 4 策略引擎运行正常！")
        print("\n✨ 可以访问 http://localhost:8501 查看Web界面")
        print("   点击侧边栏的 '💰 投资策略' 体验所有策略功能")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit(main())

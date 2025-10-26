"""
测试技术分析模块
"""
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_test_data(days=60):
    """生成测试数据"""
    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    # 生成模拟价格数据
    np.random.seed(42)
    base_price = 1.000
    returns = np.random.normal(0.001, 0.02, days)
    prices = base_price * (1 + returns).cumprod()
    
    # 生成OHLCV数据
    data = pd.DataFrame({
        'date': dates,
        'open': prices * np.random.uniform(0.98, 1.02, days),
        'high': prices * np.random.uniform(1.00, 1.05, days),
        'low': prices * np.random.uniform(0.95, 1.00, days),
        'close': prices,
        'volume': np.random.uniform(1e6, 5e6, days)
    })
    
    return data

def test_technical_analyzer():
    """测试技术分析器"""
    print("\n" + "="*60)
    print("测试 TechnicalAnalyzer")
    print("="*60)
    
    try:
        from analysis.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        data = generate_test_data()
        
        print(f"✓ 成功导入 TechnicalAnalyzer")
        print(f"✓ 生成测试数据: {len(data)} 条记录")
        
        # 测试各个指标
        data_with_ma = analyzer.calculate_ma(data)
        print(f"✓ 计算MA成功: {[c for c in data_with_ma.columns if 'MA' in c]}")
        
        data_with_indicators = analyzer.calculate_all_indicators(data)
        print(f"✓ 计算所有指标成功")
        print(f"  指标列: {[c for c in data_with_indicators.columns if c not in data.columns]}")
        
        summary = analyzer.get_indicator_summary(data_with_indicators)
        print(f"✓ 获取指标汇总成功")
        print(f"  当前价格: {summary['price']['current']:.4f}")
        print(f"  RSI: {summary['rsi']['RSI']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trend_analyzer():
    """测试趋势分析器"""
    print("\n" + "="*60)
    print("测试 TrendAnalyzer")
    print("="*60)
    
    try:
        from analysis.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer()
        data = generate_test_data()
        
        print(f"✓ 成功导入 TrendAnalyzer")
        
        trend_info = analyzer.identify_trend(data)
        print(f"✓ 识别趋势成功")
        print(f"  趋势: {trend_info['trend']}")
        print(f"  强度: {trend_info['strength']}")
        print(f"  均线排列: {trend_info['ma_alignment']}")
        
        sr_levels = analyzer.find_support_resistance(data)
        print(f"✓ 找到支撑阻力位")
        print(f"  支撑位: {sr_levels['support']}")
        print(f"  阻力位: {sr_levels['resistance']}")
        
        trend_strength = analyzer.calculate_trend_strength(data)
        print(f"✓ 计算趋势强度成功")
        print(f"  ADX: {trend_strength.get('adx', 0):.2f}")
        print(f"  强度描述: {trend_strength.get('strength_description', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_volatility_analyzer():
    """测试波动率分析器"""
    print("\n" + "="*60)
    print("测试 VolatilityAnalyzer")
    print("="*60)
    
    try:
        from analysis.volatility_analyzer import VolatilityAnalyzer
        
        analyzer = VolatilityAnalyzer()
        data = generate_test_data()
        
        print(f"✓ 成功导入 VolatilityAnalyzer")
        
        hist_vol = analyzer.calculate_historical_volatility(data)
        print(f"✓ 计算历史波动率成功")
        print(f"  当前波动率: {hist_vol['current_volatility']:.2f}%")
        print(f"  波动率级别: {hist_vol['volatility_level']}")
        
        regime = analyzer.analyze_volatility_regime(data)
        print(f"✓ 分析波动率状态成功")
        print(f"  趋势: {regime['trend']}")
        print(f"  状态: {regime['regime']}")
        
        risk = analyzer.calculate_risk_metrics(data)
        print(f"✓ 计算风险指标成功")
        print(f"  最大回撤: {risk.get('max_drawdown', 0):.2f}%")
        print(f"  夏普比率: {risk.get('sharpe_ratio', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_generator():
    """测试信号生成器"""
    print("\n" + "="*60)
    print("测试 SignalGenerator")
    print("="*60)
    
    try:
        from analysis.signal_generator import SignalGenerator
        
        generator = SignalGenerator()
        data = generate_test_data()
        
        print(f"✓ 成功导入 SignalGenerator")
        
        # 完整分析
        report = generator.analyze_with_signals(data)
        
        print(f"✓ 完整分析成功")
        
        if 'signals' in report:
            signals = report['signals']
            print(f"\n交易信号:")
            print(f"  信号: {signals['signal']}")
            print(f"  信心度: {signals['confidence']}")
            print(f"  强度: {signals['total_strength']}")
            print(f"  买入信号数: {signals['buy_signals']}")
            print(f"  卖出信号数: {signals['sell_signals']}")
            
            print(f"\n信号理由:")
            for reason in signals['reasons'][:3]:
                print(f"  • {reason}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("PersonalQuantAssistant - Stage 3 模块测试")
    print("="*60)
    
    results = []
    
    # 测试各模块
    results.append(("TechnicalAnalyzer", test_technical_analyzer()))
    results.append(("TrendAnalyzer", test_trend_analyzer()))
    results.append(("VolatilityAnalyzer", test_volatility_analyzer()))
    results.append(("SignalGenerator", test_signal_generator()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试汇总")
    print("="*60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name:<25} {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())

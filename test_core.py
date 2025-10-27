"""
测试核心功能模块
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path.cwd() / "src"))

def test_config():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")
    try:
        from utils.config_loader import get_config
        config = get_config()
        print(f"✅ 配置加载成功")
        print(f"   应用名称: {config.get('app.name')}")
        print(f"   版本: {config.get('app.version', config.app_version)}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_data_manager():
    """测试数据管理器"""
    print("\n=== 测试数据管理器 ===")
    try:
        from data_fetcher.data_manager import DataManager
        dm = DataManager()
        print("✅ DataManager初始化成功")
        
        # 测试获取加密货币数据
        print("\n尝试获取Bitcoin实时数据...")
        data = dm.get_asset_data('crypto', 'bitcoin', 'realtime')
        if data:
            # 支持多种可能的字段名
            price = data.get('current_price') or data.get('price_usd') or data.get('price')
            change = data.get('price_change_percentage_24h') or data.get('change_24h') or 0
            
            if price:
                print(f"✅ 成功获取Bitcoin价格: ${price:,.2f}")
                print(f"   24h变化: {change:+.2f}%")
                return True
            else:
                print(f"⚠️ 获取到数据但格式不正确: {data.keys()}")
                return False
        else:
            print("⚠️ 未能获取Bitcoin数据（可能是网络问题）")
            return False
            
    except Exception as e:
        print(f"❌ DataManager错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_generator():
    """测试信号生成器"""
    print("\n=== 测试信号生成器 ===")
    try:
        from analysis.signal_generator import SignalGenerator
        import pandas as pd
        import numpy as np
        
        sg = SignalGenerator()
        print("✅ SignalGenerator初始化成功")
        
        # 创建模拟数据
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        prices = np.random.randn(100).cumsum() + 100
        data = pd.DataFrame({
            'close': prices,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'open': prices,
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        print("\n生成交易信号...")
        result = sg.analyze_with_signals(data)
        
        if result and 'signals' in result:
            print(f"✅ 信号生成成功")
            print(f"   信号: {result['signals']['signal']}")
            print(f"   信心度: {result['signals']['confidence']}")
            print(f"   强度: {result['signals']['total_strength']}")
            return True
        else:
            print("⚠️ 信号生成返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ SignalGenerator错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backtest_engine():
    """测试回测引擎"""
    print("\n=== 测试回测引擎 ===")
    try:
        from strategy.backtest_engine import BacktestEngine, BacktestConfig
        print("✅ BacktestEngine导入成功")
        
        config = BacktestConfig(initial_capital=100000)
        engine = BacktestEngine(config)
        print("✅ BacktestEngine初始化成功")
        return True
            
    except Exception as e:
        print(f"❌ BacktestEngine错误: {e}")
        return False


def test_risk_monitor():
    """测试风险监控"""
    print("\n=== 测试风险监控 ===")
    try:
        from risk_management.risk_monitor import RiskMonitor
        print("✅ RiskMonitor导入成功")
        
        monitor = RiskMonitor()
        print("✅ RiskMonitor初始化成功")
        return True
            
    except Exception as e:
        print(f"❌ RiskMonitor错误: {e}")
        return False


def test_ai_assistant():
    """测试AI助手"""
    print("\n=== 测试AI助手 ===")
    try:
        from ai.ai_assistant import AIAssistant
        print("✅ AIAssistant导入成功")
        
        # 不实际初始化（需要API key）
        print("⚠️ 跳过实际初始化（需要API密钥）")
        return True
            
    except Exception as e:
        print(f"❌ AIAssistant错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PersonalQuantAssistant 核心功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("配置加载", test_config()))
    results.append(("数据管理器", test_data_manager()))
    results.append(("信号生成器", test_signal_generator()))
    results.append(("回测引擎", test_backtest_engine()))
    results.append(("风险监控", test_risk_monitor()))
    results.append(("AI助手", test_ai_assistant()))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:.<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"总计: {len(results)}个测试")
    print(f"通过: {passed}个")
    print(f"失败: {failed}个")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    print("=" * 60)

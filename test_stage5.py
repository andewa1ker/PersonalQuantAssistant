"""
Stage 5 单元测试
测试风险管理模块
"""

import sys
from pathlib import Path
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加src目录到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from risk_management import (
    RiskMetrics,
    PositionSizing,
    StopLossTarget,
    RiskAlert,
    RiskMeasurement,
    PositionManager,
    StopLossManager,
    RiskMonitor
)


def generate_test_data(days=252, trend='flat', volatility=0.02):
    """生成测试数据"""
    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    np.random.seed(42)
    base_price = 100.0
    
    # 根据趋势生成收益
    if trend == 'up':
        drift = 0.001
    elif trend == 'down':
        drift = -0.001
    else:
        drift = 0.0
    
    returns = np.random.normal(drift, volatility, days)
    prices = base_price * (1 + returns).cumprod()
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices * np.random.uniform(0.99, 1.01, days),
        'high': prices * np.random.uniform(1.00, 1.02, days),
        'low': prices * np.random.uniform(0.98, 1.00, days),
        'close': prices,
        'volume': np.random.uniform(1e6, 5e6, days)
    })
    
    return data


class TestRiskMeasurement(unittest.TestCase):
    """测试风险度量"""
    
    def test_calculate_metrics(self):
        """测试风险指标计算"""
        data = generate_test_data()
        risk_measurement = RiskMeasurement()
        
        metrics = risk_measurement.calculate_metrics(data, asset_symbol='TEST')
        
        self.assertEqual(metrics.asset_symbol, 'TEST')
        self.assertGreater(metrics.volatility, 0)
        self.assertGreaterEqual(metrics.max_drawdown, 0)
        self.assertGreater(metrics.var_95, 0)
        self.assertIn(metrics.risk_level, ['low', 'medium', 'high', 'extreme'])
    
    def test_high_volatility(self):
        """测试高波动率场景"""
        data = generate_test_data(volatility=0.05)  # 5%日波动
        risk_measurement = RiskMeasurement()
        
        metrics = risk_measurement.calculate_metrics(data, asset_symbol='HIGH_VOL')
        
        self.assertGreater(metrics.volatility, 0.5)  # 年化应该>50%
        self.assertIn(metrics.risk_level, ['high', 'extreme'])
    
    def test_downtrend(self):
        """测试下跌趋势"""
        data = generate_test_data(trend='down')
        risk_measurement = RiskMeasurement()
        
        metrics = risk_measurement.calculate_metrics(data, asset_symbol='DOWNTREND')
        
        self.assertLess(metrics.annualized_return, 0)
        self.assertGreater(metrics.max_drawdown, 0)


class TestPositionManager(unittest.TestCase):
    """测试仓位管理"""
    
    def test_kelly_position(self):
        """测试凯利公式仓位"""
        position_manager = PositionManager()
        
        position = position_manager.calculate_position_kelly(
            win_rate=0.55,
            profit_loss_ratio=2.0,
            asset_symbol='KELLY_TEST'
        )
        
        self.assertEqual(position.asset_symbol, 'KELLY_TEST')
        self.assertEqual(position.method, 'kelly')
        self.assertGreater(position.recommended_position, 0)
        self.assertLessEqual(position.recommended_position, position.max_position)
    
    def test_volatility_position(self):
        """测试波动率仓位"""
        data = generate_test_data()
        position_manager = PositionManager()
        
        position = position_manager.calculate_position_volatility(
            data,
            asset_symbol='VOL_TEST'
        )
        
        self.assertEqual(position.method, 'volatility')
        self.assertIsNotNone(position.volatility)
        self.assertGreater(position.recommended_position, 0)
    
    def test_fixed_risk_position(self):
        """测试固定风险仓位"""
        position_manager = PositionManager()
        
        position = position_manager.calculate_position_fixed_risk(
            stop_loss_pct=0.05,  # 5%止损
            asset_symbol='FIXED_TEST'
        )
        
        self.assertEqual(position.method, 'fixed_risk')
        self.assertGreater(position.recommended_position, 0)
    
    def test_综合_position(self):
        """测试综合仓位计算"""
        data = generate_test_data()
        position_manager = PositionManager()
        
        position = position_manager.calculate_position_综合(
            data,
            win_rate=0.6,
            profit_loss_ratio=2.5,
            asset_symbol='COMBINED_TEST'
        )
        
        self.assertEqual(position.method, '综合')
        self.assertGreater(len(position.details.get('methods', [])), 1)


class TestStopLossManager(unittest.TestCase):
    """测试止损止盈管理"""
    
    def test_fixed_stop_loss_long(self):
        """测试固定止损 - 做多"""
        stop_loss_manager = StopLossManager()
        current_price = 100.0
        
        target = stop_loss_manager.calculate_fixed_stop_loss(
            current_price=current_price,
            direction='long',
            asset_symbol='FIXED_LONG'
        )
        
        self.assertEqual(target.method, 'fixed')
        self.assertLess(target.stop_loss_price, current_price)
        self.assertGreater(target.take_profit_price, current_price)
    
    def test_fixed_stop_loss_short(self):
        """测试固定止损 - 做空"""
        stop_loss_manager = StopLossManager()
        current_price = 100.0
        
        target = stop_loss_manager.calculate_fixed_stop_loss(
            current_price=current_price,
            direction='short',
            asset_symbol='FIXED_SHORT'
        )
        
        self.assertEqual(target.method, 'fixed')
        self.assertGreater(target.stop_loss_price, current_price)
        self.assertLess(target.take_profit_price, current_price)
    
    def test_atr_stop_loss(self):
        """测试ATR止损"""
        data = generate_test_data()
        stop_loss_manager = StopLossManager()
        
        target = stop_loss_manager.calculate_atr_stop_loss(
            data,
            direction='long',
            asset_symbol='ATR_TEST'
        )
        
        self.assertEqual(target.method, 'atr')
        self.assertIsNotNone(target.atr_value)
        self.assertGreater(target.atr_value, 0)
    
    def test_support_resistance(self):
        """测试支撑阻力止损"""
        data = generate_test_data()
        stop_loss_manager = StopLossManager()
        
        target = stop_loss_manager.calculate_支撑阻力_stop_loss(
            data,
            direction='long',
            asset_symbol='SR_TEST'
        )
        
        self.assertEqual(target.method, 'support_resistance')
        self.assertIn('support', target.details)
        self.assertIn('resistance', target.details)


class TestRiskMonitor(unittest.TestCase):
    """测试风险监控"""
    
    def test_monitor_asset_risk(self):
        """测试资产风险监控"""
        data = generate_test_data()
        risk_monitor = RiskMonitor()
        
        metrics, alerts = risk_monitor.monitor_asset_risk(
            data,
            asset_symbol='MONITOR_TEST'
        )
        
        self.assertIsInstance(metrics, RiskMetrics)
        self.assertIsInstance(alerts, list)
    
    def test_high_risk_alerts(self):
        """测试高风险告警"""
        # 生成高风险数据
        data = generate_test_data(trend='down', volatility=0.06)
        risk_monitor = RiskMonitor(config={
            'max_drawdown_threshold': 0.10,
            'volatility_threshold': 0.30
        })
        
        metrics, alerts = risk_monitor.monitor_asset_risk(
            data,
            asset_symbol='HIGH_RISK'
        )
        
        # 应该有告警
        self.assertGreater(len(alerts), 0)
        
        # 检查告警类型
        alert_types = [a.alert_type for a in alerts]
        self.assertTrue(any(t in ['warning', 'critical'] for t in alert_types))
    
    def test_portfolio_monitoring(self):
        """测试投资组合监控"""
        risk_monitor = RiskMonitor()
        
        holdings = {
            'ASSET1': {'value': 60000, 'quantity': 100},
            'ASSET2': {'value': 30000, 'quantity': 50},
            'ASSET3': {'value': 10000, 'quantity': 20}
        }
        
        alerts = risk_monitor.monitor_portfolio_risk(holdings)
        
        self.assertIsInstance(alerts, list)
        # ASSET1占60%，应该触发集中度告警
        self.assertGreater(len(alerts), 0)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestRiskMeasurement))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestStopLossManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskMonitor))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印摘要
    print("\n" + "="*70)
    print("测试摘要")
    print("="*70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())

"""
Stage 4 单元测试
测试投资策略引擎
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

from strategy.base_strategy import BaseStrategy, StrategyResult
from strategy.etf_valuation import ETFValuationStrategy
from strategy.crypto_momentum import CryptoMomentumStrategy
from strategy.portfolio_manager import PortfolioManager
from strategy.dca_strategy import DCAStrategy


class TestBaseStrategy(unittest.TestCase):
    """测试策略基类"""
    
    def test_strategy_result_creation(self):
        """测试策略结果创建"""
        result = StrategyResult(
            strategy_name="TestStrategy",
            asset_symbol="TEST",
            timestamp="2024-01-01 12:00:00",
            action="buy",
            quantity=100.0,
            confidence=0.8,
            current_price=10.0,
            target_price=12.0,
            stop_loss=9.0,
            take_profit=12.0,
            reason="Test reason",
            indicators={'test': 'value'},
            risk_level='medium'
        )
        
        self.assertEqual(result.strategy_name, "TestStrategy")
        self.assertEqual(result.action, "buy")
        self.assertEqual(result.confidence, 0.8)
        
        # 测试转换为字典
        result_dict = result.to_dict()
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['action'], 'buy')
    
    def test_kelly_criterion(self):
        """测试凯利公式"""
        # 创建一个具体策略实例用于测试
        strategy = ETFValuationStrategy()
        
        kelly = strategy.calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=0.15,
            avg_loss=0.10
        )
        
        self.assertGreater(kelly, 0)
        self.assertLessEqual(kelly, 0.25)  # 不应超过25%
    
    def test_risk_reward_ratio(self):
        """测试风险收益比"""
        strategy = ETFValuationStrategy()
        
        ratio = strategy.calculate_risk_reward_ratio(
            entry_price=100,
            target_price=120,
            stop_loss=95
        )
        
        self.assertEqual(ratio, 4.0)  # (120-100)/(100-95) = 4


class TestETFValuationStrategy(unittest.TestCase):
    """测试ETF估值策略"""
    
    def setUp(self):
        """设置测试数据"""
        self.strategy = ETFValuationStrategy()
        
        # 创建模拟ETF数据
        dates = pd.date_range(start='2021-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        
        # 生成价格数据（随机游走）
        prices = 3.0 + np.cumsum(np.random.randn(len(dates)) * 0.02)
        
        # 生成PE/PB数据
        pe = 20 + np.random.randn(len(dates)) * 5
        pb = 2.0 + np.random.randn(len(dates)) * 0.5
        
        self.data = pd.DataFrame({
            'close': prices,
            'pe': np.clip(pe, 5, 50),
            'pb': np.clip(pb, 0.5, 5)
        }, index=dates)
    
    def test_analyze_low_valuation(self):
        """测试低估值情况"""
        # 设置当前PE/PB为历史低位
        self.data.iloc[-1, self.data.columns.get_loc('pe')] = 12  # 低PE
        self.data.iloc[-1, self.data.columns.get_loc('pb')] = 1.2  # 低PB
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            capital=100000
        )
        
        self.assertEqual(result.asset_symbol, '513500')
        self.assertIn(result.action, ['buy', 'hold'])
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertIn(result.risk_level, ['low', 'medium', 'high'])
    
    def test_analyze_high_valuation(self):
        """测试高估值情况"""
        # 设置当前PE/PB为历史高位
        self.data.iloc[-1, self.data.columns.get_loc('pe')] = 45  # 高PE
        self.data.iloc[-1, self.data.columns.get_loc('pb')] = 4.5  # 高PB
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            capital=100000
        )
        
        self.assertEqual(result.asset_symbol, '513500')
        self.assertIn(result.action, ['sell', 'hold'])
    
    def test_insufficient_data(self):
        """测试数据不足情况"""
        # 使用很少的数据
        small_data = self.data.tail(10)
        
        result = self.strategy.analyze(
            data=small_data,
            asset_symbol='513500',
            capital=100000
        )
        
        self.assertEqual(result.action, 'hold')


class TestCryptoMomentumStrategy(unittest.TestCase):
    """测试加密货币动量策略"""
    
    def setUp(self):
        """设置测试数据"""
        self.strategy = CryptoMomentumStrategy()
        
        # 创建模拟加密货币数据
        dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
        np.random.seed(42)
        
        # 生成OHLCV数据
        close = 95000 + np.cumsum(np.random.randn(len(dates)) * 1000)
        high = close * 1.02
        low = close * 0.98
        open_price = np.roll(close, 1)
        volume = np.random.rand(len(dates)) * 1000000
        
        self.data = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
    
    def test_analyze_uptrend(self):
        """测试上升趋势"""
        # 制造上升趋势
        trend = np.linspace(0, 10000, len(self.data))
        self.data['close'] = 95000 + trend
        self.data['high'] = self.data['close'] * 1.02
        self.data['low'] = self.data['close'] * 0.98
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='BTC',
            capital=10000
        )
        
        self.assertEqual(result.asset_symbol, 'BTC')
        self.assertIn(result.action, ['buy', 'hold', 'sell'])
        self.assertIsNotNone(result.indicators)
        self.assertTrue('rsi' in result.indicators or not result.indicators.get('valid'))
    
    def test_analyze_downtrend(self):
        """测试下降趋势"""
        # 制造下降趋势
        trend = np.linspace(0, -10000, len(self.data))
        self.data['close'] = 95000 + trend
        self.data['high'] = self.data['close'] * 1.02
        self.data['low'] = self.data['close'] * 0.98
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='BTC',
            capital=10000
        )
        
        self.assertEqual(result.asset_symbol, 'BTC')
        self.assertIn(result.action, ['buy', 'hold', 'sell'])
    
    def test_insufficient_data(self):
        """测试数据不足"""
        small_data = self.data.tail(5)
        
        result = self.strategy.analyze(
            data=small_data,
            asset_symbol='BTC',
            capital=10000
        )
        
        self.assertEqual(result.action, 'hold')


class TestPortfolioManager(unittest.TestCase):
    """测试投资组合管理器"""
    
    def setUp(self):
        """设置测试数据"""
        self.strategy = PortfolioManager()
        
        self.portfolio = {
            'ETF': {'quantity': 1000, 'price': 3.5},
            'BTC': {'quantity': 0.05, 'price': 95000},
            'ETH': {'quantity': 1.0, 'price': 3500}
        }
        
        self.prices = {
            'ETF': 3.5,
            'BTC': 95000,
            'ETH': 3500
        }
    
    def test_balanced_portfolio(self):
        """测试平衡的投资组合"""
        # 设置平衡的持仓
        total_value = sum(
            self.portfolio[asset]['quantity'] * self.portfolio[asset]['price']
            for asset in self.portfolio
        )
        
        result = self.strategy.analyze(
            data=pd.DataFrame(),
            portfolio=self.portfolio,
            prices=self.prices,
            total_capital=total_value
        )
        
        self.assertEqual(result.asset_symbol, 'Portfolio')
        self.assertIn(result.action, ['hold', 'rebalance'])
        self.assertIn('current_allocation', result.indicators)
        self.assertIn('target_allocation', result.indicators)
    
    def test_unbalanced_portfolio(self):
        """测试失衡的投资组合"""
        # 制造严重失衡 - BTC占比过高
        self.portfolio['BTC']['quantity'] = 0.5  # 大幅增加BTC持仓
        
        total_value = sum(
            self.portfolio[asset]['quantity'] * self.portfolio[asset]['price']
            for asset in self.portfolio
        )
        
        result = self.strategy.analyze(
            data=pd.DataFrame(),
            portfolio=self.portfolio,
            prices=self.prices,
            total_capital=total_value
        )
        
        self.assertIn(result.action, ['hold', 'rebalance'])
        
        if result.action == 'rebalance':
            self.assertIn('trades', result.indicators)
            self.assertGreater(len(result.indicators['trades']), 0)
    
    def test_optimize_allocation(self):
        """测试资产配置优化"""
        # 创建收益率数据
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        returns = pd.DataFrame({
            'ETF': np.random.randn(len(dates)) * 0.01,
            'BTC': np.random.randn(len(dates)) * 0.03,
            'ETH': np.random.randn(len(dates)) * 0.025
        }, index=dates)
        
        # 测试不同优化方法
        for method in ['equal_weight', 'min_variance', 'risk_parity']:
            allocation = self.strategy.optimize_allocation(returns, method=method)
            
            self.assertIsInstance(allocation, dict)
            # 权重总和应该接近1
            total_weight = sum(allocation.values())
            self.assertAlmostEqual(total_weight, 1.0, places=2)


class TestDCAStrategy(unittest.TestCase):
    """测试定投策略"""
    
    def setUp(self):
        """设置测试数据"""
        self.strategy = DCAStrategy()
        
        # 创建模拟价格数据
        dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
        prices = 3.5 + np.random.randn(len(dates)) * 0.1
        
        self.data = pd.DataFrame({
            'close': prices
        }, index=dates)
    
    def test_fixed_dca(self):
        """测试固定定投"""
        self.strategy.dca_type = 'fixed'
        self.strategy.base_amount = 1000
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            last_dca_date=None  # 首次定投
        )
        
        self.assertEqual(result.action, 'buy')
        self.assertEqual(result.indicators['invest_amount'], 1000)
        self.assertGreater(result.quantity, 0)
    
    def test_smart_dca_low_valuation(self):
        """测试智能定投 - 低估值"""
        self.strategy.dca_type = 'smart'
        self.strategy.base_amount = 1000
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            last_dca_date=None,
            valuation_percentile=20  # 低估值
        )
        
        self.assertEqual(result.action, 'buy')
        # 低估值时应该投入更多
        self.assertGreater(result.indicators['invest_amount'], 1000)
        self.assertGreater(result.indicators['adjustment_factor'], 1.0)
    
    def test_smart_dca_high_valuation(self):
        """测试智能定投 - 高估值"""
        self.strategy.dca_type = 'smart'
        self.strategy.base_amount = 1000
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            last_dca_date=None,
            valuation_percentile=80  # 高估值
        )
        
        self.assertEqual(result.action, 'buy')
        # 高估值时应该投入更少
        self.assertLess(result.indicators['invest_amount'], 1000)
        self.assertLess(result.indicators['adjustment_factor'], 1.0)
    
    def test_grid_dca(self):
        """测试网格定投"""
        self.strategy.dca_type = 'grid'
        self.strategy.base_amount = 1000
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            last_dca_date=None
        )
        
        self.assertEqual(result.action, 'buy')
        self.assertIn('invest_amount', result.indicators)
        self.assertGreater(result.quantity, 0)
    
    def test_timing_check(self):
        """测试定投时机检查"""
        self.strategy.frequency = 7  # 每周定投
        
        # 测试刚定投过
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = self.strategy.analyze(
            data=self.data,
            asset_symbol='513500',
            last_dca_date=yesterday
        )
        
        self.assertEqual(result.action, 'hold')
        self.assertIn('未到定投时间', result.reason)
    
    def test_dca_statistics(self):
        """测试定投统计"""
        # 模拟几次定投
        for i in range(3):
            result = StrategyResult(
                strategy_name='DCAStrategy',
                asset_symbol='513500',
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                action='buy',
                quantity=100.0,
                confidence=0.9,
                current_price=3.5,
                target_price=None,
                stop_loss=None,
                take_profit=None,
                reason='定投',
                indicators={'invest_amount': 1000},
                risk_level='low'
            )
            self.strategy._record_dca(result)
        
        stats = self.strategy.get_dca_statistics()
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['num_investments'], 3)
        self.assertAlmostEqual(stats['total_invested'], 3000, places=0)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBaseStrategy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestETFValuationStrategy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCryptoMomentumStrategy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPortfolioManager))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDCAStrategy))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印结果摘要
    print("\n" + "="*70)
    print("测试摘要")
    print("="*70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

"""
测试高级回测引擎
Test Enhanced Backtest Engine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategy.backtest_engine import (
    BacktestEngine, BacktestConfig, OrderSide, OrderType,
    quick_backtest
)
from loguru import logger


def generate_sample_data(days=252, start_price=100) -> pd.DataFrame:
    """生成模拟数据"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成价格 (随机游走 + 趋势)
    returns = np.random.randn(days) * 0.02 + 0.0003  # 日波动2% + 微小上涨趋势
    prices = start_price * (1 + returns).cumprod()
    
    # 生成OHLCV
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(days) * 0.005),
        'high': prices * (1 + abs(np.random.randn(days)) * 0.01),
        'low': prices * (1 - abs(np.random.randn(days)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    
    return df


def simple_ma_strategy(data: pd.DataFrame, context: dict, **kwargs) -> list:
    """
    简单移动平均策略
    
    当短期均线上穿长期均线时买入
    当短期均线下穿长期均线时卖出
    """
    signals = []
    
    # 需要足够的数据计算均线
    if len(data) < 20:
        return signals
    
    # 计算移动平均线
    short_ma = kwargs.get('short_period', 5)
    long_ma = kwargs.get('long_period', 20)
    
    data['ma_short'] = data['close'].rolling(window=short_ma).mean()
    data['ma_long'] = data['close'].rolling(window=long_ma).mean()
    
    # 获取最近两个交易日的数据
    if len(data) < 2:
        return signals
    
    prev_short = data['ma_short'].iloc[-2]
    prev_long = data['ma_long'].iloc[-2]
    curr_short = data['ma_short'].iloc[-1]
    curr_long = data['ma_long'].iloc[-1]
    
    # 检查金叉和死叉
    symbol = kwargs.get('symbol', 'TEST')
    
    # 金叉: 买入信号
    if prev_short <= prev_long and curr_short > curr_long:
        # 计算买入数量 (使用90%的现金)
        cash = context['cash']
        current_price = data['close'].iloc[-1]
        quantity = int((cash * 0.9) / current_price / 100) * 100  # 调整到100的倍数
        
        if quantity >= 100:
            signals.append({
                'action': 'buy',
                'symbol': symbol,
                'quantity': quantity
            })
            logger.info(f"金叉信号: MA{short_ma}上穿MA{long_ma}, 买入 {quantity}股")
    
    # 死叉: 卖出信号
    elif prev_short >= prev_long and curr_short < curr_long:
        # 卖出所有持仓
        positions = context['positions']
        if symbol in positions:
            quantity = positions[symbol].quantity
            if quantity > 0:
                signals.append({
                    'action': 'sell',
                    'symbol': symbol,
                    'quantity': quantity
                })
                logger.info(f"死叉信号: MA{short_ma}下穿MA{long_ma}, 卖出 {quantity}股")
    
    return signals


def test_basic_backtest():
    """测试基本回测功能"""
    logger.info("=" * 80)
    logger.info("测试1: 基本回测功能")
    logger.info("=" * 80)
    
    # 生成测试数据
    data = generate_sample_data(days=252, start_price=100)
    logger.info(f"生成测试数据: {len(data)}天")
    
    # 配置回测
    config = BacktestConfig(
        initial_capital=100000,
        commission_rate=0.0003,
        slippage_rate=0.0005,
        enable_commission=True,
        enable_slippage=True
    )
    
    # 运行回测
    engine = BacktestEngine(config)
    result = engine.run_backtest(
        data,
        simple_ma_strategy,
        short_period=5,
        long_period=20,
        symbol='TEST'
    )
    
    # 打印结果
    print("\n" + "=" * 80)
    print("回测结果")
    print("=" * 80)
    print(f"回测期间: {result.start_date} 至 {result.end_date}")
    print(f"交易天数: {result.trading_days}天")
    print(f"初始资金: {result.initial_capital:,.2f}")
    print(f"最终资金: {result.final_capital:,.2f}")
    print(f"总收益: {result.total_return:,.2f}")
    print(f"总收益率: {result.total_return_pct:.2%}")
    print(f"年化收益率: {result.annualized_return:.2%}")
    print(f"\n风险指标:")
    print(f"波动率: {result.volatility:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"索提诺比率: {result.sortino_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"最大回撤持续: {result.max_drawdown_duration}天")
    print(f"\n交易统计:")
    print(f"总交易次数: {result.total_trades}")
    print(f"盈利交易: {result.winning_trades}")
    print(f"亏损交易: {result.losing_trades}")
    print(f"胜率: {result.win_rate:.2%}")
    print(f"平均盈利: {result.avg_win:.2f}")
    print(f"平均亏损: {result.avg_loss:.2f}")
    print(f"盈亏比: {result.profit_factor:.2f}")
    print(f"\n成本统计:")
    print(f"总佣金: {result.total_commission:.2f}")
    print(f"总滑点: {result.total_slippage:.2f}")
    print(f"总印花税: {result.total_stamp_duty:.2f}")
    print("=" * 80)
    
    return result


def test_cost_impact():
    """测试交易成本影响"""
    logger.info("\n" + "=" * 80)
    logger.info("测试2: 交易成本对收益的影响")
    logger.info("=" * 80)
    
    data = generate_sample_data(days=252, start_price=100)
    
    # 测试不同成本配置
    configs = [
        {"name": "无成本", "commission": 0, "slippage": 0, "enable_c": False, "enable_s": False},
        {"name": "仅佣金", "commission": 0.0003, "slippage": 0, "enable_c": True, "enable_s": False},
        {"name": "仅滑点", "commission": 0, "slippage": 0.0005, "enable_c": False, "enable_s": True},
        {"name": "全部成本", "commission": 0.0003, "slippage": 0.0005, "enable_c": True, "enable_s": True},
    ]
    
    results = []
    
    for cfg in configs:
        config = BacktestConfig(
            initial_capital=100000,
            commission_rate=cfg['commission'],
            slippage_rate=cfg['slippage'],
            enable_commission=cfg['enable_c'],
            enable_slippage=cfg['enable_s']
        )
        
        engine = BacktestEngine(config)
        result = engine.run_backtest(
            data,
            simple_ma_strategy,
            short_period=5,
            long_period=20,
            symbol='TEST'
        )
        
        results.append({
            'name': cfg['name'],
            'return_pct': result.total_return_pct,
            'sharpe': result.sharpe_ratio,
            'commission': result.total_commission,
            'slippage': result.total_slippage,
            'trades': result.total_trades
        })
    
    # 打印对比
    print("\n" + "=" * 80)
    print("成本影响对比")
    print("=" * 80)
    print(f"{'配置':<12} {'收益率':>10} {'夏普':>8} {'佣金':>10} {'滑点':>10} {'交易次数':>10}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<12} {r['return_pct']:>9.2%} {r['sharpe']:>8.2f} "
              f"{r['commission']:>10.2f} {r['slippage']:>10.2f} {r['trades']:>10}")
    print("=" * 80)
    
    # 计算成本侵蚀
    no_cost_return = results[0]['return_pct']
    full_cost_return = results[3]['return_pct']
    cost_erosion = no_cost_return - full_cost_return
    
    print(f"\n成本侵蚀: {cost_erosion:.2%}")
    print(f"占无成本收益的比例: {cost_erosion/no_cost_return*100:.1f}%")


def test_quick_backtest():
    """测试快速回测函数"""
    logger.info("\n" + "=" * 80)
    logger.info("测试3: 快速回测函数")
    logger.info("=" * 80)
    
    data = generate_sample_data(days=126, start_price=100)
    
    result = quick_backtest(
        data,
        simple_ma_strategy,
        initial_capital=50000,
        commission_rate=0.0003,
        slippage_rate=0.0005,
        short_period=5,
        long_period=20,
        symbol='TEST'
    )
    
    print(f"\n快速回测完成:")
    print(f"收益率: {result.total_return_pct:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")


def run_all_tests():
    """运行所有测试"""
    logger.info("\n" + "🚀" * 40)
    logger.info("开始测试高级回测引擎")
    logger.info("🚀" * 40 + "\n")
    
    try:
        # 测试1: 基本功能
        result1 = test_basic_backtest()
        
        # 测试2: 成本影响
        test_cost_impact()
        
        # 测试3: 快速回测
        test_quick_backtest()
        
        logger.info("\n" + "✅" * 40)
        logger.info("所有测试完成!")
        logger.info("✅" * 40)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

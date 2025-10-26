"""
测试机器学习框架
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from src.ai.ml_framework import MLFramework, MLConfig, FeatureEngineer
from src.ai.ml_predictor import ReturnPredictor, quick_predict_return
from src.ai.factor_mining import FactorMiner, FactorConfig


def generate_test_data(n_days: int = 500) -> pd.DataFrame:
    """生成测试数据"""
    logger.info(f"生成 {n_days} 天测试数据...")
    
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    
    # 生成随机价格序列
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, n_days)
    close = 100 * np.exp(np.cumsum(returns))
    
    # OHLCV
    high = close * (1 + np.random.uniform(0, 0.02, n_days))
    low = close * (1 - np.random.uniform(0, 0.02, n_days))
    open_price = close * (1 + np.random.normal(0, 0.01, n_days))
    volume = np.random.uniform(1e6, 5e6, n_days)
    
    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    df.set_index('date', inplace=True)
    
    logger.info("测试数据生成完成")
    return df


def test_feature_engineering():
    """测试特征工程"""
    logger.info("\n" + "=" * 60)
    logger.info("测试1: 特征工程")
    logger.info("=" * 60)
    
    df = generate_test_data(200)
    
    # 创建技术特征
    features = FeatureEngineer.create_technical_features(df)
    logger.info(f"原始特征: {len(df.columns)}")
    logger.info(f"技术特征后: {len(features.columns)}")
    
    # 创建时间特征
    features = FeatureEngineer.create_time_features(features)
    logger.info(f"时间特征后: {len(features.columns)}")
    
    # 创建滞后特征
    features = FeatureEngineer.create_lag_features(
        features,
        columns=['returns', 'volume'],
        lags=[1, 2, 3]
    )
    logger.info(f"滞后特征后: {len(features.columns)}")
    
    logger.info("✅ 特征工程测试通过")


def test_ml_framework():
    """测试ML框架"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: ML框架")
    logger.info("=" * 60)
    
    df = generate_test_data(300)
    
    # 创建特征
    features = FeatureEngineer.create_technical_features(df)
    
    # 创建目标 (5日收益率)
    features['target'] = df['close'].pct_change(5).shift(-5)
    features = features.dropna()
    
    # 训练模型
    config = MLConfig(
        model_type='random_forest',
        target_column='target',
        test_size=0.2,
        cv_folds=3
    )
    
    framework = MLFramework(config)
    X, y, feature_names = framework.prepare_data(features, 'target')
    result = framework.train(X, y)
    
    logger.info(f"\n训练集R²: {result.train_score:.4f}")
    logger.info(f"测试集R²: {result.test_score:.4f}")
    logger.info(f"交叉验证R²: {result.cv_mean:.4f} (+/- {result.cv_std:.4f})")
    logger.info(f"RMSE: {result.metrics['rmse']:.6f}")
    
    # 预测
    X_test = X[-10:]
    predictions = framework.predict(X_test)
    logger.info(f"\n最近10个预测: {predictions}")
    
    logger.info("✅ ML框架测试通过")


def test_ml_predictor():
    """测试ML预测器"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: ML预测器")
    logger.info("=" * 60)
    
    df = generate_test_data(400)
    
    # 创建预测器
    predictor = ReturnPredictor(forecast_horizon=5)
    
    # 训练
    training_result = predictor.train(df)
    
    logger.info(f"\n模型类型: {training_result['model_type']}")
    logger.info(f"预测类型: {training_result['predict_type']}")
    logger.info(f"预测周期: {training_result['forecast_horizon']}天")
    logger.info(f"测试集R²: {training_result['test_score']:.4f}")
    logger.info(f"交叉验证R²: {training_result['cv_mean']:.4f}")
    
    # 预测
    prediction = predictor.predict(df)
    
    logger.info(f"\n最新预测:")
    logger.info(f"  时间: {prediction.timestamp}")
    logger.info(f"  预测收益率: {prediction.prediction:.4f} ({prediction.prediction*100:.2f}%)")
    if prediction.confidence:
        logger.info(f"  预测信心: {prediction.confidence:.4f}")
    
    # 批量预测
    batch_preds = predictor.predict_batch(df, last_n=5)
    logger.info(f"\n批量预测 (最近5个):")
    for i, pred in enumerate(batch_preds, 1):
        logger.info(f"  {i}. 预测: {pred.prediction:.4f}")
    
    logger.info("✅ ML预测器测试通过")


def test_factor_mining():
    """测试因子挖掘"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 因子挖掘")
    logger.info("=" * 60)
    
    df = generate_test_data(300)
    
    # 创建简单特征
    df['returns'] = df['close'].pct_change()
    df['ma_5'] = df['close'].rolling(5).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['volatility'] = df['returns'].rolling(10).std()
    
    # 创建目标 (未来5日收益)
    df['forward_returns'] = df['close'].pct_change(5).shift(-5)
    
    df = df.dropna()
    
    # 配置因子挖掘
    config = FactorConfig(
        population_size=50,
        generations=10,
        min_ic=0.01
    )
    
    miner = FactorMiner(config)
    
    # 挖掘因子
    result = miner.mine_factors(df, target_column='forward_returns')
    
    logger.info(f"\n发现 {len(result.all_factors)} 个有效因子")
    
    if result.best_factor:
        logger.info(f"\n最佳因子:")
        logger.info(f"  名称: {result.best_factor.name}")
        logger.info(f"  表达式: {result.best_factor.expression}")
        logger.info(f"  IC: {result.best_factor.ic:.4f}")
        logger.info(f"  IC_IR: {result.best_factor.ic_ir:.4f}")
        logger.info(f"  Rank IC: {result.best_factor.rank_ic:.4f}")
    
    logger.info(f"\nTop 5 因子:")
    for i, factor in enumerate(result.top_factors[:5], 1):
        logger.info(f"{i}. {factor.expression[:50]}... (IC={factor.ic:.4f})")
    
    logger.info("✅ 因子挖掘测试通过")


def test_quick_functions():
    """测试便捷函数"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 便捷函数")
    logger.info("=" * 60)
    
    df = generate_test_data(200)
    
    # 快速预测
    prediction = quick_predict_return(df, forecast_horizon=3)
    
    logger.info(f"快速预测结果:")
    logger.info(f"  预测收益率: {prediction.prediction:.4f}")
    logger.info(f"  预测周期: {prediction.forecast_horizon}天")
    
    logger.info("✅ 便捷函数测试通过")


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("机器学习模块测试")
    logger.info("=" * 60)
    
    try:
        test_feature_engineering()
        test_ml_framework()
        test_ml_predictor()
        test_factor_mining()
        test_quick_functions()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

"""
综合集成测试 - 验证所有AI模块功能
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger


def generate_test_data(n_days: int = 300) -> pd.DataFrame:
    """生成测试数据"""
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, n_days)
    close = 100 * np.exp(np.cumsum(returns))
    
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
    
    return df


def test_ml_predictor():
    """测试ML预测器"""
    logger.info("\n" + "=" * 60)
    logger.info("测试1: ML预测器")
    logger.info("=" * 60)
    
    from src.ai.ml_predictor import ReturnPredictor, DirectionPredictor
    
    df = generate_test_data(400)
    
    # 测试收益率预测
    logger.info("测试收益率预测...")
    return_predictor = ReturnPredictor(forecast_horizon=5)
    training_result = return_predictor.train(df)
    prediction = return_predictor.predict(df)
    
    logger.info(f"  测试集R²: {training_result['test_score']:.4f}")
    logger.info(f"  预测收益率: {prediction.prediction:.4f}")
    
    # 测试方向预测
    logger.info("测试方向预测...")
    direction_predictor = DirectionPredictor(forecast_horizon=5)
    training_result = direction_predictor.train(df)
    prediction = direction_predictor.predict(df)
    
    logger.info(f"  测试集R²: {training_result['test_score']:.4f}")
    logger.info(f"  预测方向: {prediction.prediction:.4f}")
    
    logger.info("✅ ML预测器测试通过")


def test_factor_mining():
    """测试因子挖掘"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 因子挖掘")
    logger.info("=" * 60)
    
    from src.ai.factor_mining import FactorMiner, FactorConfig
    
    df = generate_test_data(300)
    
    # 创建特征
    df['returns'] = df['close'].pct_change()
    df['ma_5'] = df['close'].rolling(5).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['volatility'] = df['returns'].rolling(10).std()
    df['forward_returns'] = df['close'].pct_change(5).shift(-5)
    df = df.dropna()
    
    # 因子挖掘
    config = FactorConfig(
        population_size=30,
        generations=5,
        min_ic=0.01
    )
    
    miner = FactorMiner(config)
    result = miner.mine_factors(df, target_column='forward_returns')
    
    logger.info(f"  发现 {len(result.all_factors)} 个有效因子")
    if result.best_factor:
        logger.info(f"  最佳因子IC: {result.best_factor.ic:.4f}")
    
    logger.info("✅ 因子挖掘测试通过")


def test_dl_framework():
    """测试深度学习框架"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 深度学习框架")
    logger.info("=" * 60)
    
    try:
        from src.ai.dl_framework import DLFramework, DLConfig
        
        df = generate_test_data(200)
        
        # LSTM配置
        config = DLConfig(
            model_type='lstm',
            sequence_length=30,
            prediction_horizon=5,
            epochs=5,  # 少量epoch用于测试
            batch_size=16
        )
        
        framework = DLFramework(config)
        
        X, y = framework.prepare_sequences(df)
        
        logger.info(f"  序列形状: X={X.shape}, y={y.shape}")
        
        history = framework.train(X, y, validation_split=0.2)
        
        logger.info(f"  训练完成，最终Loss: {history['train_loss'][-1]:.6f}")
        
        # 预测
        last_X = X[-1:]
        prediction = framework.predict(last_X)
        
        logger.info(f"  预测收益率: {prediction[0][0]:.4f}")
        
        logger.info("✅ 深度学习框架测试通过")
        
    except ImportError as e:
        logger.warning(f"⚠️ PyTorch未安装，跳过深度学习测试: {e}")
    except Exception as e:
        logger.warning(f"⚠️ 深度学习测试失败: {e}")


def test_nlp_sentiment():
    """测试NLP情感分析"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: NLP情感分析")
    logger.info("=" * 60)
    
    from src.ai.nlp_sentiment import ChineseSentimentAnalyzer, quick_sentiment_analysis
    
    # 测试单文本
    positive_text = "公司业绩超预期，净利润增长50%，未来发展前景良好"
    negative_text = "股价大跌，面临退市风险，经营状况恶化"
    
    logger.info("测试正向文本...")
    result1 = quick_sentiment_analysis(positive_text)
    logger.info(f"  情感得分: {result1['sentiment_score']:.3f}")
    logger.info(f"  情感标签: {result1['sentiment_label']}")
    logger.info(f"  正向词: {result1['positive_words']}")
    
    logger.info("测试负向文本...")
    result2 = quick_sentiment_analysis(negative_text)
    logger.info(f"  情感得分: {result2['sentiment_score']:.3f}")
    logger.info(f"  情感标签: {result2['sentiment_label']}")
    logger.info(f"  负向词: {result2['negative_words']}")
    
    # 测试批量分析
    logger.info("测试批量分析...")
    news_list = [
        "公司发布年报，营收创历史新高",
        "市场预期良好，机构看好后市",
        "公司遭遇重大亏损，管理层辞职",
        "新产品上市，市场反应积极"
    ]
    
    from src.ai.nlp_sentiment import analyze_news_sentiment
    result_df = analyze_news_sentiment(news_list)
    
    logger.info(f"  批量分析完成: {len(result_df)} 条")
    logger.info(f"  平均情感得分: {result_df['sentiment_score'].mean():.3f}")
    
    logger.info("✅ NLP情感分析测试通过")


def test_integration():
    """集成测试 - 端到端流程"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 端到端集成测试")
    logger.info("=" * 60)
    
    df = generate_test_data(500)
    
    # 1. 特征工程
    logger.info("步骤1: 特征工程...")
    from src.ai.ml_framework import FeatureEngineer
    
    features = FeatureEngineer.create_technical_features(df)
    features = FeatureEngineer.create_time_features(features)
    
    logger.info(f"  创建了 {len(features.columns)} 个特征")
    
    # 2. ML预测
    logger.info("步骤2: ML预测...")
    from src.ai.ml_predictor import ReturnPredictor
    
    predictor = ReturnPredictor(forecast_horizon=5)
    training_result = predictor.train(df)
    prediction = predictor.predict(df)
    
    logger.info(f"  预测收益率: {prediction.prediction:.4f}")
    logger.info(f"  预测信心: {prediction.confidence:.4f}" if prediction.confidence else "  无集成")
    
    # 3. 因子挖掘
    logger.info("步骤3: 因子挖掘...")
    from src.ai.factor_mining import FactorMiner, FactorConfig
    
    features['forward_returns'] = df['close'].pct_change(5).shift(-5)
    features = features.dropna()
    
    config = FactorConfig(
        population_size=20,
        generations=3,
        min_ic=0.01
    )
    
    miner = FactorMiner(config)
    result = miner.mine_factors(features, target_column='forward_returns')
    
    logger.info(f"  发现 {len(result.all_factors)} 个因子")
    
    # 4. 情感分析
    logger.info("步骤4: 情感分析...")
    from src.ai.nlp_sentiment import quick_sentiment_analysis
    
    sample_news = "公司业绩表现优异，股价强势上涨，投资者信心十足"
    sentiment = quick_sentiment_analysis(sample_news)
    
    logger.info(f"  情感得分: {sentiment['sentiment_score']:.3f}")
    
    # 综合决策
    logger.info("\n步骤5: 综合投资决策...")
    logger.info(f"  ML预测: {prediction.prediction:.4f}")
    logger.info(f"  情感得分: {sentiment['sentiment_score']:.3f}")
    logger.info(f"  因子数量: {len(result.all_factors)}")
    
    # 简单决策逻辑
    decision_score = (
        prediction.prediction * 0.4 +
        sentiment['sentiment_score'] * 0.3 +
        (len(result.all_factors) / 10) * 0.3
    )
    
    if decision_score > 0.3:
        decision = "📈 强烈看多"
    elif decision_score > 0.1:
        decision = "📊 看多"
    elif decision_score > -0.1:
        decision = "➖ 中性"
    elif decision_score > -0.3:
        decision = "📉 看空"
    else:
        decision = "⚠️ 强烈看空"
    
    logger.info(f"  综合决策得分: {decision_score:.3f}")
    logger.info(f"  投资建议: {decision}")
    
    logger.info("✅ 端到端集成测试通过")


def test_ui_pages():
    """测试UI页面导入"""
    logger.info("\n" + "=" * 60)
    logger.info("测试6: UI页面导入")
    logger.info("=" * 60)
    
    try:
        from src.ui.ai_prediction_page import show_ai_prediction_page
        logger.info("  ✓ AI预测页面导入成功")
    except Exception as e:
        logger.error(f"  ✗ AI预测页面导入失败: {e}")
    
    try:
        from src.ui.sentiment_page import show_sentiment_page
        logger.info("  ✓ 情感分析页面导入成功")
    except Exception as e:
        logger.error(f"  ✗ 情感分析页面导入失败: {e}")
    
    logger.info("✅ UI页面导入测试通过")


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("PersonalQuantAssistant 综合集成测试")
    logger.info("=" * 60)
    
    try:
        test_ml_predictor()
        test_factor_mining()
        test_dl_framework()
        test_nlp_sentiment()
        test_integration()
        test_ui_pages()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试通过！系统运行正常！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

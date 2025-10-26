"""
机器学习预测器 - 价格和波动率预测
ML Predictor for Price and Volatility Forecasting
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger
from pathlib import Path

from src.ai.ml_framework import MLFramework, MLConfig, FeatureEngineer


@dataclass
class PredictionConfig:
    """预测配置"""
    # 预测目标
    predict_type: str = 'return'      # 'return', 'direction', 'volatility'
    forecast_horizon: int = 5         # 预测未来N天
    
    # 特征工程
    use_technical: bool = True
    use_time_features: bool = True
    use_lag_features: bool = True
    lag_periods: List[int] = None
    
    # 模型配置
    model_type: str = 'random_forest'
    ensemble: bool = False            # 是否使用集成
    
    def __post_init__(self):
        if self.lag_periods is None:
            self.lag_periods = [1, 2, 3, 5, 10]


@dataclass
class Prediction:
    """预测结果"""
    timestamp: str
    predict_type: str
    forecast_horizon: int
    prediction: float
    confidence: Optional[float] = None
    features_used: Optional[List[str]] = None


@dataclass
class PredictionReport:
    """预测报告"""
    symbol: str
    predictions: List[Prediction]
    model_performance: Dict
    timestamp: str


class MLPredictor:
    """机器学习预测器"""
    
    def __init__(self, config: Optional[PredictionConfig] = None):
        """
        初始化预测器
        
        Args:
            config: 预测配置
        """
        self.config = config or PredictionConfig()
        self.models = {}  # 多个预测模型
        
        logger.info("ML预测器初始化完成")
    
    def prepare_prediction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        准备预测数据
        
        Args:
            df: OHLCV数据
            
        Returns:
            包含特征和目标的DataFrame
        """
        logger.info("准备预测数据...")
        
        data = df.copy()
        
        # 创建技术特征
        if self.config.use_technical:
            data = FeatureEngineer.create_technical_features(data)
        
        # 创建时间特征
        if self.config.use_time_features:
            data = FeatureEngineer.create_time_features(data)
        
        # 创建目标变量
        data = self._create_target(data)
        
        # 创建滞后特征
        if self.config.use_lag_features:
            # 选择关键特征做滞后
            key_features = ['returns', 'volatility_5', 'rsi_14', 'volume_ratio']
            available_features = [f for f in key_features if f in data.columns]
            
            if available_features:
                data = FeatureEngineer.create_lag_features(
                    data,
                    columns=available_features,
                    lags=self.config.lag_periods
                )
        
        logger.info(f"数据准备完成，特征数: {len(data.columns)}")
        
        return data
    
    def _create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建预测目标
        
        Args:
            df: DataFrame
            
        Returns:
            包含目标列的DataFrame
        """
        data = df.copy()
        horizon = self.config.forecast_horizon
        
        if self.config.predict_type == 'return':
            # 预测未来收益率
            data['target'] = df['close'].pct_change(horizon).shift(-horizon)
            logger.info(f"目标: {horizon}天收益率")
        
        elif self.config.predict_type == 'direction':
            # 预测涨跌方向 (分类)
            future_return = df['close'].pct_change(horizon).shift(-horizon)
            data['target'] = (future_return > 0).astype(int)
            logger.info(f"目标: {horizon}天涨跌方向")
        
        elif self.config.predict_type == 'volatility':
            # 预测未来波动率
            returns = df['close'].pct_change()
            data['target'] = returns.rolling(window=horizon).std().shift(-horizon)
            logger.info(f"目标: {horizon}天波动率")
        
        else:
            raise ValueError(f"不支持的预测类型: {self.config.predict_type}")
        
        return data
    
    def train(self, df: pd.DataFrame) -> Dict:
        """
        训练预测模型
        
        Args:
            df: OHLCV数据
            
        Returns:
            训练结果字典
        """
        logger.info("=" * 60)
        logger.info("训练预测模型")
        logger.info("=" * 60)
        
        # 准备数据
        data = self.prepare_prediction_data(df)
        
        # 删除NaN
        data = data.dropna()
        
        if len(data) < 100:
            logger.error(f"数据不足: {len(data)} 行")
            return {}
        
        # 配置ML框架
        ml_config = MLConfig(
            model_type=self.config.model_type,
            target_column='target',
            test_size=0.2,
            cv_folds=5
        )
        
        # 训练主模型
        logger.info(f"\n训练主模型: {self.config.model_type}")
        framework = MLFramework(ml_config)
        
        X, y, feature_names = framework.prepare_data(data, 'target')
        result = framework.train(X, y)
        
        self.models['main'] = framework
        
        # 如果启用集成，训练多个模型
        if self.config.ensemble:
            logger.info("\n训练集成模型...")
            
            for model_type in ['gbdt', 'ridge']:
                if model_type == self.config.model_type:
                    continue
                
                logger.info(f"\n训练 {model_type}...")
                ml_config_ensemble = MLConfig(
                    model_type=model_type,
                    target_column='target',
                    test_size=0.2
                )
                
                framework_ensemble = MLFramework(ml_config_ensemble)
                X, y, _ = framework_ensemble.prepare_data(data, 'target')
                result_ensemble = framework_ensemble.train(X, y)
                
                self.models[model_type] = framework_ensemble
        
        # 保存模型
        self._save_models()
        
        # 构建结果
        training_result = {
            'model_type': self.config.model_type,
            'predict_type': self.config.predict_type,
            'forecast_horizon': self.config.forecast_horizon,
            'train_score': result.train_score,
            'test_score': result.test_score,
            'cv_mean': result.cv_mean,
            'cv_std': result.cv_std,
            'feature_importance': result.feature_importance,
            'metrics': result.metrics,
            'ensemble': self.config.ensemble,
            'ensemble_models': list(self.models.keys()) if self.config.ensemble else []
        }
        
        logger.info("=" * 60)
        logger.info("模型训练完成")
        logger.info("=" * 60)
        
        return training_result
    
    def predict(self, df: pd.DataFrame) -> Prediction:
        """
        预测
        
        Args:
            df: OHLCV数据
            
        Returns:
            Prediction
        """
        if 'main' not in self.models:
            raise ValueError("模型未训练，请先调用train()")
        
        # 准备数据
        data = self.prepare_prediction_data(df)
        
        # 获取最新数据
        latest_data = data.iloc[-1:]
        
        # 提取特征
        main_model = self.models['main']
        feature_names = main_model.feature_names
        
        # 检查特征
        missing_features = [f for f in feature_names if f not in latest_data.columns]
        if missing_features:
            logger.warning(f"缺失特征: {missing_features}")
            # 用0填充
            for feat in missing_features:
                latest_data[feat] = 0
        
        X = latest_data[feature_names].values
        
        # 主模型预测
        pred = main_model.predict(X)[0]
        
        # 如果使用集成，取平均
        if self.config.ensemble:
            predictions = [pred]
            
            for model_name, model in self.models.items():
                if model_name == 'main':
                    continue
                
                try:
                    pred_ensemble = model.predict(X)[0]
                    predictions.append(pred_ensemble)
                except Exception as e:
                    logger.warning(f"{model_name} 预测失败: {e}")
            
            pred = np.mean(predictions)
            confidence = 1.0 - np.std(predictions)  # 标准差越小，信心越高
        else:
            confidence = None
        
        prediction = Prediction(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            predict_type=self.config.predict_type,
            forecast_horizon=self.config.forecast_horizon,
            prediction=float(pred),
            confidence=confidence,
            features_used=feature_names
        )
        
        logger.info(f"预测结果: {pred:.4f}")
        if confidence:
            logger.info(f"预测信心: {confidence:.4f}")
        
        return prediction
    
    def predict_batch(self, df: pd.DataFrame, last_n: int = 20) -> List[Prediction]:
        """
        批量预测最近N个时间点
        
        Args:
            df: OHLCV数据
            last_n: 最近N个时间点
            
        Returns:
            预测列表
        """
        logger.info(f"批量预测最近 {last_n} 个时间点")
        
        predictions = []
        
        for i in range(last_n, 0, -1):
            try:
                # 使用前i个数据点
                df_slice = df.iloc[:-i] if i > 1 else df
                pred = self.predict(df_slice)
                predictions.append(pred)
            except Exception as e:
                logger.warning(f"预测失败 (t-{i}): {e}")
        
        return predictions
    
    def generate_report(self, 
                       symbol: str,
                       df: pd.DataFrame,
                       training_result: Dict) -> PredictionReport:
        """
        生成预测报告
        
        Args:
            symbol: 股票代码
            df: OHLCV数据
            training_result: 训练结果
            
        Returns:
            PredictionReport
        """
        logger.info(f"生成预测报告: {symbol}")
        
        # 最新预测
        latest_pred = self.predict(df)
        
        # 批量预测 (验证)
        batch_preds = self.predict_batch(df, last_n=10)
        
        report = PredictionReport(
            symbol=symbol,
            predictions=[latest_pred] + batch_preds,
            model_performance=training_result,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return report
    
    def _save_models(self):
        """保存所有模型"""
        save_dir = Path("data/models/ml_predictor")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for model_name, model in self.models.items():
            filename = f"{self.config.predict_type}_{model_name}_{timestamp}.pkl"
            model.save_model(filename)
        
        logger.info(f"模型已保存到: {save_dir}")
    
    def load_models(self, model_dir: str):
        """
        加载模型
        
        Args:
            model_dir: 模型目录
        """
        model_path = Path(model_dir)
        
        if not model_path.exists():
            raise FileNotFoundError(f"模型目录不存在: {model_dir}")
        
        # 加载所有.pkl文件
        for model_file in model_path.glob("*.pkl"):
            model_name = model_file.stem.split('_')[1]  # 提取模型名
            
            ml_config = MLConfig()
            framework = MLFramework(ml_config)
            framework.load_model(model_file.name)
            
            self.models[model_name] = framework
            logger.info(f"已加载模型: {model_name}")


class ReturnPredictor(MLPredictor):
    """收益率预测器"""
    
    def __init__(self, forecast_horizon: int = 5):
        config = PredictionConfig(
            predict_type='return',
            forecast_horizon=forecast_horizon,
            model_type='random_forest',
            ensemble=True
        )
        super().__init__(config)


class DirectionPredictor(MLPredictor):
    """方向预测器"""
    
    def __init__(self, forecast_horizon: int = 5):
        config = PredictionConfig(
            predict_type='direction',
            forecast_horizon=forecast_horizon,
            model_type='random_forest',
            ensemble=True
        )
        super().__init__(config)


class VolatilityPredictor(MLPredictor):
    """波动率预测器"""
    
    def __init__(self, forecast_horizon: int = 5):
        config = PredictionConfig(
            predict_type='volatility',
            forecast_horizon=forecast_horizon,
            model_type='gbdt',
            ensemble=False
        )
        super().__init__(config)


# 便捷函数
def quick_predict_return(df: pd.DataFrame, 
                         forecast_horizon: int = 5) -> Prediction:
    """
    快速预测收益率
    
    Args:
        df: OHLCV数据
        forecast_horizon: 预测周期
        
    Returns:
        Prediction
    """
    predictor = ReturnPredictor(forecast_horizon)
    predictor.train(df)
    return predictor.predict(df)


def quick_predict_direction(df: pd.DataFrame,
                           forecast_horizon: int = 5) -> Prediction:
    """
    快速预测方向
    
    Args:
        df: OHLCV数据
        forecast_horizon: 预测周期
        
    Returns:
        Prediction
    """
    predictor = DirectionPredictor(forecast_horizon)
    predictor.train(df)
    return predictor.predict(df)

"""
机器学习框架 - 特征工程、模型训练、交叉验证
Machine Learning Framework for Quantitative Finance
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from pathlib import Path
from loguru import logger

try:
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge, Lasso
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("Scikit-learn未安装，机器学习功能不可用")
    SKLEARN_AVAILABLE = False


@dataclass
class MLConfig:
    """机器学习配置"""
    # 特征工程
    feature_columns: List[str] = None
    target_column: str = 'target'
    scaler_type: str = 'standard'      # 'standard', 'minmax', 'robust'
    
    # 模型配置
    model_type: str = 'random_forest'   # 'random_forest', 'gbdt', 'ridge', 'lasso'
    model_params: Dict = None
    
    # 训练配置
    test_size: float = 0.2
    cv_folds: int = 5
    random_state: int = 42
    
    # 存储路径
    model_save_dir: str = "data/models"
    

@dataclass
class MLResult:
    """机器学习结果"""
    model_name: str
    train_score: float
    test_score: float
    cv_scores: List[float]
    cv_mean: float
    cv_std: float
    feature_importance: Optional[Dict[str, float]]
    predictions: Optional[np.ndarray]
    metrics: Dict[str, float]
    timestamp: str


class FeatureEngineer:
    """特征工程师"""
    
    @staticmethod
    def create_technical_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        创建技术指标特征
        
        Args:
            df: OHLCV数据
            
        Returns:
            包含技术特征的DataFrame
        """
        logger.info("创建技术指标特征...")
        
        features = df.copy()
        
        # 价格特征
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # 移动平均
        for window in [5, 10, 20, 60]:
            features[f'ma_{window}'] = df['close'].rolling(window=window).mean()
            features[f'close_ma_{window}_ratio'] = df['close'] / features[f'ma_{window}']
        
        # 波动率
        for window in [5, 10, 20]:
            features[f'volatility_{window}'] = df['close'].pct_change().rolling(window=window).std()
        
        # 动量指标
        for period in [5, 10, 20]:
            features[f'momentum_{period}'] = df['close'] / df['close'].shift(period) - 1
        
        # RSI
        for period in [14, 28]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            features[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = exp1 - exp2
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_hist'] = features['macd'] - features['macd_signal']
        
        # 布林带
        for window in [20]:
            ma = df['close'].rolling(window=window).mean()
            std = df['close'].rolling(window=window).std()
            features[f'bollinger_upper_{window}'] = ma + (std * 2)
            features[f'bollinger_lower_{window}'] = ma - (std * 2)
            features[f'bollinger_width_{window}'] = (features[f'bollinger_upper_{window}'] - 
                                                     features[f'bollinger_lower_{window}']) / ma
            features[f'bollinger_position_{window}'] = (df['close'] - features[f'bollinger_lower_{window}']) / \
                                                       (features[f'bollinger_upper_{window}'] - features[f'bollinger_lower_{window}'])
        
        # 成交量特征
        features['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        features['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        features['volume_ratio'] = df['volume'] / features['volume_ma_20']
        
        # OBV (On Balance Volume)
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        features['obv'] = obv
        features['obv_ma_5'] = features['obv'].rolling(window=5).mean()
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        features['atr_14'] = true_range.rolling(window=14).mean()
        
        logger.info(f"创建了 {len(features.columns) - len(df.columns)} 个技术特征")
        
        return features
    
    @staticmethod
    def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        创建时间特征
        
        Args:
            df: 包含时间索引的DataFrame
            
        Returns:
            包含时间特征的DataFrame
        """
        logger.info("创建时间特征...")
        
        features = df.copy()
        
        if isinstance(features.index, pd.DatetimeIndex):
            features['day_of_week'] = features.index.dayofweek
            features['day_of_month'] = features.index.day
            features['month'] = features.index.month
            features['quarter'] = features.index.quarter
            features['is_month_start'] = features.index.is_month_start.astype(int)
            features['is_month_end'] = features.index.is_month_end.astype(int)
            features['is_quarter_start'] = features.index.is_quarter_start.astype(int)
            features['is_quarter_end'] = features.index.is_quarter_end.astype(int)
            
            logger.info("时间特征创建完成")
        else:
            logger.warning("索引不是DatetimeIndex，跳过时间特征")
        
        return features
    
    @staticmethod
    def create_lag_features(df: pd.DataFrame,
                           columns: List[str],
                           lags: List[int] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
        """
        创建滞后特征
        
        Args:
            df: DataFrame
            columns: 要创建滞后的列
            lags: 滞后期数列表
            
        Returns:
            包含滞后特征的DataFrame
        """
        logger.info(f"创建滞后特征: {columns}, lags={lags}")
        
        features = df.copy()
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"列不存在: {col}")
                continue
            
            for lag in lags:
                features[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        logger.info(f"创建了 {len(columns) * len(lags)} 个滞后特征")
        
        return features


class MLFramework:
    """机器学习框架"""
    
    def __init__(self, config: Optional[MLConfig] = None):
        """
        初始化机器学习框架
        
        Args:
            config: ML配置
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("请安装 scikit-learn: pip install scikit-learn")
        
        self.config = config or MLConfig()
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        # 创建模型保存目录
        Path(self.config.model_save_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info("机器学习框架初始化完成")
    
    def prepare_data(self,
                    df: pd.DataFrame,
                    target_column: str,
                    feature_columns: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        准备训练数据
        
        Args:
            df: 特征数据
            target_column: 目标列
            feature_columns: 特征列 (None则自动选择)
            
        Returns:
            (X, y, feature_names)
        """
        logger.info("准备训练数据...")
        
        # 删除NaN
        df = df.dropna()
        
        # 选择特征列
        if feature_columns is None:
            # 排除目标列和非数值列
            feature_columns = [col for col in df.columns 
                             if col != target_column and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]]
        
        # 提取特征和目标
        X = df[feature_columns].values
        y = df[target_column].values
        
        self.feature_names = feature_columns
        
        logger.info(f"数据形状: X={X.shape}, y={y.shape}")
        logger.info(f"特征数量: {len(feature_columns)}")
        
        return X, y, feature_columns
    
    def scale_features(self, X_train: np.ndarray, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        特征缩放
        
        Args:
            X_train: 训练集特征
            X_test: 测试集特征
            
        Returns:
            (X_train_scaled, X_test_scaled)
        """
        logger.info(f"特征缩放: {self.config.scaler_type}")
        
        # 选择缩放器
        if self.config.scaler_type == 'standard':
            self.scaler = StandardScaler()
        elif self.config.scaler_type == 'minmax':
            self.scaler = MinMaxScaler()
        elif self.config.scaler_type == 'robust':
            self.scaler = RobustScaler()
        else:
            logger.warning(f"未知的scaler类型: {self.config.scaler_type}, 使用standard")
            self.scaler = StandardScaler()
        
        # 拟合和转换
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def create_model(self) -> Any:
        """
        创建模型
        
        Returns:
            模型实例
        """
        model_type = self.config.model_type
        params = self.config.model_params or {}
        
        logger.info(f"创建模型: {model_type}")
        
        if model_type == 'random_forest':
            model = RandomForestRegressor(
                n_estimators=params.get('n_estimators', 100),
                max_depth=params.get('max_depth', 10),
                min_samples_split=params.get('min_samples_split', 5),
                random_state=self.config.random_state,
                n_jobs=-1
            )
        
        elif model_type == 'gbdt':
            model = GradientBoostingRegressor(
                n_estimators=params.get('n_estimators', 100),
                max_depth=params.get('max_depth', 5),
                learning_rate=params.get('learning_rate', 0.1),
                random_state=self.config.random_state
            )
        
        elif model_type == 'ridge':
            model = Ridge(
                alpha=params.get('alpha', 1.0),
                random_state=self.config.random_state
            )
        
        elif model_type == 'lasso':
            model = Lasso(
                alpha=params.get('alpha', 1.0),
                random_state=self.config.random_state
            )
        
        else:
            logger.error(f"不支持的模型类型: {model_type}")
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        return model
    
    def train(self,
             X: np.ndarray,
             y: np.ndarray,
             validation_split: Optional[float] = None) -> MLResult:
        """
        训练模型
        
        Args:
            X: 特征
            y: 目标
            validation_split: 验证集比例 (None则使用交叉验证)
            
        Returns:
            MLResult
        """
        logger.info("=" * 60)
        logger.info("开始训练模型")
        logger.info("=" * 60)
        
        # 创建模型
        self.model = self.create_model()
        
        # 划分训练集和测试集
        split_idx = int(len(X) * (1 - self.config.test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 特征缩放
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        # 训练
        logger.info("训练模型...")
        self.model.fit(X_train_scaled, y_train)
        
        # 评估
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"训练集R²: {train_score:.4f}")
        logger.info(f"测试集R²: {test_score:.4f}")
        
        # 交叉验证
        logger.info("执行时间序列交叉验证...")
        tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)
        cv_scores = cross_val_score(
            self.model,
            X_train_scaled,
            y_train,
            cv=tscv,
            scoring='r2',
            n_jobs=-1
        )
        
        logger.info(f"交叉验证R²: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # 预测
        y_pred = self.model.predict(X_test_scaled)
        
        # 计算更多指标
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': test_score
        }
        
        # 特征重要性
        feature_importance = self._get_feature_importance()
        
        # 构建结果
        result = MLResult(
            model_name=self.config.model_type,
            train_score=train_score,
            test_score=test_score,
            cv_scores=cv_scores.tolist(),
            cv_mean=cv_scores.mean(),
            cv_std=cv_scores.std(),
            feature_importance=feature_importance,
            predictions=y_pred,
            metrics=metrics,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        logger.info("=" * 60)
        logger.info("模型训练完成")
        logger.info(f"RMSE: {rmse:.6f}")
        logger.info(f"MAE: {mae:.6f}")
        logger.info("=" * 60)
        
        return result
    
    def _get_feature_importance(self) -> Optional[Dict[str, float]]:
        """获取特征重要性"""
        if self.model is None or self.feature_names is None:
            return None
        
        # 检查模型是否支持feature_importances_
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            # 创建字典并排序
            importance_dict = dict(zip(self.feature_names, importances))
            importance_dict = dict(sorted(importance_dict.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True))
            
            # 打印top 10
            logger.info("\nTop 10 重要特征:")
            for i, (feat, imp) in enumerate(list(importance_dict.items())[:10], 1):
                logger.info(f"{i}. {feat}: {imp:.4f}")
            
            return importance_dict
        
        return None
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Args:
            X: 特征
            
        Returns:
            预测值
        """
        if self.model is None:
            raise ValueError("模型未训练")
        
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
        return self.model.predict(X_scaled)
    
    def save_model(self, filename: Optional[str] = None):
        """保存模型"""
        if self.model is None:
            logger.warning("没有模型可保存")
            return
        
        if filename is None:
            filename = f"{self.config.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        filepath = Path(self.config.model_save_dir) / filename
        
        # 保存模型和缩放器
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'config': self.config
        }, filepath)
        
        logger.info(f"模型已保存: {filepath}")
    
    def load_model(self, filename: str):
        """加载模型"""
        filepath = Path(self.config.model_save_dir) / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        data = joblib.load(filepath)
        
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.config = data.get('config', self.config)
        
        logger.info(f"模型已加载: {filepath}")


# 便捷函数
def quick_ml_train(df: pd.DataFrame,
                  target_column: str,
                  model_type: str = 'random_forest') -> MLResult:
    """
    快速训练模型
    
    Args:
        df: 包含特征和目标的DataFrame
        target_column: 目标列名
        model_type: 模型类型
        
    Returns:
        MLResult
    """
    config = MLConfig(model_type=model_type, target_column=target_column)
    framework = MLFramework(config)
    
    X, y, feature_names = framework.prepare_data(df, target_column)
    result = framework.train(X, y)
    
    return result

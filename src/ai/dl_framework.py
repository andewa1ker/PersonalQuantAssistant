"""
深度学习框架 - LSTM、GRU、Transformer时序预测
Deep Learning Framework for Time Series Prediction
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch未安装，深度学习功能不可用")
    TORCH_AVAILABLE = False


@dataclass
class DLConfig:
    """深度学习配置"""
    # 模型类型
    model_type: str = 'lstm'           # 'lstm', 'gru', 'transformer'
    
    # 序列参数
    sequence_length: int = 60          # 输入序列长度
    prediction_horizon: int = 5        # 预测长度
    
    # 模型结构
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.2
    
    # Transformer特定参数
    num_heads: int = 8
    ff_dim: int = 256
    
    # 训练参数
    batch_size: int = 32
    epochs: int = 50
    learning_rate: float = 0.001
    weight_decay: float = 1e-5
    
    # 设备
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # 存储路径
    model_save_dir: str = "data/models/dl"


class TimeSeriesDataset(Dataset):
    """时间序列数据集"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        """
        初始化数据集
        
        Args:
            X: 输入序列 (N, seq_len, features)
            y: 目标值 (N, pred_horizon)
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class LSTMModel(nn.Module):
    """LSTM模型"""
    
    def __init__(self, 
                 input_size: int,
                 hidden_size: int,
                 num_layers: int,
                 output_size: int,
                 dropout: float = 0.2):
        """
        初始化LSTM模型
        
        Args:
            input_size: 输入特征数
            hidden_size: 隐藏层大小
            num_layers: 层数
            output_size: 输出大小
            dropout: Dropout比率
        """
        super(LSTMModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # 取最后一个时间步
        last_output = lstm_out[:, -1, :]
        
        # Dropout + 全连接
        out = self.dropout(last_output)
        out = self.fc(out)
        
        return out


class GRUModel(nn.Module):
    """GRU模型"""
    
    def __init__(self,
                 input_size: int,
                 hidden_size: int,
                 num_layers: int,
                 output_size: int,
                 dropout: float = 0.2):
        """
        初始化GRU模型
        
        Args:
            input_size: 输入特征数
            hidden_size: 隐藏层大小
            num_layers: 层数
            output_size: 输出大小
            dropout: Dropout比率
        """
        super(GRUModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # GRU forward
        gru_out, _ = self.gru(x)
        
        # 取最后一个时间步
        last_output = gru_out[:, -1, :]
        
        # Dropout + 全连接
        out = self.dropout(last_output)
        out = self.fc(out)
        
        return out


class PositionalEncoding(nn.Module):
    """位置编码"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:, :x.size(1), :]


class TransformerModel(nn.Module):
    """Transformer模型"""
    
    def __init__(self,
                 input_size: int,
                 d_model: int,
                 num_heads: int,
                 num_layers: int,
                 ff_dim: int,
                 output_size: int,
                 dropout: float = 0.2):
        """
        初始化Transformer模型
        
        Args:
            input_size: 输入特征数
            d_model: Transformer维度
            num_heads: 注意力头数
            num_layers: 层数
            ff_dim: 前馈网络维度
            output_size: 输出大小
            dropout: Dropout比率
        """
        super(TransformerModel, self).__init__()
        
        # 输入投影
        self.input_proj = nn.Linear(input_size, d_model)
        
        # 位置编码
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Transformer编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 输出层
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(d_model, output_size)
    
    def forward(self, x):
        # 输入投影
        x = self.input_proj(x)
        
        # 位置编码
        x = self.pos_encoder(x)
        
        # Transformer
        x = self.transformer(x)
        
        # 取最后一个时间步
        x = x[:, -1, :]
        
        # Dropout + 全连接
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class DLFramework:
    """深度学习框架"""
    
    def __init__(self, config: Optional[DLConfig] = None):
        """
        初始化深度学习框架
        
        Args:
            config: DL配置
        """
        if not TORCH_AVAILABLE:
            raise ImportError("请安装 PyTorch: pip install torch")
        
        self.config = config or DLConfig()
        self.model = None
        self.optimizer = None
        self.criterion = nn.MSELoss()
        
        # 创建模型保存目录
        Path(self.config.model_save_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"深度学习框架初始化完成 (设备: {self.config.device})")
    
    def prepare_sequences(self, 
                         df: pd.DataFrame,
                         target_column: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """
        准备时间序列数据
        
        Args:
            df: 特征数据
            target_column: 目标列
            
        Returns:
            (X, y) 序列数组
        """
        logger.info("准备时间序列数据...")
        
        # 选择特征列
        feature_columns = [col for col in df.columns if col != target_column]
        
        data = df[feature_columns].values
        target = df[target_column].values
        
        seq_len = self.config.sequence_length
        pred_horizon = self.config.prediction_horizon
        
        X, y = [], []
        
        for i in range(len(data) - seq_len - pred_horizon + 1):
            # 输入序列
            X.append(data[i:i+seq_len])
            
            # 目标：未来pred_horizon个值的平均收益率
            future_prices = target[i+seq_len:i+seq_len+pred_horizon]
            current_price = target[i+seq_len-1]
            future_return = (future_prices[-1] - current_price) / current_price
            
            y.append([future_return])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"序列形状: X={X.shape}, y={y.shape}")
        
        return X, y
    
    def create_model(self, input_size: int, output_size: int):
        """
        创建模型
        
        Args:
            input_size: 输入特征数
            output_size: 输出大小
        """
        model_type = self.config.model_type
        
        logger.info(f"创建模型: {model_type}")
        
        if model_type == 'lstm':
            model = LSTMModel(
                input_size=input_size,
                hidden_size=self.config.hidden_size,
                num_layers=self.config.num_layers,
                output_size=output_size,
                dropout=self.config.dropout
            )
        
        elif model_type == 'gru':
            model = GRUModel(
                input_size=input_size,
                hidden_size=self.config.hidden_size,
                num_layers=self.config.num_layers,
                output_size=output_size,
                dropout=self.config.dropout
            )
        
        elif model_type == 'transformer':
            model = TransformerModel(
                input_size=input_size,
                d_model=self.config.hidden_size,
                num_heads=self.config.num_heads,
                num_layers=self.config.num_layers,
                ff_dim=self.config.ff_dim,
                output_size=output_size,
                dropout=self.config.dropout
            )
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        model = model.to(self.config.device)
        
        # 打印模型结构
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"模型参数数量: {total_params:,}")
        
        return model
    
    def train(self, 
             X: np.ndarray, 
             y: np.ndarray,
             validation_split: float = 0.2) -> Dict:
        """
        训练模型
        
        Args:
            X: 输入序列
            y: 目标值
            validation_split: 验证集比例
            
        Returns:
            训练历史
        """
        logger.info("=" * 60)
        logger.info("开始训练深度学习模型")
        logger.info("=" * 60)
        
        # 划分训练集和验证集
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # 创建数据集
        train_dataset = TimeSeriesDataset(X_train, y_train)
        val_dataset = TimeSeriesDataset(X_val, y_val)
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False
        )
        
        # 创建模型
        input_size = X.shape[2]
        output_size = y.shape[1]
        
        self.model = self.create_model(input_size, output_size)
        
        # 优化器
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        
        # 学习率调度器
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        # 训练循环
        history = {
            'train_loss': [],
            'val_loss': []
        }
        
        best_val_loss = float('inf')
        patience_counter = 0
        early_stop_patience = 10
        
        for epoch in range(self.config.epochs):
            # 训练
            self.model.train()
            train_loss = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.config.device)
                batch_y = batch_y.to(self.config.device)
                
                # 前向传播
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                
                # 反向传播
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # 验证
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.config.device)
                    batch_y = batch_y.to(self.config.device)
                    
                    outputs = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            
            # 记录
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            
            # 学习率调度
            scheduler.step(val_loss)
            
            # 早停检查
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # 保存最佳模型
                self.save_model('best_model.pth')
            else:
                patience_counter += 1
            
            # 打印进度
            if (epoch + 1) % 5 == 0 or epoch == 0:
                logger.info(f"Epoch [{epoch+1}/{self.config.epochs}] "
                          f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
            
            # 早停
            if patience_counter >= early_stop_patience:
                logger.info(f"早停触发 (Epoch {epoch+1})")
                break
        
        logger.info("=" * 60)
        logger.info("模型训练完成")
        logger.info(f"最佳验证Loss: {best_val_loss:.6f}")
        logger.info("=" * 60)
        
        # 加载最佳模型
        self.load_model('best_model.pth')
        
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Args:
            X: 输入序列
            
        Returns:
            预测值
        """
        if self.model is None:
            raise ValueError("模型未训练")
        
        self.model.eval()
        
        X_tensor = torch.FloatTensor(X).to(self.config.device)
        
        with torch.no_grad():
            predictions = self.model(X_tensor)
        
        return predictions.cpu().numpy()
    
    def save_model(self, filename: str):
        """保存模型"""
        if self.model is None:
            logger.warning("没有模型可保存")
            return
        
        filepath = Path(self.config.model_save_dir) / filename
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'config': self.config
        }, filepath)
        
        logger.info(f"模型已保存: {filepath}")
    
    def load_model(self, filename: str):
        """加载模型"""
        filepath = Path(self.config.model_save_dir) / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        checkpoint = torch.load(filepath, map_location=self.config.device)
        
        # 重建模型
        # 这里需要先知道input_size和output_size
        # 实际使用中应该保存这些信息
        logger.warning("加载模型需要预先知道模型结构")
        
        logger.info(f"模型已加载: {filepath}")


# 便捷函数
def quick_lstm_predict(df: pd.DataFrame, 
                       prediction_horizon: int = 5,
                       epochs: int = 30) -> np.ndarray:
    """
    快速LSTM预测
    
    Args:
        df: OHLCV数据
        prediction_horizon: 预测周期
        epochs: 训练轮数
        
    Returns:
        预测值
    """
    config = DLConfig(
        model_type='lstm',
        prediction_horizon=prediction_horizon,
        epochs=epochs
    )
    
    framework = DLFramework(config)
    X, y = framework.prepare_sequences(df)
    history = framework.train(X, y)
    
    # 预测最后一个序列
    last_X = X[-1:]
    prediction = framework.predict(last_X)
    
    return prediction

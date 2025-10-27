"""
配置管理模块
负责加载和验证配置文件
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import os


class AppConfig(BaseModel):
    """应用配置"""
    name: str
    version: str
    timezone: str = "Asia/Shanghai"
    log_level: str = "INFO"
    cache_ttl: int = 3600


class AssetConfig(BaseModel):
    """资产配置"""
    enabled: bool = True
    symbol: Optional[str] = None
    symbols: Optional[list] = None
    data_source: str
    update_frequency: int
    position_limit: float


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 config/config.yaml
        """
        if config_path is None:
            # 获取项目根目录
            self.root_dir = Path(__file__).parent.parent.parent
            config_path = self.root_dir / "config" / "config.yaml"
        else:
            self.root_dir = Path(config_path).parent.parent
            config_path = Path(config_path)
        
        self.config_path = config_path
        self.api_keys_path = self.root_dir / "config" / "api_keys.yaml"
        
        self._config: Dict[str, Any] = {}
        self._api_keys: Dict[str, Any] = {}
        
        self.load_config()
        self.load_api_keys()
    
    def load_config(self) -> None:
        """加载主配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            # print(f"✓ 配置文件加载成功: {self.config_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def load_api_keys(self) -> None:
        """加载API密钥文件"""
        try:
            if self.api_keys_path.exists():
                with open(self.api_keys_path, 'r', encoding='utf-8') as f:
                    self._api_keys = yaml.safe_load(f)
                # print(f"✓ API密钥文件加载成功: {self.api_keys_path}")
            else:
                # print(f"⚠ API密钥文件不存在，使用默认配置: {self.api_keys_path}")
                self._api_keys = {}
        except yaml.YAMLError as e:
            raise ValueError(f"API密钥文件格式错误: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'app.name'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_api_key(self, service: str, key: str = 'api_key') -> Optional[str]:
        """
        获取API密钥
        
        Args:
            service: 服务名称，如 'tushare'
            key: 密钥字段名，默认为 'api_key'
            
        Returns:
            API密钥
        """
        if service in self._api_keys:
            return self._api_keys[service].get(key)
        return None
    
    def get_asset_config(self, asset_name: str) -> Optional[Dict[str, Any]]:
        """
        获取资产配置
        
        Args:
            asset_name: 资产名称，如 'etf_513500', 'crypto'
            
        Returns:
            资产配置字典
        """
        return self.get(f'assets.{asset_name}')
    
    def get_enabled_assets(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的资产配置"""
        assets = self.get('assets', {})
        return {
            name: config 
            for name, config in assets.items() 
            if config.get('enabled', False)
        }
    
    def get_strategy_config(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        获取策略配置
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            策略配置字典
        """
        return self.get(f'strategy.{strategy_name}')
    
    def get_risk_config(self) -> Dict[str, Any]:
        """获取风险管理配置"""
        return self.get('risk_management', {})
    
    def get_data_path(self, subdir: str = '') -> Path:
        """
        获取数据目录路径
        
        Args:
            subdir: 子目录名称，如 'market_data', 'portfolio'
            
        Returns:
            数据目录路径
        """
        data_dir = self.root_dir / "data"
        if subdir:
            data_dir = data_dir / subdir
        
        # 确保目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def is_asset_enabled(self, asset_name: str) -> bool:
        """检查资产是否启用"""
        config = self.get_asset_config(asset_name)
        return config.get('enabled', False) if config else False
    
    def is_alert_enabled(self, alert_type: str = None) -> bool:
        """
        检查警报是否启用
        
        Args:
            alert_type: 警报类型，如 'price', 'technical', 'risk'
                       如果为None，检查总开关
        """
        if alert_type is None:
            return self.get('alerts.enabled', False)
        return self.get(f'alerts.{alert_type}.enabled', False)
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self.load_config()
        self.load_api_keys()
        print("✓ 配置已重新加载")
    
    @property
    def app_name(self) -> str:
        """获取应用名称"""
        return self.get('app.name', 'Personal Quant Assistant')
    
    @property
    def app_version(self) -> str:
        """获取应用版本"""
        return self.get('app.version', '1.0.0')
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self.get('app.log_level', 'INFO')
    
    @property
    def deepseek_api_key(self) -> Optional[str]:
        """获取DeepSeek API密钥"""
        return self.get_api_key('deepseek', 'api_key')
    
    def __repr__(self) -> str:
        return f"ConfigManager(config_path='{self.config_path}')"


# 全局配置实例
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    获取配置管理器单例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigManager实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    
    return _config_instance


if __name__ == "__main__":
    # 测试配置管理器
    config = get_config()
    
    print("\n=== 应用配置 ===")
    print(f"应用名称: {config.app_name}")
    print(f"版本: {config.app_version}")
    print(f"日志级别: {config.log_level}")
    
    print("\n=== 启用的资产 ===")
    for name, cfg in config.get_enabled_assets().items():
        print(f"- {name}: {cfg.get('symbol') or cfg.get('symbols')}")
    
    print("\n=== 数据路径 ===")
    print(f"市场数据: {config.get_data_path('market_data')}")
    print(f"持仓数据: {config.get_data_path('portfolio')}")
    
    print("\n=== 风险管理配置 ===")
    risk_cfg = config.get_risk_config()
    print(f"最大仓位: {risk_cfg.get('position', {}).get('max_position_pct', 0)}")
    print(f"最大回撤: {risk_cfg.get('position', {}).get('max_drawdown_pct', 0)}")

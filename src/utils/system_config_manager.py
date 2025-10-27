"""
系统配置管理器
管理用户偏好设置、交易参数、通知设置等
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger


class SystemConfigManager:
    """系统配置管理器"""
    
    DEFAULT_CONFIG = {
        "user": {
            "username": "量化投资者",
            "email": "user@example.com",
            "risk_preference": "平衡",  # 保守/稳健/平衡/进取/激进
            "created_at": datetime.now().isoformat()
        },
        "trading": {
            "max_position_per_asset": 0.30,  # 单资产最大仓位30%
            "max_daily_trades": 10,
            "auto_rebalance": True,
            "rebalance_threshold": 0.05,
            "default_stop_loss": 0.05,
            "default_take_profit": 0.15
        },
        "data_sources": {
            "coingecko": {"enabled": True, "priority": 1},
            "tushare": {"enabled": True, "priority": 2, "token": ""},
            "akshare": {"enabled": True, "priority": 3}
        },
        "notifications": {
            "price_alert": True,
            "signal_alert": True,
            "risk_alert": True,
            "daily_summary": False,
            "email": False,
            "wechat": False
        },
        "ui": {
            "theme": "auto",  # light/dark/auto
            "language": "zh_CN",
            "default_chart_days": 30
        },
        "advanced": {
            "cache_enabled": True,
            "cache_ttl": 300,
            "api_timeout": 10,
            "log_level": "INFO"
        },
        "updated_at": datetime.now().isoformat()
    }
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "system_config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # 加载或创建配置
        self.config = self._load_config()
        
        logger.info(f"系统配置管理器初始化完成: {self.config_file}")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_file.exists():
            logger.info("配置文件不存在,创建默认配置")
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("配置文件加载成功")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}, 使用默认配置")
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict) -> bool:
        """保存配置到文件"""
        try:
            config["updated_at"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("配置文件保存成功")
            return True
        except Exception as e:
            logger.error(f"配置文件保存失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置路径,用.分隔,如 'user.username'
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key_path: 配置路径,用.分隔
            value: 新值
            
        Returns:
            bool: 是否成功
        """
        keys = key_path.split('.')
        config = self.config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        return self._save_config(self.config)
    
    def get_section(self, section: str) -> Dict:
        """
        获取配置节
        
        Args:
            section: 节名称,如 'user', 'trading'
            
        Returns:
            Dict: 配置节内容
        """
        return self.config.get(section, {})
    
    def update_section(self, section: str, values: Dict) -> bool:
        """
        更新配置节
        
        Args:
            section: 节名称
            values: 新值字典
            
        Returns:
            bool: 是否成功
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(values)
        return self._save_config(self.config)
    
    def reset_section(self, section: str) -> bool:
        """
        重置配置节为默认值
        
        Args:
            section: 节名称
            
        Returns:
            bool: 是否成功
        """
        if section in self.DEFAULT_CONFIG:
            self.config[section] = self.DEFAULT_CONFIG[section].copy()
            return self._save_config(self.config)
        return False
    
    def reset_all(self) -> bool:
        """重置所有配置为默认值"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self._save_config(self.config)
    
    def export_config(self) -> str:
        """
        导出配置为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.config, indent=2, ensure_ascii=False)
    
    def import_config(self, config_json: str) -> bool:
        """
        从JSON字符串导入配置
        
        Args:
            config_json: JSON字符串
            
        Returns:
            bool: 是否成功
        """
        try:
            new_config = json.loads(config_json)
            self.config = new_config
            return self._save_config(self.config)
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

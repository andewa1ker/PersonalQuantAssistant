"""
策略配置管理器
管理用户的策略配置,保存/加载/编辑
"""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger


class StrategyConfigManager:
    """策略配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "user_strategies.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # 初始化配置文件
        if not self.config_file.exists():
            self._create_default_config()
        
        logger.info(f"策略配置管理器初始化完成: {self.config_file}")
    
    def _create_default_config(self):
        """创建默认配置"""
        default_strategies = [
            {
                "id": "momentum_btc_1",
                "name": "BTC动量突破策略",
                "type": "crypto_momentum",
                "status": "running",
                "asset": "BTC",
                "params": {
                    "short_window": 5,
                    "long_window": 20,
                    "threshold": 0.02
                },
                "risk": {
                    "stop_loss": 0.05,
                    "position_limit": 0.30
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "dca_eth_1",
                "name": "ETH定投策略",
                "type": "dca",
                "status": "running",
                "asset": "ETH",
                "params": {
                    "investment_amount": 1000,
                    "frequency": "weekly"
                },
                "risk": {
                    "stop_loss": 0.15,
                    "position_limit": 0.25
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump({"strategies": default_strategies}, f, indent=2, ensure_ascii=False)
        
        logger.info("创建默认策略配置")
    
    def get_all_strategies(self) -> List[Dict]:
        """
        获取所有策略配置
        
        Returns:
            List[Dict]: 策略配置列表
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("strategies", [])
        except Exception as e:
            logger.error(f"读取策略配置失败: {e}")
            return []
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """
        获取单个策略配置
        
        Args:
            strategy_id: 策略ID
            
        Returns:
            Optional[Dict]: 策略配置,不存在则返回None
        """
        strategies = self.get_all_strategies()
        for strategy in strategies:
            if strategy.get("id") == strategy_id:
                return strategy
        return None
    
    def save_strategy(self, strategy: Dict) -> bool:
        """
        保存或更新策略配置
        
        Args:
            strategy: 策略配置字典
            
        Returns:
            bool: 是否成功
        """
        try:
            strategies = self.get_all_strategies()
            
            # 检查是否为新策略
            strategy_id = strategy.get("id")
            if not strategy_id:
                # 生成新ID
                strategy_id = f"{strategy['type']}_{strategy['asset']}_{len(strategies)+1}"
                strategy["id"] = strategy_id
                strategy["created_at"] = datetime.now().isoformat()
            
            # 更新时间戳
            strategy["updated_at"] = datetime.now().isoformat()
            
            # 查找并更新,或添加新策略
            found = False
            for i, s in enumerate(strategies):
                if s.get("id") == strategy_id:
                    strategies[i] = strategy
                    found = True
                    break
            
            if not found:
                strategies.append(strategy)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"strategies": strategies}, f, indent=2, ensure_ascii=False)
            
            logger.info(f"策略配置已保存: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存策略配置失败: {e}")
            return False
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """
        删除策略配置
        
        Args:
            strategy_id: 策略ID
            
        Returns:
            bool: 是否成功
        """
        try:
            strategies = self.get_all_strategies()
            strategies = [s for s in strategies if s.get("id") != strategy_id]
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"strategies": strategies}, f, indent=2, ensure_ascii=False)
            
            logger.info(f"策略配置已删除: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除策略配置失败: {e}")
            return False
    
    def update_strategy_status(self, strategy_id: str, status: str) -> bool:
        """
        更新策略状态
        
        Args:
            strategy_id: 策略ID
            status: 新状态 (running/paused/stopped)
            
        Returns:
            bool: 是否成功
        """
        strategy = self.get_strategy(strategy_id)
        if strategy:
            strategy["status"] = status
            strategy["updated_at"] = datetime.now().isoformat()
            return self.save_strategy(strategy)
        return False
    
    def get_strategy_types(self) -> List[Dict]:
        """
        获取支持的策略类型列表
        
        Returns:
            List[Dict]: 策略类型信息
        """
        return [
            {
                "id": "crypto_momentum",
                "name": "加密货币动量策略",
                "description": "基于价格动量的突破交易策略",
                "suitable_for": ["BTC", "ETH", "BNB"]
            },
            {
                "id": "dca",
                "name": "定投策略",
                "description": "固定周期定额投资策略",
                "suitable_for": ["BTC", "ETH", "ETF"]
            },
            {
                "id": "etf_valuation",
                "name": "ETF估值策略",
                "description": "基于估值的ETF买入卖出策略",
                "suitable_for": ["ETF"]
            },
            {
                "id": "mean_reversion",
                "name": "均值回归策略",
                "description": "价格偏离均值后的回归交易",
                "suitable_for": ["BTC", "ETH", "Stock"]
            },
            {
                "id": "trend_following",
                "name": "趋势跟踪策略",
                "description": "跟随市场趋势的交易策略",
                "suitable_for": ["BTC", "ETH", "Stock"]
            }
        ]
    
    def get_stats(self) -> Dict:
        """
        获取策略统计信息
        
        Returns:
            Dict: 统计信息
        """
        strategies = self.get_all_strategies()
        
        total = len(strategies)
        running = sum(1 for s in strategies if s.get("status") == "running")
        paused = sum(1 for s in strategies if s.get("status") == "paused")
        stopped = sum(1 for s in strategies if s.get("status") == "stopped")
        
        return {
            "total": total,
            "running": running,
            "paused": paused,
            "stopped": stopped
        }

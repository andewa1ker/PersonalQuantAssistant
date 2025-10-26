"""
统一数据管理器 - 升级版
整合多个数据源，提供统一的数据获取接口
支持混合策略: Tushare(主) + 新浪 + 东财 + AKShare(备用)
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import pickle
import sys
import time

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.data_fetcher.multi_source_fetcher import MultiSourceETFFetcher
from src.data_fetcher.multi_source_crypto import MultiSourceCryptoFetcher
from src.utils.config_loader import get_config

try:
    from src.utils.logger import log
except ImportError:
    import logging
    log = logging.getLogger(__name__)


class DataManager:
    """统一数据管理器 - 升级版"""
    
    def __init__(self):
        """初始化数据管理器"""
        self.config = get_config()
        
        # 初始化多数据源ETF获取器 (使用硬编码的Tushare token)
        self.etf_fetcher = MultiSourceETFFetcher(
            tushare_token='a4ee49df8870a77df1b14650059f7424dca109a038dc840741474798'
        )
        
        # 初始化多数据源加密货币获取器
        self.crypto_fetcher = MultiSourceCryptoFetcher()
        
        # 缓存配置
        self.cache_dir = self.config.get_data_path('cache')
        self.cache_timeout = self.config.get('app.cache_ttl', 3600)
        
        log.info("DataManager初始化完成 (多数据源模式)")
    
    def get_asset_data(
        self,
        asset_type: str,
        symbol: str,
        data_type: str = 'realtime',
        **kwargs
    ) -> Optional[Any]:
        """
        获取资产数据（统一接口）
        
        Args:
            asset_type: 资产类型，'stock', 'etf', 'crypto'
            symbol: 资产代码
            data_type: 数据类型，'realtime', 'history', 'valuation'
            **kwargs: 其他参数
            
        Returns:
            数据（格式取决于data_type）
        """
        try:
            log.info(f"获取{asset_type}/{symbol}的{data_type}数据")
            
            if asset_type in ['stock', 'etf']:
                return self._get_stock_data(symbol, data_type, **kwargs)
            elif asset_type == 'crypto':
                return self._get_crypto_data(symbol, data_type, **kwargs)
            else:
                log.error(f"不支持的资产类型: {asset_type}")
                return None
                
        except Exception as e:
            log.error(f"获取{asset_type}/{symbol}数据失败: {e}")
            return None
    
    def _get_stock_data(self, symbol: str, data_type: str, **kwargs) -> Optional[Any]:
        """获取股票/ETF数据 - 使用多数据源策略"""
        if data_type == 'realtime':
            return self.etf_fetcher.get_realtime_price(symbol)
        elif data_type == 'history':
            period = kwargs.get('period', '1y')
            end_date = datetime.now().strftime('%Y%m%d')
            
            # 根据period计算start_date
            if period == '1d':
                start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            elif period == '5d':
                start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            elif period == '1m':
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            elif period == '3m':
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
            elif period == '6m':
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
            elif period == '1y':
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            elif period == '3y':
                start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y%m%d')
            elif period == '5y':
                start_date = (datetime.now() - timedelta(days=1825)).strftime('%Y%m%d')
            else:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            return self.etf_fetcher.get_history_data(symbol, start_date, end_date)
        if data_type == 'realtime':
            return self.stock_fetcher.get_realtime_price(symbol)
        elif data_type == 'history':
            period = kwargs.get('period', '1y')
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            return self.stock_fetcher.get_history_data(symbol, start_date, end_date, period)
        elif data_type == 'valuation':
            return self.stock_fetcher.get_valuation_data(symbol)
        else:
            log.error(f"不支持的数据类型: {data_type}")
            return None
    
    def _get_crypto_data(self, symbol: str, data_type: str, **kwargs) -> Optional[Any]:
        """获取加密货币数据 (使用多数据源策略)"""
        if data_type == 'realtime':
            return self.crypto_fetcher.get_realtime_price(symbol)
        elif data_type == 'history':
            days = kwargs.get('days', 90)
            return self.crypto_fetcher.get_history_data(symbol, days)
        elif data_type == 'market':
            coin_list = kwargs.get('coin_list')
            return self.crypto_fetcher.get_market_data(coin_list)
        elif data_type == 'fear_greed':
            return self.crypto_fetcher.get_fear_greed_index()
        else:
            log.error(f"不支持的数据类型: {data_type}")
            return None
    
    def get_portfolio_data(self) -> Dict[str, Any]:
        """
        获取投资组合所有资产的数据
        
        Returns:
            {
                'etf': {...},
                'crypto': {...},
                'timestamp': '...'
            }
        """
        portfolio = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 获取启用的资产
        enabled_assets = self.config.get_enabled_assets()
        
        for asset_name, asset_config in enabled_assets.items():
            try:
                if asset_name == 'etf_513500':
                    # 获取ETF数据
                    symbol = asset_config.get('symbol', '513500')
                    data = self.get_asset_data('etf', symbol, 'realtime')
                    portfolio['etf_513500'] = data
                    
                elif asset_name == 'crypto':
                    # 获取加密货币数据
                    symbols = asset_config.get('symbols', ['bitcoin', 'ethereum'])
                    data = self.crypto_fetcher.get_market_data(symbols)
                    portfolio['crypto'] = data
                    
            except Exception as e:
                log.error(f"获取{asset_name}数据失败: {e}")
                portfolio[asset_name] = None
        
        return portfolio
    
    def cache_data(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        缓存数据到文件
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            ttl: 过期时间（秒），None表示使用默认值
            
        Returns:
            是否成功
        """
        try:
            if ttl is None:
                ttl = self.cache_timeout
            
            cache_file = self.cache_dir / f"{key}.pkl"
            
            cache_data = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            log.debug(f"数据已缓存: {key}")
            return True
            
        except Exception as e:
            log.error(f"缓存数据失败: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，或None（如果不存在或过期）
        """
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            age = time.time() - cache_data['timestamp']
            if age > cache_data['ttl']:
                log.debug(f"缓存已过期: {key} (age: {age:.0f}s)")
                return None
            
            log.debug(f"从缓存获取数据: {key}")
            return cache_data['data']
            
        except Exception as e:
            log.error(f"读取缓存失败: {e}")
            return None
    
    def clear_cache(self, pattern: str = '*') -> int:
        """
        清除缓存文件
        
        Args:
            pattern: 文件模式，如 '*', 'stock_*'
            
        Returns:
            删除的文件数
        """
        try:
            count = 0
            for cache_file in self.cache_dir.glob(f"{pattern}.pkl"):
                cache_file.unlink()
                count += 1
            
            log.info(f"清除了{count}个缓存文件")
            return count
            
        except Exception as e:
            log.error(f"清除缓存失败: {e}")
            return 0
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """获取恐惧贪婪指数"""
        return self.crypto_fetcher.get_fear_greed_index()
    
    def refresh_all_data(self) -> Dict[str, bool]:
        """
        刷新所有资产数据
        
        Returns:
            各资产刷新状态
        """
        log.info("开始刷新所有数据...")
        
        status = {}
        enabled_assets = self.config.get_enabled_assets()
        
        for asset_name, asset_config in enabled_assets.items():
            try:
                if asset_name == 'etf_513500':
                    symbol = asset_config.get('symbol', '513500')
                    data = self.stock_fetcher.get_realtime_price(symbol)
                    status[asset_name] = data is not None
                    
                    if data:
                        self.cache_data(f"realtime_{symbol}", data)
                    
                elif asset_name == 'crypto':
                    symbols = asset_config.get('symbols', ['bitcoin', 'ethereum'])
                    data = self.crypto_fetcher.get_market_data(symbols)
                    status[asset_name] = data is not None
                    
                    if data is not None:
                        self.cache_data(f"crypto_market", data)
                
                time.sleep(1)  # 避免API限制
                
            except Exception as e:
                log.error(f"刷新{asset_name}失败: {e}")
                status[asset_name] = False
        
        log.info(f"数据刷新完成: {status}")
        return status


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=" * 60)
    print("数据管理器测试")
    print("=" * 60)
    
    # 创建数据管理器
    manager = DataManager()
    
    # 测试统一接口
    print("\n1. 测试获取ETF数据...")
    etf_data = manager.get_asset_data('etf', '513500', 'realtime')
    if etf_data:
        print(f"   ✓ {etf_data['name']}: {etf_data['price']:.3f}")
    
    print("\n2. 测试获取加密货币数据...")
    btc_data = manager.get_asset_data('crypto', 'bitcoin', 'realtime')
    if btc_data:
        print(f"   ✓ {btc_data['name']}: ${btc_data['price_usd']:,.2f}")
    
    print("\n3. 测试获取投资组合数据...")
    portfolio = manager.get_portfolio_data()
    print(f"   时间戳: {portfolio['timestamp']}")
    if 'etf_513500' in portfolio and portfolio['etf_513500']:
        print(f"   ETF: {portfolio['etf_513500']['price']:.3f}")
    if 'crypto' in portfolio and portfolio['crypto'] is not None:
        print(f"   加密货币: {len(portfolio['crypto'])}个")
    
    print("\n4. 测试恐惧贪婪指数...")
    fng = manager.get_fear_greed_index()
    if fng:
        print(f"   ✓ {fng['value']} ({fng['classification']})")
    
    print("\n5. 测试缓存功能...")
    manager.cache_data('test_key', {'data': 'test_value'})
    cached = manager.get_cached_data('test_key')
    if cached:
        print(f"   ✓ 缓存读取成功: {cached}")
    
    print("\n6. 测试刷新所有数据...")
    status = manager.refresh_all_data()
    for asset, success in status.items():
        symbol = "✓" if success else "✗"
        print(f"   {symbol} {asset}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

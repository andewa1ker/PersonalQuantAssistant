"""
加密货币数据获取模块
支持CoinGecko和Binance双数据源
"""
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from pathlib import Path
import sys

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.utils.config_loader import get_config

try:
    from src.utils.logger import log
except ImportError:
    import logging
    log = logging.getLogger(__name__)


class CryptoDataFetcher:
    """加密货币数据获取器"""
    
    # CoinGecko币种ID映射
    COIN_ID_MAP = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'BNB': 'binancecoin',
        'SOL': 'solana',
        'ADA': 'cardano',
        'XRP': 'ripple',
        'DOT': 'polkadot',
        'DOGE': 'dogecoin',
        'MATIC': 'matic-network',
        'AVAX': 'avalanche-2'
    }
    
    def __init__(self, data_source: str = 'coingecko'):
        """
        初始化加密货币数据获取器
        
        Args:
            data_source: 数据源，'coingecko' 或 'binance'
        """
        self.config = get_config()
        self.data_source = data_source
        self._cache = {}
        self._cache_timeout = 300  # 加密货币缓存5分钟
        
        # CoinGecko配置
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # Binance配置
        if data_source == 'binance':
            self._init_binance()
        
        log.info(f"CryptoDataFetcher初始化完成，数据源: {data_source}")
    
    def _init_binance(self):
        """初始化Binance API"""
        try:
            from binance.client import Client
            
            api_key = self.config.get_api_key('binance', 'api_key')
            secret_key = self.config.get_api_key('binance', 'secret_key')
            
            if api_key and secret_key:
                self.binance_client = Client(api_key, secret_key)
                log.info("Binance API初始化成功")
            else:
                log.warning("未配置Binance API密钥，将使用CoinGecko")
                self.data_source = 'coingecko'
        except ImportError:
            log.warning("python-binance未安装，将使用CoinGecko")
            self.data_source = 'coingecko'
        except Exception as e:
            log.error(f"Binance初始化失败: {e}")
            self.data_source = 'coingecko'
    
    def get_crypto_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取加密货币实时价格
        
        Args:
            symbol: 币种符号，如 'BTC', 'ETH' 或 'bitcoin', 'ethereum'
            
        Returns:
            价格数据字典: {
                'symbol': 币种符号,
                'name': 币种名称,
                'price_usd': 美元价格,
                'price_cny': 人民币价格,
                'change_24h': 24小时涨跌幅(%),
                'volume_24h': 24小时成交量,
                'market_cap': 市值,
                'timestamp': 时间戳
            }
        """
        # 标准化币种ID
        coin_id = self._normalize_coin_id(symbol)
        
        # 检查缓存
        cache_key = f"price_{coin_id}"
        if cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < 60:  # 价格数据缓存1分钟
                log.debug(f"从缓存获取{coin_id}价格数据")
                return cache_data
        
        try:
            log.info(f"获取{coin_id}实时价格...")
            
            if self.data_source == 'coingecko':
                data = self._get_price_coingecko(coin_id)
            else:
                data = self._get_price_binance(symbol)
            
            # 更新缓存
            self._cache[cache_key] = (data, time.time())
            
            log.info(f"✓ {coin_id}价格: ${data.get('price_usd', 'N/A'):,.2f}")
            return data
            
        except Exception as e:
            log.error(f"获取{coin_id}价格失败: {e}")
            return None
    
    def _get_price_coingecko(self, coin_id: str) -> Dict[str, Any]:
        """使用CoinGecko获取价格"""
        url = f"{self.coingecko_base_url}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd,cny',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if coin_id not in data:
            raise ValueError(f"未找到币种 {coin_id}")
        
        coin_data = data[coin_id]
        
        return {
            'symbol': coin_id.upper()[:3],
            'name': coin_id,
            'price_usd': float(coin_data.get('usd', 0)),
            'price_cny': float(coin_data.get('cny', 0)),
            'change_24h': float(coin_data.get('usd_24h_change', 0)),
            'volume_24h': float(coin_data.get('usd_24h_vol', 0)),
            'market_cap': float(coin_data.get('usd_market_cap', 0)),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_price_binance(self, symbol: str) -> Dict[str, Any]:
        """使用Binance获取价格"""
        # Binance的交易对格式
        trading_pair = f"{symbol.upper()}USDT"
        
        # 获取24小时统计
        ticker = self.binance_client.get_ticker(symbol=trading_pair)
        
        return {
            'symbol': symbol.upper(),
            'name': symbol.lower(),
            'price_usd': float(ticker['lastPrice']),
            'price_cny': float(ticker['lastPrice']) * 7.2,  # 简单汇率转换
            'change_24h': float(ticker['priceChangePercent']),
            'volume_24h': float(ticker['volume']),
            'market_cap': None,  # Binance不提供市值数据
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_market_data(self, coin_ids: List[str] = None) -> Optional[pd.DataFrame]:
        """
        获取多个币种的市场数据
        
        Args:
            coin_ids: 币种ID列表，如果为None则使用配置文件中的币种
            
        Returns:
            DataFrame包含多个币种的市场数据
        """
        if coin_ids is None:
            # 从配置文件获取
            crypto_config = self.config.get_asset_config('crypto')
            if crypto_config and 'symbols' in crypto_config:
                coin_ids = crypto_config['symbols']
            else:
                coin_ids = ['bitcoin', 'ethereum']
        
        try:
            log.info(f"获取市场数据: {coin_ids}")
            
            market_data = []
            for coin_id in coin_ids:
                price_data = self.get_crypto_price(coin_id)
                if price_data:
                    market_data.append(price_data)
                time.sleep(0.5)  # 避免API限制
            
            df = pd.DataFrame(market_data)
            log.info(f"✓ 获取{len(df)}个币种的市场数据")
            return df
            
        except Exception as e:
            log.error(f"获取市场数据失败: {e}")
            return None
    
    def get_historical_prices(
        self,
        coin_id: str,
        days: int = 30,
        vs_currency: str = 'usd'
    ) -> Optional[pd.DataFrame]:
        """
        获取历史价格数据
        
        Args:
            coin_id: 币种ID
            days: 天数，最多365天（免费API限制）
            vs_currency: 对比货币，'usd' 或 'cny'
            
        Returns:
            DataFrame包含历史价格数据
        """
        coin_id = self._normalize_coin_id(coin_id)
        
        try:
            log.info(f"获取{coin_id}历史数据，天数: {days}")
            
            if self.data_source == 'coingecko':
                df = self._get_history_coingecko(coin_id, days, vs_currency)
            else:
                df = self._get_history_binance(coin_id, days)
            
            log.info(f"✓ 获取{coin_id}历史数据成功，共{len(df)}条")
            return df
            
        except Exception as e:
            log.error(f"获取{coin_id}历史数据失败: {e}")
            return None
    
    def _get_history_coingecko(self, coin_id: str, days: int, vs_currency: str) -> pd.DataFrame:
        """使用CoinGecko获取历史数据"""
        url = f"{self.coingecko_base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 解析价格数据
        prices = data['prices']
        volumes = data['total_volumes']
        market_caps = data['market_caps']
        
        df = pd.DataFrame({
            'timestamp': [p[0] for p in prices],
            'price': [p[1] for p in prices],
            'volume': [v[1] for v in volumes],
            'market_cap': [m[1] for m in market_caps]
        })
        
        # 转换时间戳
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop('timestamp', axis=1)
        
        # 重新排列列
        df = df[['date', 'price', 'volume', 'market_cap']]
        
        return df
    
    def _get_history_binance(self, symbol: str, days: int) -> pd.DataFrame:
        """使用Binance获取历史数据"""
        trading_pair = f"{symbol.upper()}USDT"
        
        # Binance klines数据
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        klines = self.binance_client.get_historical_klines(
            trading_pair,
            '1d',  # 日线
            start_time
        )
        
        # 转换为DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # 转换数据类型
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['price'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # 选择需要的列
        df = df[['date', 'price', 'volume']]
        df['market_cap'] = None
        
        return df
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """
        获取加密货币恐惧贪婪指数
        
        Returns:
            {
                'value': 指数值(0-100),
                'classification': 分类('Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'),
                'timestamp': 时间戳
            }
        """
        cache_key = "fear_greed_index"
        if cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < 3600:  # 恐惧贪婪指数缓存1小时
                log.debug("从缓存获取恐惧贪婪指数")
                return cache_data
        
        try:
            log.info("获取恐惧贪婪指数...")
            
            # 使用Alternative.me的免费API
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()['data'][0]
            
            result = {
                'value': int(data['value']),
                'classification': data['value_classification'],
                'timestamp': data['timestamp']
            }
            
            # 更新缓存
            self._cache[cache_key] = (result, time.time())
            
            log.info(f"✓ 恐惧贪婪指数: {result['value']} ({result['classification']})")
            return result
            
        except Exception as e:
            log.error(f"获取恐惧贪婪指数失败: {e}")
            return None
    
    def _normalize_coin_id(self, symbol: str) -> str:
        """标准化币种ID"""
        symbol = symbol.upper()
        
        # 如果是常见符号，转换为CoinGecko ID
        if symbol in self.COIN_ID_MAP:
            return self.COIN_ID_MAP[symbol]
        
        # 否则转为小写作为ID
        return symbol.lower()
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        log.info("缓存已清除")


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=" * 60)
    print("加密货币数据获取模块测试")
    print("=" * 60)
    
    # 创建数据获取器
    fetcher = CryptoDataFetcher(data_source='coingecko')
    
    # 测试BTC
    print("\n1. 测试获取BTC价格...")
    btc_price = fetcher.get_crypto_price('BTC')
    if btc_price:
        print(f"   名称: {btc_price['name']}")
        print(f"   价格: ${btc_price['price_usd']:,.2f}")
        print(f"   24h涨跌: {btc_price['change_24h']:.2f}%")
        print(f"   24h成交量: ${btc_price['volume_24h']:,.0f}")
        print(f"   市值: ${btc_price['market_cap']:,.0f}")
    
    # 测试多币种
    print("\n2. 测试获取多币种数据...")
    market_data = fetcher.get_market_data(['bitcoin', 'ethereum', 'binancecoin'])
    if market_data is not None:
        print(f"   获取{len(market_data)}个币种数据")
        print(market_data[['symbol', 'price_usd', 'change_24h']])
    
    # 测试历史数据
    print("\n3. 测试获取BTC历史数据...")
    hist_data = fetcher.get_historical_prices('bitcoin', days=7)
    if hist_data is not None:
        print(f"   数据条数: {len(hist_data)}")
        print(f"   日期范围: {hist_data['date'].min()} - {hist_data['date'].max()}")
        print(f"\n   最近数据:")
        print(hist_data.tail())
    
    # 测试恐惧贪婪指数
    print("\n4. 测试获取恐惧贪婪指数...")
    fng = fetcher.get_fear_greed_index()
    if fng:
        print(f"   指数值: {fng['value']}")
        print(f"   分类: {fng['classification']}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

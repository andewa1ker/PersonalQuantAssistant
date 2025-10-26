"""
加密货币多数据源获取模块
支持4个数据源的混合策略:
1. CoinGecko (主力,免费)
2. Binance (备用1,需要API key)
3. CoinMarketCap (备用2,免费)
4. CryptoCompare (备用3,免费)
"""
import pandas as pd
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from pathlib import Path
import sys
import random

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.utils.config_loader import get_config

try:
    from src.utils.logger import log
except ImportError:
    import logging
    log = logging.getLogger(__name__)


class MultiSourceCryptoFetcher:
    """加密货币多数据源获取器"""
    
    # 币种ID映射
    COIN_ID_MAP = {
        'BTC': {'coingecko': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
        'ETH': {'coingecko': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
        'BNB': {'coingecko': 'binancecoin', 'symbol': 'BNB', 'name': 'Binance Coin'},
        'SOL': {'coingecko': 'solana', 'symbol': 'SOL', 'name': 'Solana'},
        'ADA': {'coingecko': 'cardano', 'symbol': 'ADA', 'name': 'Cardano'},
        'XRP': {'coingecko': 'ripple', 'symbol': 'XRP', 'name': 'Ripple'},
        'DOT': {'coingecko': 'polkadot', 'symbol': 'DOT', 'name': 'Polkadot'},
        'DOGE': {'coingecko': 'dogecoin', 'symbol': 'DOGE', 'name': 'Dogecoin'},
        'MATIC': {'coingecko': 'matic-network', 'symbol': 'MATIC', 'name': 'Polygon'},
        'AVAX': {'coingecko': 'avalanche-2', 'symbol': 'AVAX', 'name': 'Avalanche'}
    }
    
    def __init__(self, db_path: str = None):
        """
        初始化多数据源加密货币获取器
        
        Args:
            db_path: 数据库路径
        """
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 数据库配置
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / 'crypto_cache.db')
        
        self.db_path = db_path
        self._init_database()
        
        # API配置
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coinmarketcap_base = "https://pro-api.coinmarketcap.com/v1"
        self.cryptocompare_base = "https://min-api.cryptocompare.com/data"
        
        # 获取API密钥
        self.coinmarketcap_key = self.config.get_api_key('coinmarketcap', 'api_key')
        self.cryptocompare_key = self.config.get_api_key('cryptocompare', 'api_key')
        
        # 重试配置
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # 指数退避
        self.timeout = 30
        
        log.info("MultiSourceCryptoFetcher初始化完成")
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 实时价格缓存表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crypto_realtime (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    price_usd REAL,
                    price_cny REAL,
                    change_24h REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 历史数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crypto_history (
                    symbol TEXT,
                    date DATE,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_crypto_realtime_timestamp ON crypto_realtime(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_crypto_history_symbol_date ON crypto_history(symbol, date)")
            
            conn.commit()
            conn.close()
            
            log.info(f"✓ 加密货币数据库初始化完成: {self.db_path}")
            
        except Exception as e:
            log.error(f"数据库初始化失败: {e}")
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取加密货币实时价格 (多数据源混合策略)
        
        策略:
        1. 检查数据库缓存 (5分钟有效)
        2. CoinGecko (主力,免费)
        3. CoinMarketCap (备用1)
        4. CryptoCompare (备用2)
        5. 降级到旧缓存 (24小时内)
        
        Args:
            symbol: 币种符号,如 'BTC', 'ETH' 或 'bitcoin', 'ethereum'
            
        Returns:
            价格数据字典
        """
        # 标准化币种符号
        symbol_upper = symbol.upper()
        
        # 检查是否是CoinGecko ID格式(小写)
        if symbol.islower():
            # 转换为符号
            for sym, info in self.COIN_ID_MAP.items():
                if info['coingecko'] == symbol:
                    symbol_upper = sym
                    break
        
        # 1. 尝试从数据库获取缓存
        cached_data = self._get_from_database(symbol_upper, cache_minutes=5)
        if cached_data:
            log.info(f"✓ 从数据库获取{symbol_upper}数据 (缓存)")
            return cached_data
        
        # 2. 尝试多个数据源
        sources = [
            ('coingecko', self._fetch_coingecko_realtime),
            ('coinmarketcap', self._fetch_coinmarketcap_realtime),
            ('cryptocompare', self._fetch_cryptocompare_realtime)
        ]
        
        for source_name, fetch_func in sources:
            for retry in range(self.max_retries):
                try:
                    log.info(f"尝试从{source_name}获取{symbol_upper}数据...")
                    
                    data = fetch_func(symbol_upper)
                    
                    if data:
                        log.info(f"✓ {symbol_upper}数据获取成功 (来源: {source_name})")
                        
                        # 保存到数据库
                        self._save_to_database(data, source_name)
                        
                        return data
                    
                except Exception as e:
                    log.warning(f"✗ {source_name}获取失败: {e}")
                    
                    if retry < self.max_retries - 1:
                        delay = self.retry_delays[retry]
                        log.info(f"等待{delay}秒后重试...")
                        time.sleep(delay)
            
            # 每个源之间随机间隔
            time.sleep(random.uniform(0.5, 1.5))
        
        # 3. 所有源都失败,尝试使用旧缓存
        old_cached = self._get_from_database(symbol_upper, cache_minutes=1440)  # 24小时
        if old_cached:
            log.warning(f"⚠ 使用{symbol_upper}旧缓存数据 (24小时内)")
            old_cached['is_old_cache'] = True
            return old_cached
        
        log.error(f"✗ 所有数据源均失败: {symbol_upper}")
        return None
    
    def _fetch_coingecko_realtime(self, symbol: str) -> Optional[Dict[str, Any]]:
        """使用CoinGecko获取实时价格"""
        # 获取币种ID
        coin_info = self.COIN_ID_MAP.get(symbol)
        if not coin_info:
            raise ValueError(f"不支持的币种: {symbol}")
        
        coin_id = coin_info['coingecko']
        
        url = f"{self.coingecko_base}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd,cny',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if coin_id not in data:
            return None
        
        coin_data = data[coin_id]
        
        return {
            'symbol': symbol,
            'name': coin_info['name'],
            'price_usd': float(coin_data.get('usd', 0)),
            'price_cny': float(coin_data.get('cny', 0)),
            'change_24h': float(coin_data.get('usd_24h_change', 0)),
            'volume_24h': float(coin_data.get('usd_24h_vol', 0)),
            'market_cap': float(coin_data.get('usd_market_cap', 0)),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _fetch_coinmarketcap_realtime(self, symbol: str) -> Optional[Dict[str, Any]]:
        """使用CoinMarketCap获取实时价格"""
        if not self.coinmarketcap_key:
            raise ValueError("未配置CoinMarketCap API密钥")
        
        coin_info = self.COIN_ID_MAP.get(symbol)
        if not coin_info:
            raise ValueError(f"不支持的币种: {symbol}")
        
        url = f"{self.coinmarketcap_base}/cryptocurrency/quotes/latest"
        headers = {
            'X-CMC_PRO_API_KEY': self.coinmarketcap_key,
            'Accept': 'application/json'
        }
        params = {
            'symbol': symbol,
            'convert': 'USD,CNY'
        }
        
        response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if symbol not in data['data']:
            return None
        
        coin_data = data['data'][symbol]
        quote_usd = coin_data['quote']['USD']
        quote_cny = coin_data['quote']['CNY']
        
        return {
            'symbol': symbol,
            'name': coin_data['name'],
            'price_usd': float(quote_usd['price']),
            'price_cny': float(quote_cny['price']),
            'change_24h': float(quote_usd['percent_change_24h']),
            'volume_24h': float(quote_usd['volume_24h']),
            'market_cap': float(quote_usd['market_cap']),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _fetch_cryptocompare_realtime(self, symbol: str) -> Optional[Dict[str, Any]]:
        """使用CryptoCompare获取实时价格"""
        coin_info = self.COIN_ID_MAP.get(symbol)
        if not coin_info:
            raise ValueError(f"不支持的币种: {symbol}")
        
        # 获取价格
        url = f"{self.cryptocompare_base}/pricemultifull"
        params = {
            'fsyms': symbol,
            'tsyms': 'USD,CNY'
        }
        
        if self.cryptocompare_key:
            params['api_key'] = self.cryptocompare_key
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if 'RAW' not in data or symbol not in data['RAW']:
            return None
        
        raw_data = data['RAW'][symbol]
        usd_data = raw_data['USD']
        cny_data = raw_data['CNY']
        
        return {
            'symbol': symbol,
            'name': coin_info['name'],
            'price_usd': float(usd_data['PRICE']),
            'price_cny': float(cny_data['PRICE']),
            'change_24h': float(usd_data['CHANGEPCT24HOUR']),
            'volume_24h': float(usd_data['VOLUME24HOUR']),
            'market_cap': float(usd_data.get('MKTCAP', 0)),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_history_data(
        self,
        symbol: str,
        days: int = 90,
        vs_currency: str = 'usd'
    ) -> Optional[pd.DataFrame]:
        """
        获取历史数据 (多数据源混合策略)
        
        Args:
            symbol: 币种符号或ID (如 'BTC', 'bitcoin')
            days: 天数
            vs_currency: 对比货币
            
        Returns:
            历史数据DataFrame
        """
        # 标准化币种符号
        symbol_upper = symbol.upper()
        
        # 检查是否是CoinGecko ID格式(小写)
        if symbol.islower():
            # 转换为符号
            for sym, info in self.COIN_ID_MAP.items():
                if info['coingecko'] == symbol:
                    symbol_upper = sym
                    break
        
        # 1. 尝试从数据库获取
        cached_df = self._get_history_from_database(symbol_upper, days)
        if cached_df is not None and len(cached_df) >= days * 0.8:  # 至少80%数据
            log.info(f"✓ 从数据库获取{symbol_upper}历史数据")
            return cached_df
        
        # 2. 尝试多个数据源
        sources = [
            ('coingecko', self._fetch_coingecko_history),
            ('cryptocompare', self._fetch_cryptocompare_history)
        ]
        
        for source_name, fetch_func in sources:
            try:
                log.info(f"尝试从{source_name}获取{symbol_upper}历史数据...")
                
                df = fetch_func(symbol_upper, days, vs_currency)
                
                if df is not None and len(df) > 0:
                    log.info(f"✓ {symbol_upper}历史数据获取成功 (来源: {source_name})")
                    
                    # 保存到数据库
                    self._save_history_to_database(df, symbol_upper, source_name)
                    
                    return df
                
            except Exception as e:
                log.warning(f"✗ {source_name}历史数据获取失败: {e}")
            
            time.sleep(random.uniform(0.5, 1.5))
        
        # 返回缓存数据(即使不完整)
        if cached_df is not None:
            log.warning(f"⚠ 使用{symbol_upper}不完整的历史数据")
            return cached_df
        
        log.error(f"✗ 所有数据源均失败: {symbol_upper} 历史数据")
        return None
    
    def _fetch_coingecko_history(
        self,
        symbol: str,
        days: int,
        vs_currency: str
    ) -> Optional[pd.DataFrame]:
        """使用CoinGecko获取历史数据"""
        coin_info = self.COIN_ID_MAP.get(symbol)
        if not coin_info:
            return None
        
        coin_id = coin_info['coingecko']
        
        url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # 解析OHLCV数据
        prices = data['prices']
        volumes = data['total_volumes']
        
        df = pd.DataFrame({
            'timestamp': [p[0] for p in prices],
            'close': [p[1] for p in prices],
            'volume': [v[1] for v in volumes]
        })
        
        # 转换时间戳
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop('timestamp', axis=1)
        
        # CoinGecko没有OHLC,用close填充
        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        
        # 重新排列列
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df = df.set_index('date')
        
        return df
    
    def _fetch_cryptocompare_history(
        self,
        symbol: str,
        days: int,
        vs_currency: str
    ) -> Optional[pd.DataFrame]:
        """使用CryptoCompare获取历史数据"""
        url = f"{self.cryptocompare_base}/v2/histoday"
        params = {
            'fsym': symbol,
            'tsym': vs_currency.upper(),
            'limit': days
        }
        
        if self.cryptocompare_key:
            params['api_key'] = self.cryptocompare_key
        
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if data['Response'] != 'Success':
            return None
        
        hist_data = data['Data']['Data']
        
        df = pd.DataFrame(hist_data)
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df = df[['date', 'open', 'high', 'low', 'close', 'volumefrom']]
        df = df.rename(columns={'volumefrom': 'volume'})
        df = df.set_index('date')
        
        return df
    
    def _get_from_database(self, symbol: str, cache_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """从数据库获取实时数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询最近的数据
            cursor.execute("""
                SELECT symbol, name, price_usd, price_cny, change_24h, volume_24h, market_cap, source, timestamp
                FROM crypto_realtime
                WHERE symbol = ?
                AND datetime(timestamp) > datetime('now', '-' || ? || ' minutes')
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol, cache_minutes))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'symbol': row[0],
                    'name': row[1],
                    'price_usd': row[2],
                    'price_cny': row[3],
                    'change_24h': row[4],
                    'volume_24h': row[5],
                    'market_cap': row[6],
                    'source': row[7],
                    'timestamp': row[8]
                }
            
            return None
            
        except Exception as e:
            log.error(f"从数据库读取失败: {e}")
            return None
    
    def _save_to_database(self, data: Dict[str, Any], source: str):
        """保存实时数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO crypto_realtime
                (symbol, name, price_usd, price_cny, change_24h, volume_24h, market_cap, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                data['symbol'],
                data['name'],
                data['price_usd'],
                data['price_cny'],
                data['change_24h'],
                data['volume_24h'],
                data['market_cap'],
                source
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log.error(f"保存到数据库失败: {e}")
    
    def _get_history_from_database(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """从数据库获取历史数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            df = pd.read_sql_query("""
                SELECT date, open, high, low, close, volume
                FROM crypto_history
                WHERE symbol = ?
                AND date >= ?
                ORDER BY date
            """, conn, params=(symbol, start_date))
            
            conn.close()
            
            if len(df) > 0:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                return df
            
            return None
            
        except Exception as e:
            log.error(f"从数据库读取历史数据失败: {e}")
            return None
    
    def _save_history_to_database(self, df: pd.DataFrame, symbol: str, source: str):
        """保存历史数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            df_reset = df.reset_index()
            
            for _, row in df_reset.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO crypto_history
                    (symbol, date, open, high, low, close, volume, source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    symbol,
                    row['date'].strftime('%Y-%m-%d'),
                    row['open'],
                    row['high'],
                    row['low'],
                    row['close'],
                    row['volume'],
                    source
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log.error(f"保存历史数据到数据库失败: {e}")
    
    def get_market_data(self, coin_list: List[str] = None) -> Optional[pd.DataFrame]:
        """
        获取多个币种的市场数据
        
        Args:
            coin_list: 币种列表
            
        Returns:
            市场数据DataFrame
        """
        if coin_list is None:
            coin_list = list(self.COIN_ID_MAP.keys())[:5]  # 默认前5个
        
        try:
            log.info(f"获取市场数据: {coin_list}")
            
            market_data = []
            for symbol in coin_list:
                price_data = self.get_realtime_price(symbol)
                if price_data:
                    market_data.append(price_data)
                time.sleep(0.5)
            
            df = pd.DataFrame(market_data)
            log.info(f"✓ 获取{len(df)}个币种的市场数据")
            return df
            
        except Exception as e:
            log.error(f"获取市场数据失败: {e}")
            return None
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """
        获取加密货币恐惧贪婪指数
        
        Returns:
            恐惧贪婪指数数据
        """
        try:
            log.info("获取恐惧贪婪指数...")
            
            url = "https://api.alternative.me/fng/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()['data'][0]
            
            result = {
                'value': int(data['value']),
                'classification': data['value_classification'],
                'timestamp': data['timestamp']
            }
            
            log.info(f"✓ 恐惧贪婪指数: {result['value']} ({result['classification']})")
            return result
            
        except Exception as e:
            log.error(f"获取恐惧贪婪指数失败: {e}")
            return None
    
    def clear_old_cache(self, days: int = 30):
        """清理旧缓存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 清理实时数据
            cursor.execute("""
                DELETE FROM crypto_realtime
                WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            realtime_deleted = cursor.rowcount
            
            # 清理历史数据
            cursor.execute("""
                DELETE FROM crypto_history
                WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            history_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            log.info(f"✓ 清理旧缓存: 实时数据{realtime_deleted}条, 历史数据{history_deleted}条")
            return realtime_deleted + history_deleted
            
        except Exception as e:
            log.error(f"清理缓存失败: {e}")
            return 0


# ===== 测试代码 =====
if __name__ == "__main__":
    print("=" * 60)
    print("加密货币多数据源获取器测试")
    print("=" * 60)
    
    fetcher = MultiSourceCryptoFetcher()
    
    # 测试BTC实时价格
    print("\n1. 测试BTC实时价格...")
    btc_data = fetcher.get_realtime_price('BTC')
    if btc_data:
        print(f"   价格: ${btc_data['price_usd']:,.2f}")
        print(f"   24h涨跌: {btc_data['change_24h']:.2f}%")
        print(f"   来源: {btc_data.get('source', 'N/A')}")
    
    # 测试ETH历史数据
    print("\n2. 测试ETH历史数据...")
    eth_hist = fetcher.get_history_data('ETH', days=7)
    if eth_hist is not None:
        print(f"   数据条数: {len(eth_hist)}")
        print(f"   最新价格: ${eth_hist['close'].iloc[-1]:,.2f}")
    
    # 测试市场数据
    print("\n3. 测试市场数据...")
    market = fetcher.get_market_data(['BTC', 'ETH', 'BNB'])
    if market is not None:
        print(f"   获取{len(market)}个币种")
        print(market[['symbol', 'price_usd', 'change_24h']])
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

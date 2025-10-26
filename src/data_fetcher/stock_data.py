"""
股票/ETF数据获取模块
支持AKShare和Tushare双数据源
主要用于获取513500等A股ETF数据
"""
import pandas as pd
import numpy as np
import akshare as ak
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


class StockDataFetcher:
    """股票/ETF数据获取器"""
    
    def __init__(self, data_source: str = 'akshare'):
        """
        初始化数据获取器
        
        Args:
            data_source: 数据源，'akshare' 或 'tushare'
        """
        self.config = get_config()
        self.data_source = data_source
        self._cache = {}
        self._cache_timeout = self.config.get('app.cache_ttl', 3600)
        
        # 数据获取配置
        self.retry_times = self.config.get('app.data_fetch.retry_times', 3)
        self.retry_delay = self.config.get('app.data_fetch.retry_delay', 1)
        self.use_mock_on_fail = self.config.get('app.data_fetch.use_mock_on_fail', True)
        self.use_cached_on_fail = self.config.get('app.data_fetch.use_cached_on_fail', True)
        
        # 初始化Tushare（如果需要）
        if data_source == 'tushare':
            self._init_tushare()
        
        log.info(f"StockDataFetcher初始化完成，数据源: {data_source}")
    
    def _init_tushare(self):
        """初始化Tushare接口"""
        try:
            import tushare as ts
            token = self.config.get_api_key('tushare', 'token')
            if token:
                ts.set_token(token)
                self.ts_pro = ts.pro_api()
                log.info("Tushare接口初始化成功")
            else:
                log.warning("未配置Tushare token，将使用AKShare")
                self.data_source = 'akshare'
        except ImportError:
            log.warning("Tushare未安装，将使用AKShare")
            self.data_source = 'akshare'
        except Exception as e:
            log.error(f"Tushare初始化失败: {e}")
            self.data_source = 'akshare'
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时价格数据
        
        Args:
            symbol: 股票/ETF代码，如 '513500' 或 '513500.SH'
            
        Returns:
            包含实时价格信息的字典，或None（如果失败）
            {
                'symbol': 代码,
                'name': 名称,
                'price': 最新价,
                'change': 涨跌额,
                'change_pct': 涨跌幅(%),
                'volume': 成交量,
                'amount': 成交额,
                'open': 开盘价,
                'high': 最高价,
                'low': 最低价,
                'pre_close': 昨收价,
                'timestamp': 时间戳
            }
        """
        # 标准化代码
        symbol = self._normalize_symbol(symbol)
        
        # 检查缓存
        cache_key = f"realtime_{symbol}"
        if cache_key in self._cache:
            cache_data, cache_time = self._cache[cache_key]
            if time.time() - cache_time < 60:  # 实时数据缓存1分钟
                log.debug(f"从缓存获取{symbol}实时数据")
                return cache_data
        
        try:
            log.info(f"获取{symbol}实时价格...")
            
            # 尝试多次获取数据
            for attempt in range(self.retry_times):
                try:
                    if self.data_source == 'akshare':
                        data = self._get_realtime_akshare(symbol)
                    else:
                        data = self._get_realtime_tushare(symbol)
                    
                    # 更新缓存
                    self._cache[cache_key] = (data, time.time())
                    
                    log.info(f"✓ {symbol}实时价格: {data.get('price', 'N/A')}")
                    return data
                    
                except Exception as retry_error:
                    if attempt < self.retry_times - 1:  # 不是最后一次，继续重试
                        log.warning(f"获取{symbol}失败(尝试{attempt+1}/{self.retry_times}): {retry_error}")
                        time.sleep(self.retry_delay)
                    else:
                        raise  # 最后一次失败则抛出异常
            
        except Exception as e:
            log.error(f"获取{symbol}实时价格失败: {e}")
            
            # 策略1: 尝试返回缓存数据(即使过期)
            if self.use_cached_on_fail and cache_key in self._cache:
                old_data, _ = self._cache[cache_key]
                log.warning(f"✓ 使用过期缓存数据: {symbol}")
                old_data['is_cached'] = True
                return old_data
            
            # 策略2: 返回模拟数据
            if self.use_mock_on_fail:
                log.warning(f"✓ 使用模拟数据: {symbol}")
                return self._get_mock_realtime_data(symbol)
            
            # 策略3: 返回None
            return None
    
    def _get_realtime_akshare(self, symbol: str) -> Dict[str, Any]:
        """使用AKShare获取实时数据"""
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 查找对应代码
        stock_data = df[df['代码'] == symbol]
        
        if stock_data.empty:
            raise ValueError(f"未找到代码 {symbol} 的数据")
        
        row = stock_data.iloc[0]
        
        return {
            'symbol': symbol,
            'name': row['名称'],
            'price': float(row['最新价']),
            'change': float(row['涨跌额']),
            'change_pct': float(row['涨跌幅']),
            'volume': float(row['成交量']),
            'amount': float(row['成交额']),
            'open': float(row['今开']),
            'high': float(row['最高']),
            'low': float(row['最低']),
            'pre_close': float(row['昨收']),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_realtime_tushare(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取实时数据"""
        # Tushare需要转换代码格式
        ts_symbol = self._to_tushare_symbol(symbol)
        
        # 获取实时行情
        df = self.ts_pro.daily(ts_code=ts_symbol, trade_date=datetime.now().strftime('%Y%m%d'))
        
        if df.empty:
            # 如果今天没有数据，获取最近一个交易日
            df = self.ts_pro.daily(ts_code=ts_symbol)
            df = df.head(1)
        
        if df.empty:
            raise ValueError(f"未找到代码 {ts_symbol} 的数据")
        
        row = df.iloc[0]
        
        return {
            'symbol': symbol,
            'name': ts_symbol,
            'price': float(row['close']),
            'change': float(row['change']),
            'change_pct': float(row['pct_chg']),
            'volume': float(row['vol']) * 100,  # Tushare单位是手
            'amount': float(row['amount']) * 1000,  # Tushare单位是千元
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'pre_close': float(row['pre_close']),
            'timestamp': row['trade_date']
        }
    
    def get_history_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = '1y'
    ) -> Optional[pd.DataFrame]:
        """
        获取历史数据
        
        Args:
            symbol: 股票/ETF代码
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            period: 时间周期，如 '1d', '1w', '1mo', '1y', '5y'
            
        Returns:
            DataFrame包含OHLCV数据，列名：
            ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        """
        symbol = self._normalize_symbol(symbol)
        
        # 解析时间周期
        if start_date is None:
            start_date = self._parse_period(period)
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = end_date.replace('-', '')
        
        start_date = start_date.replace('-', '')
        
        try:
            log.info(f"获取{symbol}历史数据: {start_date} - {end_date}")
            
            # 尝试多次获取数据
            for attempt in range(self.retry_times):
                try:
                    if self.data_source == 'akshare':
                        df = self._get_history_akshare(symbol, start_date, end_date)
                    else:
                        df = self._get_history_tushare(symbol, start_date, end_date)
                    
                    log.info(f"✓ 获取{symbol}历史数据成功，共{len(df)}条")
                    return df
                    
                except Exception as retry_error:
                    if attempt < self.retry_times - 1:
                        log.warning(f"获取{symbol}历史数据失败(尝试{attempt+1}/{self.retry_times}): {retry_error}")
                        time.sleep(self.retry_delay)
                    else:
                        raise
            
        except Exception as e:
            log.error(f"获取{symbol}历史数据失败: {e}")
            
            # 使用模拟数据
            if self.use_mock_on_fail:
                log.warning(f"✓ 使用模拟历史数据: {symbol}")
                return self._get_mock_history_data(symbol, start_date, end_date)
            
            return None
    
    def _get_history_akshare(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用AKShare获取历史数据"""
        # 获取日线数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        
        if df.empty:
            raise ValueError(f"未获取到 {symbol} 的历史数据")
        
        # 标准化列名
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        })
        
        # 选择需要的列
        columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        df = df[columns]
        
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _get_history_tushare(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用Tushare获取历史数据"""
        ts_symbol = self._to_tushare_symbol(symbol)
        
        # 获取日线数据
        df = self.ts_pro.daily(
            ts_code=ts_symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            raise ValueError(f"未获取到 {ts_symbol} 的历史数据")
        
        # 标准化列名和单位
        df = df.rename(columns={
            'trade_date': 'date',
            'vol': 'volume',
        })
        
        df['volume'] = df['volume'] * 100  # 手转为股
        df['amount'] = df['amount'] * 1000  # 千元转为元
        
        # 选择需要的列
        columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        df = df[columns]
        
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def get_valuation_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取估值数据
        
        Args:
            symbol: 股票/ETF代码
            
        Returns:
            估值数据字典: {
                'pe': 市盈率,
                'pb': 市净率,
                'pe_percentile': PE历史分位数,
                'pb_percentile': PB历史分位数
            }
        """
        symbol = self._normalize_symbol(symbol)
        
        try:
            log.info(f"获取{symbol}估值数据...")
            
            # 获取最新估值
            if self.data_source == 'akshare':
                data = self._get_valuation_akshare(symbol)
            else:
                data = self._get_valuation_tushare(symbol)
            
            log.info(f"✓ {symbol}估值数据获取成功")
            return data
            
        except Exception as e:
            log.error(f"获取{symbol}估值数据失败: {e}")
            return None
    
    def _get_valuation_akshare(self, symbol: str) -> Dict[str, Any]:
        """使用AKShare获取估值数据"""
        # AKShare的估值数据获取相对复杂，这里提供基础实现
        try:
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=symbol)
            
            valuation = {}
            for _, row in df.iterrows():
                item = row['item']
                value_str = row['value']
                
                if item == '市盈率-动态':
                    try:
                        valuation['pe'] = float(value_str)
                    except:
                        valuation['pe'] = None
                elif item == '市净率':
                    try:
                        valuation['pb'] = float(value_str)
                    except:
                        valuation['pb'] = None
            
            # 计算历史分位数（需要历史PE/PB数据，这里简化处理）
            valuation['pe_percentile'] = None
            valuation['pb_percentile'] = None
            
            return valuation
            
        except Exception as e:
            log.warning(f"AKShare获取估值数据失败: {e}，返回默认值")
            return {'pe': None, 'pb': None, 'pe_percentile': None, 'pb_percentile': None}
    
    def _get_valuation_tushare(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取估值数据"""
        ts_symbol = self._to_tushare_symbol(symbol)
        
        # 获取最新日期
        today = datetime.now().strftime('%Y%m%d')
        
        # 获取每日指标
        df = self.ts_pro.daily_basic(
            ts_code=ts_symbol,
            start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
            end_date=today,
            fields='ts_code,trade_date,pe,pb'
        )
        
        if df.empty:
            return {'pe': None, 'pb': None, 'pe_percentile': None, 'pb_percentile': None}
        
        # 获取最新数据
        latest = df.iloc[0]
        
        return {
            'pe': float(latest['pe']) if pd.notna(latest['pe']) else None,
            'pb': float(latest['pb']) if pd.notna(latest['pb']) else None,
            'pe_percentile': None,  # 需要更多历史数据计算
            'pb_percentile': None
        }
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码，去除后缀"""
        return symbol.split('.')[0]
    
    def _to_tushare_symbol(self, symbol: str) -> str:
        """转换为Tushare格式的代码"""
        symbol = self._normalize_symbol(symbol)
        
        # 根据代码判断市场
        if symbol.startswith('6'):
            return f"{symbol}.SH"  # 上海
        elif symbol.startswith('0') or symbol.startswith('3'):
            return f"{symbol}.SZ"  # 深圳
        elif symbol.startswith('5'):
            # ETF，根据具体代码判断
            if symbol.startswith('51') or symbol.startswith('56'):
                return f"{symbol}.SH"
            else:
                return f"{symbol}.SZ"
        else:
            return f"{symbol}.SH"  # 默认上海
    
    def _parse_period(self, period: str) -> str:
        """解析时间周期为开始日期"""
        now = datetime.now()
        
        if period == '1d':
            start = now - timedelta(days=1)
        elif period == '1w':
            start = now - timedelta(weeks=1)
        elif period == '1mo':
            start = now - timedelta(days=30)
        elif period == '1y':
            start = now - timedelta(days=365)
        elif period == '5y':
            start = now - timedelta(days=365*5)
        else:
            # 默认1年
            start = now - timedelta(days=365)
        
        return start.strftime('%Y%m%d')
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        log.info("缓存已清除")
    
    def _get_mock_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """
        生成模拟实时数据(当API失败时使用)
        
        Args:
            symbol: 股票/ETF代码
            
        Returns:
            模拟的实时数据
        """
        # 根据不同ETF生成不同的基础价格
        base_prices = {
            '513500': 1.85,   # 标普500ETF
            '159915': 3.20,   # 纳斯达克100ETF
            '512690': 2.50,   # 酒ETF
            '159941': 2.80,   # 广发纳指100ETF
            '512880': 2.10,   # 证券ETF
        }
        
        base_price = base_prices.get(symbol, 2.0)
        
        # 添加随机波动
        price = base_price * (1 + np.random.uniform(-0.02, 0.02))
        change = np.random.uniform(-0.05, 0.05)
        
        return {
            'symbol': symbol,
            'name': f"ETF{symbol}",
            'price': round(price, 3),
            'change': round(change, 4),
            'change_pct': round(change * 100, 2),
            'volume': int(np.random.uniform(1000000, 10000000)),
            'amount': round(price * np.random.uniform(1000000, 10000000), 2),
            'open': round(price * (1 + np.random.uniform(-0.01, 0.01)), 3),
            'high': round(price * (1 + np.random.uniform(0, 0.02)), 3),
            'low': round(price * (1 - np.random.uniform(0, 0.02)), 3),
            'prev_close': round(price / (1 + change), 3),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_mock': True  # 标记为模拟数据
        }
    
    def _get_mock_history_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        生成模拟历史数据(当API失败时使用)
        
        Args:
            symbol: 股票/ETF代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            模拟的历史DataFrame
        """
        # 解析日期
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        
        # 生成日期序列(只包含工作日)
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 周一到周五
                dates.append(current)
            current += timedelta(days=1)
        
        # 根据不同ETF生成不同的基础价格
        base_prices = {
            '513500': 1.85,   # 标普500ETF
            '159915': 3.20,   # 纳斯达克100ETF
            '512690': 2.50,   # 酒ETF
            '159941': 2.80,   # 广发纳指100ETF
            '512880': 2.10,   # 证券ETF
        }
        
        base_price = base_prices.get(symbol, 2.0)
        
        # 生成模拟K线数据
        data = []
        price = base_price
        
        for date in dates:
            # 每日随机波动
            daily_change = np.random.uniform(-0.03, 0.03)
            open_price = price * (1 + np.random.uniform(-0.01, 0.01))
            high_price = max(open_price, price) * (1 + abs(np.random.uniform(0, 0.02)))
            low_price = min(open_price, price) * (1 - abs(np.random.uniform(0, 0.02)))
            close_price = price * (1 + daily_change)
            volume = int(np.random.uniform(1000000, 10000000))
            amount = close_price * volume
            
            data.append({
                'date': date,
                'open': round(open_price, 3),
                'high': round(high_price, 3),
                'low': round(low_price, 3),
                'close': round(close_price, 3),
                'volume': volume,
                'amount': round(amount, 2)
            })
            
            # 更新价格(加入趋势和均值回归)
            trend = np.random.uniform(-0.001, 0.001)
            mean_reversion = (base_price - price) * 0.05
            price = price * (1 + daily_change + trend) + mean_reversion
            price = max(price, base_price * 0.7)  # 不低于基础价格的70%
            price = min(price, base_price * 1.3)  # 不高于基础价格的130%
        
        df = pd.DataFrame(data)
        log.info(f"✓ 生成{symbol}模拟历史数据，共{len(df)}条")
        return df



# ===== 使用示例 =====
if __name__ == "__main__":
    print("=" * 60)
    print("股票/ETF数据获取模块测试")
    print("=" * 60)
    
    # 创建数据获取器
    fetcher = StockDataFetcher(data_source='akshare')
    
    # 测试513500
    symbol = '513500'
    
    print(f"\n1. 测试获取 {symbol} 实时价格...")
    price_data = fetcher.get_realtime_price(symbol)
    if price_data:
        print(f"   名称: {price_data['name']}")
        print(f"   最新价: {price_data['price']:.3f}")
        print(f"   涨跌幅: {price_data['change_pct']:.2f}%")
        print(f"   成交量: {price_data['volume']:,.0f}")
    
    print(f"\n2. 测试获取 {symbol} 历史数据...")
    hist_data = fetcher.get_history_data(symbol, period='1mo')
    if hist_data is not None:
        print(f"   数据条数: {len(hist_data)}")
        print(f"   日期范围: {hist_data['date'].min()} - {hist_data['date'].max()}")
        print(f"\n   最近5天数据:")
        print(hist_data.tail())
    
    print(f"\n3. 测试获取 {symbol} 估值数据...")
    val_data = fetcher.get_valuation_data(symbol)
    if val_data:
        print(f"   PE: {val_data.get('pe', 'N/A')}")
        print(f"   PB: {val_data.get('pb', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

"""
多数据源ETF数据获取器 - 混合策略
支持Tushare(主)、新浪财经、东方财富、AKShare(备用)
实现智能降级和数据库缓存
"""
import pandas as pd
import numpy as np
import requests
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import sys
import sqlite3
import json

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.utils.config_loader import get_config

try:
    from src.utils.logger import log
except ImportError:
    import logging
    log = logging.getLogger(__name__)


class MultiSourceETFFetcher:
    """多数据源ETF数据获取器"""
    
    def __init__(self, tushare_token: str = None):
        """
        初始化多数据源获取器
        
        Args:
            tushare_token: Tushare API Token
        """
        self.config = get_config()
        self.tushare_token = tushare_token or 'a4ee49df8870a77df1b14650059f7424dca109a038dc840741474798'
        
        # 初始化数据源
        self._init_tushare()
        self._init_database()
        
        # 数据源优先级
        self.source_priority = ['tushare', 'sina', 'eastmoney', 'akshare']
        
        # 请求配置
        self.timeout = 30  # 超时30秒
        self.max_retries = 3  # 最多重试3次
        self.retry_delay_base = 1  # 基础重试延迟
        self.request_interval = (0.5, 1.5)  # 请求间隔范围
        
        # Session复用
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        log.info("MultiSourceETFFetcher初始化完成")
    
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            import tushare as ts
            ts.set_token(self.tushare_token)
            self.ts_pro = ts.pro_api()
            log.info("✓ Tushare初始化成功")
        except ImportError:
            log.warning("✗ Tushare未安装，请运行: pip install tushare")
            self.ts_pro = None
        except Exception as e:
            log.error(f"✗ Tushare初始化失败: {e}")
            self.ts_pro = None
    
    def _init_database(self):
        """初始化SQLite数据库"""
        db_path = Path(__file__).parent.parent.parent / 'data' / 'etf_cache.db'
        db_path.parent.mkdir(exist_ok=True)
        
        self.db_path = str(db_path)
        
        # 创建表
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS etf_realtime (
                    symbol TEXT,
                    name TEXT,
                    price REAL,
                    change_pct REAL,
                    volume REAL,
                    amount REAL,
                    open REAL,
                    high REAL,
                    low REAL,
                    pre_close REAL,
                    source TEXT,
                    timestamp DATETIME,
                    PRIMARY KEY (symbol, timestamp)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS etf_history (
                    symbol TEXT,
                    date DATE,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    amount REAL,
                    source TEXT,
                    created_at DATETIME,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            
            # 创建索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_realtime_symbol ON etf_realtime(symbol)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_realtime_time ON etf_realtime(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_history_symbol ON etf_history(symbol)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_history_date ON etf_history(date)')
            
        log.info(f"✓ 数据库初始化完成: {self.db_path}")
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时价格 - 混合策略
        
        策略流程:
        1. 检查Streamlit缓存(已在cache_helper中处理)
        2. 尝试从数据库获取(5分钟内的数据)
        3. 按优先级尝试各数据源
        4. 存入数据库
        
        Args:
            symbol: ETF代码，如 '513500'
            
        Returns:
            实时价格数据字典
        """
        symbol = self._normalize_symbol(symbol)
        
        # 第1层: 数据库缓存(5分钟)
        db_data = self._get_from_database(symbol, minutes=5)
        if db_data:
            log.info(f"✓ 从数据库获取{symbol}数据 (缓存)")
            return db_data
        
        # 第2层: 多数据源获取
        for source in self.source_priority:
            try:
                log.info(f"尝试从{source}获取{symbol}数据...")
                
                if source == 'tushare':
                    data = self._fetch_tushare_realtime(symbol)
                elif source == 'sina':
                    data = self._fetch_sina_realtime(symbol)
                elif source == 'eastmoney':
                    data = self._fetch_eastmoney_realtime(symbol)
                elif source == 'akshare':
                    data = self._fetch_akshare_realtime(symbol)
                else:
                    continue
                
                if data:
                    # 存入数据库
                    self._save_to_database(symbol, data, data_type='realtime')
                    log.info(f"✓ {symbol}数据获取成功 (来源: {source})")
                    return data
                    
            except Exception as e:
                log.warning(f"✗ {source}获取失败: {e}")
                continue
        
        # 第3层: 使用旧缓存(24小时内)
        db_data = self._get_from_database(symbol, minutes=1440)
        if db_data:
            log.warning(f"⚠ 使用旧缓存数据: {symbol} (最后更新: {db_data.get('timestamp')})")
            db_data['is_cached'] = True
            return db_data
        
        log.error(f"✗ 所有数据源均失败: {symbol}")
        return None
    
    def get_history_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取历史数据 - 混合策略
        
        Args:
            symbol: ETF代码
            start_date: 开始日期 'YYYYMMDD'
            end_date: 结束日期 'YYYYMMDD'
            
        Returns:
            历史数据DataFrame
        """
        symbol = self._normalize_symbol(symbol)
        
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        # 尝试从数据库获取
        db_data = self._get_history_from_database(symbol, start_date, end_date)
        if db_data is not None and len(db_data) > 0:
            # 检查是否需要补充最新数据
            latest_date = pd.to_datetime(db_data['date'].max())
            days_diff = (datetime.now() - latest_date).days
            
            if days_diff <= 1:  # 数据足够新
                log.info(f"✓ 从数据库获取{symbol}历史数据 ({len(db_data)}条)")
                return db_data
        
        # 从数据源获取
        for source in self.source_priority:
            try:
                log.info(f"尝试从{source}获取{symbol}历史数据...")
                
                if source == 'tushare':
                    data = self._fetch_tushare_history(symbol, start_date, end_date)
                elif source == 'akshare':
                    data = self._fetch_akshare_history(symbol, start_date, end_date)
                else:
                    continue  # 新浪和东财的历史数据接口复杂，暂时跳过
                
                if data is not None and len(data) > 0:
                    # 存入数据库
                    self._save_history_to_database(symbol, data, source)
                    log.info(f"✓ {symbol}历史数据获取成功 (来源: {source}, {len(data)}条)")
                    return data
                    
            except Exception as e:
                log.warning(f"✗ {source}获取历史数据失败: {e}")
                continue
        
        # 返回数据库中的旧数据
        if db_data is not None and len(db_data) > 0:
            log.warning(f"⚠ 使用数据库旧数据: {symbol} ({len(db_data)}条)")
            return db_data
        
        log.error(f"✗ 所有数据源均失败: {symbol} 历史数据")
        return None
    
    # ==================== Tushare数据源 ====================
    
    def _fetch_tushare_realtime(self, symbol: str) -> Optional[Dict]:
        """从Tushare获取实时数据"""
        if not self.ts_pro:
            return None
        
        ts_symbol = self._to_tushare_symbol(symbol)
        
        for attempt in range(self.max_retries):
            try:
                self._sleep_random()
                
                # Tushare实时数据
                df = self.ts_pro.daily(ts_code=ts_symbol, start_date=datetime.now().strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
                
                if df.empty:
                    # 如果今天没有数据，获取最近一天
                    df = self.ts_pro.daily(ts_code=ts_symbol, end_date=datetime.now().strftime('%Y%m%d'))
                    if not df.empty:
                        df = df.head(1)
                
                if df.empty:
                    return None
                
                row = df.iloc[0]
                
                return {
                    'symbol': symbol,
                    'name': self._get_etf_name(symbol),
                    'price': float(row['close']),
                    'change': float(row['close'] - row['pre_close']),
                    'change_pct': float(row['pct_chg']),
                    'volume': float(row['vol']) * 100,  # 手转股
                    'amount': float(row['amount']) * 1000,  # 千元转元
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'pre_close': float(row['pre_close']),
                    'source': 'tushare',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2 ** attempt)
                    log.warning(f"Tushare重试 {attempt + 1}/{self.max_retries}，等待{delay}秒...")
                    time.sleep(delay)
                else:
                    raise e
        
        return None
    
    def _fetch_tushare_history(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从Tushare获取历史数据"""
        if not self.ts_pro:
            return None
        
        ts_symbol = self._to_tushare_symbol(symbol)
        
        for attempt in range(self.max_retries):
            try:
                self._sleep_random()
                
                df = self.ts_pro.fund_daily(ts_code=ts_symbol, start_date=start_date, end_date=end_date)
                
                if df.empty:
                    return None
                
                # 转换格式
                df = df.rename(columns={
                    'trade_date': 'date',
                    'vol': 'volume',
                })
                
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df['volume'] = df['volume'] * 100  # 手转股
                df['amount'] = df.get('amount', 0) * 1000  # 千元转元
                
                return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2 ** attempt)
                    log.warning(f"Tushare历史数据重试 {attempt + 1}/{self.max_retries}，等待{delay}秒...")
                    time.sleep(delay)
                else:
                    raise e
        
        return None
    
    # ==================== 新浪财经数据源 ====================
    
    def _fetch_sina_realtime(self, symbol: str) -> Optional[Dict]:
        """从新浪财经获取实时数据"""
        sina_symbol = self._to_sina_symbol(symbol)
        url = f"http://hq.sinajs.cn/list={sina_symbol}"
        
        for attempt in range(self.max_retries):
            try:
                self._sleep_random()
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # 解析数据
                content = response.text
                if 'var hq_str_' not in content:
                    return None
                
                data_str = content.split('="')[1].split('";')[0]
                parts = data_str.split(',')
                
                if len(parts) < 32:
                    return None
                
                price = float(parts[3])
                pre_close = float(parts[2])
                
                return {
                    'symbol': symbol,
                    'name': parts[0],
                    'price': price,
                    'change': price - pre_close,
                    'change_pct': ((price - pre_close) / pre_close * 100) if pre_close > 0 else 0,
                    'volume': float(parts[8]),
                    'amount': float(parts[9]),
                    'open': float(parts[1]),
                    'high': float(parts[4]),
                    'low': float(parts[5]),
                    'pre_close': pre_close,
                    'source': 'sina',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise e
        
        return None
    
    # ==================== 东方财富数据源 ====================
    
    def _fetch_eastmoney_realtime(self, symbol: str) -> Optional[Dict]:
        """从东方财富获取实时数据"""
        em_symbol = self._to_eastmoney_symbol(symbol)
        url = f"http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': em_symbol,
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f152,f162,f169,f170,f171'
        }
        
        for attempt in range(self.max_retries):
            try:
                self._sleep_random()
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                if data.get('rc') != 0 or not data.get('data'):
                    return None
                
                d = data['data']
                price = float(d.get('f43', 0)) / 100  # 价格/100
                pre_close = float(d.get('f60', 0)) / 100
                
                return {
                    'symbol': symbol,
                    'name': d.get('f58', ''),
                    'price': price,
                    'change': float(d.get('f169', 0)) / 100,
                    'change_pct': float(d.get('f170', 0)) / 100,
                    'volume': float(d.get('f47', 0)),
                    'amount': float(d.get('f48', 0)),
                    'open': float(d.get('f46', 0)) / 100,
                    'high': float(d.get('f44', 0)) / 100,
                    'low': float(d.get('f45', 0)) / 100,
                    'pre_close': pre_close,
                    'source': 'eastmoney',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise e
        
        return None
    
    # ==================== AKShare备用数据源 ====================
    
    def _fetch_akshare_realtime(self, symbol: str) -> Optional[Dict]:
        """从AKShare获取实时数据"""
        try:
            import akshare as ak
            
            self._sleep_random()
            
            # AKShare ETF实时数据
            df = ak.fund_etf_spot_em()
            
            # 查找对应代码
            row = df[df['代码'] == symbol]
            if row.empty:
                return None
            
            row = row.iloc[0]
            price = float(row['最新价'])
            pre_close = float(row['昨收'])
            
            return {
                'symbol': symbol,
                'name': str(row['名称']),
                'price': price,
                'change': price - pre_close,
                'change_pct': float(row['涨跌幅']),
                'volume': float(row['成交量']),
                'amount': float(row['成交额']),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'pre_close': pre_close,
                'source': 'akshare',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            log.warning(f"AKShare获取失败: {e}")
            return None
    
    def _fetch_akshare_history(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从AKShare获取历史数据"""
        try:
            import akshare as ak
            
            self._sleep_random()
            
            # 转换日期格式
            start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
            
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start, end_date=end, adjust="")
            
            if df.empty:
                return None
            
            # 转换格式
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            
        except Exception as e:
            log.warning(f"AKShare历史数据获取失败: {e}")
            return None
    
    # ==================== 数据库操作 ====================
    
    def _get_from_database(self, symbol: str, minutes: int = 5) -> Optional[Dict]:
        """从数据库获取实时数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM etf_realtime 
                    WHERE symbol = ? 
                    AND datetime(timestamp) > datetime('now', ?)
                    ORDER BY timestamp DESC 
                    LIMIT 1
                '''
                
                df = pd.read_sql_query(query, conn, params=(symbol, f'-{minutes} minutes'))
                
                if df.empty:
                    return None
                
                row = df.iloc[0]
                return {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'price': float(row['price']),
                    'change_pct': float(row['change_pct']),
                    'volume': float(row['volume']),
                    'amount': float(row['amount']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'pre_close': float(row['pre_close']),
                    'source': row['source'],
                    'timestamp': row['timestamp']
                }
        except Exception as e:
            log.warning(f"数据库读取失败: {e}")
            return None
    
    def _save_to_database(self, symbol: str, data: Dict, data_type: str = 'realtime'):
        """保存数据到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if data_type == 'realtime':
                    conn.execute('''
                        INSERT OR REPLACE INTO etf_realtime 
                        (symbol, name, price, change_pct, volume, amount, open, high, low, pre_close, source, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol,
                        data.get('name', ''),
                        data.get('price', 0),
                        data.get('change_pct', 0),
                        data.get('volume', 0),
                        data.get('amount', 0),
                        data.get('open', 0),
                        data.get('high', 0),
                        data.get('low', 0),
                        data.get('pre_close', 0),
                        data.get('source', ''),
                        data.get('timestamp', datetime.now().isoformat())
                    ))
                conn.commit()
        except Exception as e:
            log.warning(f"数据库写入失败: {e}")
    
    def _get_history_from_database(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从数据库获取历史数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM etf_history 
                    WHERE symbol = ? 
                    AND date >= ? 
                    AND date <= ?
                    ORDER BY date
                '''
                
                start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
                end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
                
                df = pd.read_sql_query(query, conn, params=(symbol, start, end))
                
                if df.empty:
                    return None
                
                df['date'] = pd.to_datetime(df['date'])
                return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        except Exception as e:
            log.warning(f"数据库历史数据读取失败: {e}")
            return None
    
    def _save_history_to_database(self, symbol: str, data: pd.DataFrame, source: str):
        """保存历史数据到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for _, row in data.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO etf_history 
                        (symbol, date, open, high, low, close, volume, amount, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol,
                        row['date'].strftime('%Y-%m-%d'),
                        float(row['open']),
                        float(row['high']),
                        float(row['low']),
                        float(row['close']),
                        float(row['volume']),
                        float(row.get('amount', 0)),
                        source,
                        datetime.now().isoformat()
                    ))
                conn.commit()
        except Exception as e:
            log.warning(f"数据库历史数据写入失败: {e}")
    
    # ==================== 工具函数 ====================
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        return symbol.replace('.SH', '').replace('.SZ', '').replace('.sh', '').replace('.sz', '')
    
    def _to_tushare_symbol(self, symbol: str) -> str:
        """转换为Tushare格式: 513500.SH"""
        symbol = self._normalize_symbol(symbol)
        # ETF一般都是上海交易所
        if symbol.startswith('51') or symbol.startswith('50') or symbol.startswith('56'):
            return f"{symbol}.SH"
        elif symbol.startswith('15') or symbol.startswith('16'):
            return f"{symbol}.SZ"
        else:
            return f"{symbol}.SH"  # 默认上海
    
    def _to_sina_symbol(self, symbol: str) -> str:
        """转换为新浪格式: sz159915 或 sh513500"""
        symbol = self._normalize_symbol(symbol)
        if symbol.startswith('51') or symbol.startswith('50') or symbol.startswith('56'):
            return f"sh{symbol}"
        else:
            return f"sz{symbol}"
    
    def _to_eastmoney_symbol(self, symbol: str) -> str:
        """转换为东方财富格式: 1.513500 或 0.159915"""
        symbol = self._normalize_symbol(symbol)
        if symbol.startswith('51') or symbol.startswith('50') or symbol.startswith('56'):
            return f"1.{symbol}"  # 上海
        else:
            return f"0.{symbol}"  # 深圳
    
    def _get_etf_name(self, symbol: str) -> str:
        """获取ETF名称"""
        names = {
            '513500': '标普500ETF',
            '159915': '创业板ETF',
            '512690': '酒ETF',
            '159941': '纳指100ETF',
            '510300': '300ETF',
            '510500': '500ETF',
        }
        return names.get(symbol, f'ETF{symbol}')
    
    def _sleep_random(self):
        """随机延迟，避免请求过快"""
        delay = random.uniform(*self.request_interval)
        time.sleep(delay)
    
    def clear_old_cache(self, days: int = 30):
        """清理旧缓存数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 清理旧的实时数据
                conn.execute('''
                    DELETE FROM etf_realtime 
                    WHERE datetime(timestamp) < datetime('now', ?)
                ''', (f'-{days} days',))
                
                # 清理旧的历史数据
                conn.execute('''
                    DELETE FROM etf_history 
                    WHERE datetime(created_at) < datetime('now', ?)
                ''', (f'-{days} days',))
                
                conn.commit()
            log.info(f"✓ 清理{days}天前的缓存数据")
        except Exception as e:
            log.warning(f"清理缓存失败: {e}")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                realtime_count = conn.execute('SELECT COUNT(*) FROM etf_realtime').fetchone()[0]
                history_count = conn.execute('SELECT COUNT(*) FROM etf_history').fetchone()[0]
                
                return {
                    'realtime_records': realtime_count,
                    'history_records': history_count,
                    'database_path': self.db_path
                }
        except Exception as e:
            return {'error': str(e)}

"""
数据库模块
使用SQLite存储历史数据
"""
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
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


class Database:
    """数据库管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径，None表示使用配置文件中的路径
        """
        self.config = get_config()
        
        if db_path is None:
            db_path = self.config.get('data.database.path', './data/quant.db')
        
        # 确保数据库目录存在
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # 创建表
        self._create_tables()
        
        log.info(f"数据库初始化完成: {self.db_path}")
    
    def _create_tables(self):
        """创建数据表"""
        
        # 股票/ETF历史数据表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        ''')
        
        # 股票/ETF估值数据表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_valuation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                pe REAL,
                pb REAL,
                pe_percentile REAL,
                pb_percentile REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        ''')
        
        # 加密货币历史数据表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                price REAL,
                volume REAL,
                market_cap REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        ''')
        
        # 交易信号表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_value REAL,
                signal_strength REAL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 持仓记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_cost REAL NOT NULL,
                current_price REAL,
                profit_loss REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 系统日志表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        log.info("数据表创建完成")
    
    def save_stock_history(self, symbol: str, df: pd.DataFrame) -> int:
        """
        保存股票历史数据
        
        Args:
            symbol: 股票代码
            df: 历史数据DataFrame
            
        Returns:
            插入的行数
        """
        try:
            count = 0
            for _, row in df.iterrows():
                self.cursor.execute('''
                    INSERT OR REPLACE INTO stock_history 
                    (symbol, date, open, high, low, close, volume, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else row['date'],
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close']),
                    float(row['volume']),
                    float(row.get('amount', 0))
                ))
                count += 1
            
            self.conn.commit()
            log.info(f"保存{symbol}历史数据{count}条")
            return count
            
        except Exception as e:
            log.error(f"保存{symbol}历史数据失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_stock_history(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 最大返回行数
            
        Returns:
            历史数据DataFrame
        """
        try:
            query = "SELECT date, open, high, low, close, volume, amount FROM stock_history WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += f" ORDER BY date DESC LIMIT {limit}"
            
            df = pd.read_sql_query(query, self.conn, params=params)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
            log.info(f"从数据库获取{symbol}历史数据{len(df)}条")
            return df
            
        except Exception as e:
            log.error(f"获取{symbol}历史数据失败: {e}")
            return None
    
    def save_crypto_history(self, symbol: str, df: pd.DataFrame) -> int:
        """保存加密货币历史数据"""
        try:
            count = 0
            for _, row in df.iterrows():
                self.cursor.execute('''
                    INSERT OR REPLACE INTO crypto_history 
                    (symbol, date, price, volume, market_cap)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], pd.Timestamp) else row['date'],
                    float(row['price']),
                    float(row['volume']),
                    float(row.get('market_cap', 0)) if pd.notna(row.get('market_cap')) else None
                ))
                count += 1
            
            self.conn.commit()
            log.info(f"保存{symbol}加密货币数据{count}条")
            return count
            
        except Exception as e:
            log.error(f"保存{symbol}加密货币数据失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_crypto_history(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> Optional[pd.DataFrame]:
        """获取加密货币历史数据"""
        try:
            query = "SELECT date, price, volume, market_cap FROM crypto_history WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += f" ORDER BY date DESC LIMIT {limit}"
            
            df = pd.read_sql_query(query, self.conn, params=params)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
            log.info(f"从数据库获取{symbol}加密货币数据{len(df)}条")
            return df
            
        except Exception as e:
            log.error(f"获取{symbol}加密货币数据失败: {e}")
            return None
    
    def save_trading_signal(
        self,
        asset_type: str,
        symbol: str,
        signal_type: str,
        signal_value: float,
        signal_strength: float,
        reason: str
    ) -> bool:
        """保存交易信号"""
        try:
            self.cursor.execute('''
                INSERT INTO trading_signals 
                (asset_type, symbol, signal_type, signal_value, signal_strength, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (asset_type, symbol, signal_type, signal_value, signal_strength, reason))
            
            self.conn.commit()
            log.info(f"保存{symbol}交易信号: {signal_type}")
            return True
            
        except Exception as e:
            log.error(f"保存交易信号失败: {e}")
            return False
    
    def get_latest_signals(self, limit: int = 10) -> Optional[pd.DataFrame]:
        """获取最新的交易信号"""
        try:
            query = '''
                SELECT asset_type, symbol, signal_type, signal_value, 
                       signal_strength, reason, created_at
                FROM trading_signals 
                ORDER BY created_at DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, self.conn, params=[limit])
            return df
            
        except Exception as e:
            log.error(f"获取交易信号失败: {e}")
            return None
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """备份数据库"""
        try:
            if backup_path is None:
                backup_path = str(self.db_path.parent / f"quant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            log.info(f"数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            log.error(f"数据库备份失败: {e}")
            return False
    
    def get_db_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        try:
            stats = {}
            
            tables = ['stock_history', 'stock_valuation', 'crypto_history', 
                     'trading_signals', 'positions', 'system_logs']
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                stats[table] = count
            
            return stats
            
        except Exception as e:
            log.error(f"获取数据库统计失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            log.info("数据库连接已关闭")
    
    def __del__(self):
        """析构函数"""
        self.close()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=" * 60)
    print("数据库模块测试")
    print("=" * 60)
    
    # 创建数据库
    db = Database()
    
    # 测试数据
    print("\n1. 测试保存股票历史数据...")
    test_df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5, freq='D'),
        'open': [100, 101, 102, 103, 104],
        'high': [101, 102, 103, 104, 105],
        'low': [99, 100, 101, 102, 103],
        'close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
        'amount': [100000000, 110000000, 120000000, 130000000, 140000000]
    })
    
    count = db.save_stock_history('TEST', test_df)
    print(f"   ✓ 保存{count}条数据")
    
    # 测试读取数据
    print("\n2. 测试读取股票历史数据...")
    df = db.get_stock_history('TEST')
    if df is not None:
        print(f"   ✓ 读取{len(df)}条数据")
        print(df.head())
    
    # 测试交易信号
    print("\n3. 测试保存交易信号...")
    success = db.save_trading_signal(
        'stock', 'TEST', 'BUY', 1.0, 0.85, '技术指标显示超卖'
    )
    if success:
        print("   ✓ 交易信号保存成功")
    
    # 获取信号
    print("\n4. 测试获取交易信号...")
    signals = db.get_latest_signals(5)
    if signals is not None:
        print(f"   ✓ 获取{len(signals)}条信号")
        print(signals)
    
    # 数据库统计
    print("\n5. 数据库统计...")
    stats = db.get_db_stats()
    for table, count in stats.items():
        print(f"   {table}: {count}条")
    
    # 备份
    print("\n6. 测试数据库备份...")
    if db.backup_database():
        print("   ✓ 备份成功")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

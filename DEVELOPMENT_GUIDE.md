# 开发规范和代码标准

## 📝 代码风格

### Python风格指南

遵循 PEP 8 标准，关键要点：

1. **缩进** - 使用4个空格
2. **行长度** - 最多79字符
3. **命名规范**
   - 类名：`PascalCase`
   - 函数/变量：`snake_case`
   - 常量：`UPPER_SNAKE_CASE`
   - 私有成员：`_leading_underscore`

### 示例

```python
"""
模块文档字符串
说明模块的功能
"""
import pandas as pd
from typing import Optional, Dict, List


class DataFetcher:
    """类文档字符串"""
    
    def __init__(self, config: Dict):
        """初始化方法"""
        self.config = config
        self._cache = {}  # 私有属性
    
    def get_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """
        获取数据
        
        Args:
            symbol: 股票代码
            period: 时间周期，默认1年
            
        Returns:
            DataFrame: 包含OHLCV数据
            
        Raises:
            ValueError: 当symbol无效时
        """
        # 实现代码
        pass
```

## 📚 文档规范

### 函数文档

使用Google风格的docstring：

```python
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    计算RSI指标
    
    Args:
        prices: 价格序列
        period: 计算周期，默认14
        
    Returns:
        RSI值序列，范围0-100
        
    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105])
        >>> rsi = calculate_rsi(prices)
        >>> print(rsi)
    """
    pass
```

### 模块文档

每个模块开头添加：

```python
"""
模块名称

模块功能描述
主要类和函数说明

Author: Your Name
Date: 2025-10-26
"""
```

## 🧪 测试规范

### 单元测试

使用pytest，测试文件命名：`test_*.py`

```python
# tests/test_stock_data.py
import pytest
from src.data_fetcher.stock_data import StockDataFetcher


class TestStockDataFetcher:
    """测试StockDataFetcher类"""
    
    @pytest.fixture
    def fetcher(self):
        """测试夹具"""
        return StockDataFetcher(config={})
    
    def test_get_realtime_price(self, fetcher):
        """测试实时价格获取"""
        price = fetcher.get_realtime_price('513500')
        assert isinstance(price, float)
        assert price > 0
    
    def test_invalid_symbol(self, fetcher):
        """测试无效代码"""
        with pytest.raises(ValueError):
            fetcher.get_realtime_price('INVALID')
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_stock_data.py

# 显示覆盖率
pytest --cov=src tests/
```

## 📊 日志规范

### 日志级别

```python
from src.utils.logger import log

# DEBUG - 详细的调试信息
log.debug(f"开始获取{symbol}的数据")

# INFO - 一般信息
log.info(f"成功获取{symbol}的数据，共{len(data)}条")

# WARNING - 警告信息
log.warning(f"缓存即将过期: {cache_age}秒")

# ERROR - 错误信息
log.error(f"数据获取失败: {str(e)}")

# CRITICAL - 严重错误
log.critical("数据库连接失败，系统无法运行")
```

### 日志格式

```python
# ✅ 好的日志
log.info(f"获取{symbol}历史数据完成，时间范围：{start} 到 {end}，共{count}条")

# ❌ 不好的日志
log.info("完成")  # 信息不足
log.info(f"symbol={symbol}, start={start}, end={end}")  # 难以阅读
```

## ⚡ 性能规范

### 使用向量化操作

```python
# ✅ 好的方式
returns = (prices / prices.shift(1) - 1) * 100

# ❌ 不好的方式
returns = []
for i in range(1, len(prices)):
    ret = (prices[i] / prices[i-1] - 1) * 100
    returns.append(ret)
```

### 避免重复计算

```python
# ✅ 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(symbol: str) -> float:
    # 耗时计算
    pass
```

## 🔒 安全规范

### API密钥管理

```python
# ✅ 从配置文件读取
from src.utils.config_loader import get_config
config = get_config()
api_key = config.get_api_key('tushare', 'token')

# ❌ 硬编码
api_key = "1234567890abcdef"  # 永远不要这样做
```

### 输入验证

```python
def get_data(symbol: str, period: str = '1y') -> pd.DataFrame:
    """获取数据"""
    # 验证输入
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol必须是非空字符串")
    
    valid_periods = ['1d', '1w', '1mo', '1y', '5y']
    if period not in valid_periods:
        raise ValueError(f"period必须是以下之一: {valid_periods}")
    
    # 继续处理
    pass
```

## 🚨 错误处理

### 异常处理模式

```python
from src.utils.logger import log

def fetch_data(symbol: str) -> pd.DataFrame:
    """获取数据"""
    try:
        # 尝试从API获取
        data = api.get_data(symbol)
        log.info(f"成功从API获取{symbol}的数据")
        return data
        
    except ConnectionError as e:
        # 网络错误，尝试从缓存获取
        log.warning(f"网络错误，尝试从缓存获取: {e}")
        try:
            return cache.get(symbol)
        except KeyError:
            log.error(f"缓存中也没有{symbol}的数据")
            raise
            
    except ValueError as e:
        # 数据验证错误
        log.error(f"数据验证失败: {e}")
        raise
        
    except Exception as e:
        # 其他未预期的错误
        log.critical(f"未知错误: {e}", exc_info=True)
        raise
```

## 🔄 Git提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型（type）

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

### 示例

```
feat(data): 实现513500 ETF数据获取功能

- 添加StockDataFetcher类
- 支持实时价格和历史数据获取
- 实现缓存机制

Closes #123
```

## 📦 代码组织

### 模块结构

```python
# 模块文档
"""stock_data.py - 股票数据获取模块"""

# 标准库导入
import os
from typing import Optional

# 第三方库导入
import pandas as pd
import akshare as ak

# 本地导入
from src.utils.logger import log
from src.utils.config_loader import get_config

# 常量定义
DEFAULT_PERIOD = '1y'
CACHE_TIMEOUT = 3600

# 类定义
class StockDataFetcher:
    pass

# 函数定义
def helper_function():
    pass

# 主程序
if __name__ == "__main__":
    # 测试代码
    pass
```

## 🎯 最佳实践总结

### Do（应该做）

✅ 使用类型提示
✅ 写详细的文档字符串
✅ 添加单元测试
✅ 使用日志记录重要操作
✅ 处理所有可能的异常
✅ 验证输入参数
✅ 使用配置文件管理参数
✅ 提交前运行测试

### Don't（不应该做）

❌ 硬编码配置参数
❌ 忽略异常
❌ 使用全局变量
❌ 写超长函数（>50行）
❌ 提交未测试的代码
❌ 提交包含密钥的文件
❌ 使用print调试（使用日志）

## 🔧 开发工具

### 代码格式化

```bash
# 使用black格式化
black src/

# 使用flake8检查
flake8 src/
```

### 类型检查

```bash
# 使用mypy检查类型
mypy src/
```

### 依赖管理

```bash
# 导出依赖
pip freeze > requirements.txt

# 更新依赖
pip install --upgrade -r requirements.txt
```

---

遵循这些规范将使代码更加专业、可维护和可扩展！

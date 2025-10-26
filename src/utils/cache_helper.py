"""
缓存辅助函数 - 提升应用性能
解决数据加载缓慢问题
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Dict, Any, List

# ==================== 会话状态管理 ====================

def init_session_state():
    """初始化会话状态"""
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = {}
    if 'loading_status' not in st.session_state:
        st.session_state.loading_status = {}

def is_cache_valid(cache_key: str, ttl_seconds: int = 300) -> bool:
    """检查缓存是否有效"""
    if cache_key not in st.session_state.last_update:
        return False
    
    last_time = st.session_state.last_update[cache_key]
    elapsed = (datetime.now() - last_time).total_seconds()
    return elapsed < ttl_seconds

def set_cache(cache_key: str, data: Any):
    """设置缓存数据"""
    st.session_state.data_cache[cache_key] = data
    st.session_state.last_update[cache_key] = datetime.now()

def get_cache(cache_key: str) -> Optional[Any]:
    """获取缓存数据"""
    return st.session_state.data_cache.get(cache_key)

def clear_cache(cache_key: Optional[str] = None):
    """清除缓存"""
    if cache_key:
        st.session_state.data_cache.pop(cache_key, None)
        st.session_state.last_update.pop(cache_key, None)
    else:
        st.session_state.data_cache = {}
        st.session_state.last_update = {}

# ==================== 数据获取辅助函数 ====================

@st.cache_data(ttl=300, show_spinner="📊 正在获取实时数据...")
def get_realtime_with_cache(_data_manager, asset_type: str, asset_code: str) -> Optional[Dict]:
    """获取实时数据(带缓存 5分钟)"""
    try:
        return _data_manager.get_asset_data(asset_type, asset_code, 'realtime')
    except Exception as e:
        st.warning(f"获取 {asset_code} 实时数据失败: {str(e)}")
        return None

@st.cache_data(ttl=1800, show_spinner="📈 正在获取历史数据...")
def get_history_with_cache(_data_manager, asset_type: str, asset_code: str, period: str = '1y') -> Optional[pd.DataFrame]:
    """获取历史数据(带缓存 30分钟)"""
    try:
        return _data_manager.get_asset_data(asset_type, asset_code, 'history', period=period)
    except Exception as e:
        st.warning(f"获取 {asset_code} 历史数据失败: {str(e)}")
        return None

@st.cache_data(ttl=600, show_spinner="🌐 正在获取市场数据...")
def get_market_overview_cache(_data_manager) -> Dict[str, Any]:
    """获取市场概览数据(带缓存 10分钟)"""
    try:
        market_data = {
            'crypto': [],
            'etf': [],
            'stocks': [],
            'timestamp': datetime.now()
        }
        
        # 获取加密货币数据
        crypto_symbols = ['bitcoin', 'ethereum', 'binancecoin']
        for symbol in crypto_symbols:
            data = get_realtime_with_cache(_data_manager, 'crypto', symbol)
            if data:
                market_data['crypto'].append(data)
        
        # 获取ETF数据
        etf_codes = ['513500', '159915', '512690']
        for code in etf_codes:
            data = get_realtime_with_cache(_data_manager, 'etf', code)
            if data:
                market_data['etf'].append(data)
        
        return market_data
    except Exception as e:
        st.warning(f"获取市场数据失败: {str(e)}")
        return {'crypto': [], 'etf': [], 'stocks': [], 'timestamp': datetime.now()}

@st.cache_data(ttl=600, show_spinner="🎯 正在生成交易信号...")
def get_signals_with_cache(_signal_gen, _data_manager, assets: List[tuple]) -> List[Dict]:
    """获取交易信号(带缓存 10分钟)"""
    try:
        signals = []
        for asset_type, asset_code in assets:
            # 获取历史数据用于信号分析
            history = get_history_with_cache(_data_manager, asset_type, asset_code, '3m')
            if history is not None and len(history) > 20:
                result = _signal_gen.analyze_with_signals(history, asset_code)
                if result and 'comprehensive_signal' in result:
                    sig = result['comprehensive_signal']
                    signals.append({
                        'asset': asset_code,
                        'type': asset_type,
                        'signal': sig.get('signal', '观望'),
                        'confidence': sig.get('confidence', '低'),
                        'strength': sig.get('strength', 0),
                        'reasons': sig.get('reasons', [])[:3]  # 只保留前3条原因
                    })
        return signals
    except Exception as e:
        st.warning(f"生成交易信号失败: {str(e)}")
        return []

# ==================== 批量数据获取 ====================

def batch_get_realtime(_data_manager, assets: List[tuple], max_concurrent: int = 3) -> Dict[str, Any]:
    """批量获取实时数据(限制并发数)"""
    results = {}
    for i, (asset_type, asset_code) in enumerate(assets):
        cache_key = f"{asset_type}_{asset_code}_realtime"
        
        # 检查会话状态缓存
        if is_cache_valid(cache_key, ttl_seconds=300):
            results[asset_code] = get_cache(cache_key)
        else:
            # 显示加载进度
            if i % max_concurrent == 0 and i > 0:
                st.info(f"正在加载 {i}/{len(assets)} 个资产...")
            
            data = get_realtime_with_cache(_data_manager, asset_type, asset_code)
            if data:
                results[asset_code] = data
                set_cache(cache_key, data)
    
    return results

def batch_get_history(_data_manager, assets: List[tuple], period: str = '1y') -> Dict[str, pd.DataFrame]:
    """批量获取历史数据"""
    results = {}
    total = len(assets)
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (asset_type, asset_code) in enumerate(assets):
        cache_key = f"{asset_type}_{asset_code}_history_{period}"
        
        # 更新进度
        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"正在加载 {asset_code} ({i+1}/{total})")
        
        # 检查会话状态缓存
        if is_cache_valid(cache_key, ttl_seconds=1800):
            results[asset_code] = get_cache(cache_key)
        else:
            data = get_history_with_cache(_data_manager, asset_type, asset_code, period)
            if data is not None:
                results[asset_code] = data
                set_cache(cache_key, data)
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    return results

# ==================== 缓存管理工具 ====================

def show_cache_manager():
    """显示缓存管理界面"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 缓存管理")
    
    # 显示缓存状态
    cache_count = len(st.session_state.get('data_cache', {}))
    st.sidebar.metric("缓存项数", cache_count)
    
    # 显示最近更新时间
    if st.session_state.get('last_update'):
        latest_update = max(st.session_state.last_update.values())
        elapsed = (datetime.now() - latest_update).total_seconds()
        st.sidebar.caption(f"最近更新: {int(elapsed)}秒前")
    
    # 刷新按钮
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("♻️ 刷新数据", use_container_width=True):
            clear_cache()
            st.rerun()
    with col2:
        if st.button("🗑️ 清除缓存", use_container_width=True):
            st.cache_data.clear()
            clear_cache()
            st.success("缓存已清除")
            st.rerun()

def get_cache_info() -> Dict[str, Any]:
    """获取缓存信息"""
    cache_data = st.session_state.get('data_cache', {})
    last_update = st.session_state.get('last_update', {})
    
    info = {
        'total_items': len(cache_data),
        'cache_keys': list(cache_data.keys()),
        'oldest_cache': None,
        'newest_cache': None
    }
    
    if last_update:
        times = list(last_update.values())
        info['oldest_cache'] = min(times)
        info['newest_cache'] = max(times)
    
    return info

# ==================== 性能监控 ====================

def timing_decorator(func_name: str):
    """计时装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            result = func(*args, **kwargs)
            elapsed = (datetime.now() - start).total_seconds()
            
            # 记录到会话状态
            if 'timing_log' not in st.session_state:
                st.session_state.timing_log = []
            
            st.session_state.timing_log.append({
                'function': func_name,
                'elapsed': elapsed,
                'timestamp': datetime.now()
            })
            
            # 只保留最近100条记录
            if len(st.session_state.timing_log) > 100:
                st.session_state.timing_log = st.session_state.timing_log[-100:]
            
            return result
        return wrapper
    return decorator

def show_performance_metrics():
    """显示性能指标"""
    if 'timing_log' in st.session_state and st.session_state.timing_log:
        st.sidebar.markdown("### ⚡ 性能指标")
        
        # 计算平均加载时间
        recent_logs = st.session_state.timing_log[-10:]
        avg_time = sum(log['elapsed'] for log in recent_logs) / len(recent_logs)
        
        st.sidebar.metric("平均加载时间", f"{avg_time:.2f}秒")
        
        # 显示最慢的操作
        slowest = max(recent_logs, key=lambda x: x['elapsed'])
        st.sidebar.caption(f"最慢: {slowest['function']} ({slowest['elapsed']:.2f}s)")

# ==================== 智能预加载 ====================

def preload_common_data(_data_manager):
    """预加载常用数据"""
    common_assets = [
        ('crypto', 'bitcoin'),
        ('crypto', 'ethereum'),
        ('etf', '513500'),
        ('etf', '159915'),
    ]
    
    # 在后台预加载(不显示spinner)
    for asset_type, asset_code in common_assets:
        cache_key = f"{asset_type}_{asset_code}_realtime"
        if not is_cache_valid(cache_key, ttl_seconds=300):
            try:
                data = _data_manager.get_asset_data(asset_type, asset_code, 'realtime')
                if data:
                    set_cache(cache_key, data)
            except:
                pass  # 静默失败

# ==================== 导出函数 ====================

__all__ = [
    'init_session_state',
    'get_realtime_with_cache',
    'get_history_with_cache',
    'get_market_overview_cache',
    'get_signals_with_cache',
    'batch_get_realtime',
    'batch_get_history',
    'show_cache_manager',
    'show_performance_metrics',
    'preload_common_data',
    'clear_cache',
    'get_cache_info'
]

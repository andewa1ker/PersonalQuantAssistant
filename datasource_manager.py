"""
数据源管理页面
显示多数据源状态、缓存统计、手动清理等功能
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from data_fetcher.multi_source_fetcher import MultiSourceETFFetcher


def show_datasource_manager():
    """显示数据源管理页面"""
    st.header("🔧 数据源管理")
    
    # 初始化fetcher
    fetcher = MultiSourceETFFetcher()
    
    # 数据源状态
    st.markdown("### 📊 数据源状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tushare_status = "✅ 可用" if fetcher.ts_pro else "❌ 不可用"
        st.metric("Tushare (主)", tushare_status, "优先级: 1")
    
    with col2:
        st.metric("新浪财经 (备1)", "✅ 可用", "优先级: 2")
    
    with col3:
        st.metric("东方财富 (备2)", "✅ 可用", "优先级: 3")
    
    with col4:
        st.metric("AKShare (备3)", "✅ 可用", "优先级: 4")
    
    st.markdown("---")
    
    # 缓存统计
    st.markdown("### 💾 缓存统计")
    
    stats = fetcher.get_cache_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("实时数据缓存", f"{stats.get('realtime_records', 0)} 条")
    
    with col2:
        st.metric("历史数据缓存", f"{stats.get('history_records', 0)} 条")
    
    with col3:
        st.metric("数据库路径", "已配置")
    
    if 'database_path' in stats:
        st.caption(f"📁 {stats['database_path']}")
    
    st.markdown("---")
    
    # 缓存管理
    st.markdown("### 🗑️ 缓存管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        days = st.slider("清理多少天前的数据", 7, 90, 30)
        if st.button("🗑️ 清理旧缓存", type="primary"):
            with st.spinner("正在清理..."):
                fetcher.clear_old_cache(days=days)
            st.success(f"✅ 已清理 {days} 天前的缓存数据")
    
    with col2:
        st.markdown("#### 测试数据获取")
        test_symbol = st.selectbox("选择测试ETF", ['513500', '159915', '512690', '159941'])
        
        if st.button("🧪 测试获取"):
            with st.spinner("正在测试各数据源..."):
                results = {}
                
                # 测试各数据源
                for source in fetcher.source_priority:
                    try:
                        if source == 'tushare':
                            data = fetcher._fetch_tushare_realtime(test_symbol)
                        elif source == 'sina':
                            data = fetcher._fetch_sina_realtime(test_symbol)
                        elif source == 'eastmoney':
                            data = fetcher._fetch_eastmoney_realtime(test_symbol)
                        elif source == 'akshare':
                            data = fetcher._fetch_akshare_realtime(test_symbol)
                        
                        if data:
                            results[source] = {
                                'status': '✅ 成功',
                                'price': data.get('price', 0),
                                'name': data.get('name', '')
                            }
                        else:
                            results[source] = {'status': '❌ 失败', 'price': '-', 'name': '-'}
                    except Exception as e:
                        results[source] = {'status': f'❌ 错误: {str(e)[:30]}', 'price': '-', 'name': '-'}
                
                # 显示测试结果
                st.markdown("#### 测试结果")
                for source, result in results.items():
                    st.write(f"**{source.upper()}**: {result['status']} | 价格: {result['price']} | {result['name']}")
    
    st.markdown("---")
    
    # 配置说明
    st.markdown("### ℹ️ 配置说明")
    
    with st.expander("📖 数据源策略"):
        st.markdown("""
        **混合策略流程**:
        
        1. **Streamlit缓存层** (5分钟TTL)
           - 最快速的缓存，直接从内存读取
           
        2. **SQLite数据库层** (数据库文件)
           - 实时数据缓存5分钟
           - 历史数据长期保存
           - 支持离线模式
           
        3. **多数据源获取** (按优先级尝试)
           - ① Tushare (最稳定，需token)
           - ② 新浪财经 (快速，免费)
           - ③ 东方财富 (全面，免费)
           - ④ AKShare (备用，免费)
           
        4. **降级策略**
           - 如果所有数据源失败
           - 使用24小时内的旧缓存
           - 标注为缓存数据
        """)
    
    with st.expander("⚙️ 重试机制"):
        st.markdown("""
        **智能重试配置**:
        
        - **指数退避**: 1秒 → 2秒 → 4秒
        - **最大重试**: 每个数据源重试3次
        - **超时设置**: 30秒连接超时
        - **请求间隔**: 随机0.5-1.5秒
        - **连接池**: 使用Session复用连接
        """)
    
    with st.expander("💡 使用建议"):
        st.markdown("""
        **最佳实践**:
        
        1. ✅ **定期清理缓存**: 每月清理一次旧数据
        2. ✅ **观察数据源**: 如果某个源频繁失败，可能需要调整
        3. ✅ **测试功能**: 使用测试按钮检查各数据源状态
        4. ✅ **数据库备份**: 定期备份etf_cache.db文件
        5. ⚠️ **Tushare积分**: 确保有足够积分，否则会降级到备用源
        """)
    
    # 显示最近的缓存数据
    st.markdown("---")
    st.markdown("### 📋 最近缓存记录")
    
    try:
        import sqlite3
        import pandas as pd
        
        with sqlite3.connect(fetcher.db_path) as conn:
            # 显示最近的实时数据
            df = pd.read_sql_query('''
                SELECT symbol, name, price, change_pct, source, timestamp 
                FROM etf_realtime 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', conn)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无缓存数据")
    except Exception as e:
        st.error(f"读取缓存失败: {e}")


if __name__ == "__main__":
    st.set_page_config(page_title="数据源管理", page_icon="🔧", layout="wide")
    show_datasource_manager()

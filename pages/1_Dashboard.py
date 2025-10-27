"""
📊 主控面板
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from design_system import inject_css
from ds_icons import icon
from ds_components import section_header, kpi_card, line_area_chart, tx_list

inject_css()

# 初始化AI预测器 + 持仓管理器
@st.cache_resource
def init_ml_predictor():
    try:
        from ai.ml_predictor import DirectionPredictor
        return DirectionPredictor(forecast_horizon=5)
    except Exception as e:
        st.error(f"AI预测器初始化失败: {str(e)}")
        return None

@st.cache_resource
def init_position_manager():
    try:
        from risk_management.position_manager import PositionManager
        return PositionManager()
    except Exception as e:
        st.error(f"持仓管理器初始化失败: {str(e)}")
        return None

ml_predictor = init_ml_predictor()
position_mgr = init_position_manager()

st.title('📊 量化投资主控面板')
st.caption('实时监控 · 智能决策 · 风险可控')

st.divider()

# 初始化数据管理器
@st.cache_resource
def init_data_manager():
    try:
        from data_fetcher.data_manager import DataManager
        return DataManager()
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        return None

data_manager = init_data_manager()

# 获取真实数据
@st.cache_data(ttl=300)
def get_crypto_data():
    if data_manager:
        try:
            btc_data = data_manager.get_asset_data('crypto', 'bitcoin', 'realtime')
            eth_data = data_manager.get_asset_data('crypto', 'ethereum', 'realtime')
            return btc_data, eth_data
        except:
            return None, None
    return None, None

btc_data, eth_data = get_crypto_data()

# KPI指标 - 显示真实加密货币数据
col1, col2, col3, col4 = st.columns(4)
with col1:
    if btc_data:
        price = btc_data.get('current_price', 0)
        change = btc_data.get('price_change_percentage_24h', 0)
        kpi_card('BTC价格', f'${price:,.2f}', f'{change:+.2f}%', 'up' if change > 0 else 'down')
    else:
        kpi_card('BTC价格', '加载中...', '-', 'neutral')
        
with col2:
    if eth_data:
        price = eth_data.get('current_price', 0)
        change = eth_data.get('price_change_percentage_24h', 0)
        kpi_card('ETH价格', f'${price:,.2f}', f'{change:+.2f}%', 'up' if change > 0 else 'down')
    else:
        kpi_card('ETH价格', '加载中...', '-', 'neutral')
        
with col3:
    if btc_data:
        vol = btc_data.get('total_volume', 0)
        kpi_card('BTC 24h交易量', f'${vol/1e9:.2f}B', '-', 'neutral')
    else:
        kpi_card('24h交易量', '加载中...', '-', 'neutral')
        
with col4:
    if btc_data:
        cap = btc_data.get('market_cap', 0)
        kpi_card('BTC市值', f'${cap/1e9:.2f}B', '-', 'neutral')
    else:
        kpi_card('市值', '加载中...', '-', 'neutral')

st.divider()

# 获取历史数据用于趋势图
@st.cache_data(ttl=600)
def get_btc_history():
    if data_manager:
        try:
            hist_data = data_manager.get_asset_data('crypto', 'bitcoin', 'history', period='30d')
            if hist_data is not None and len(hist_data) > 0:
                return hist_data
        except:
            pass
    return None

btc_history = get_btc_history()

# 趋势图表
col1, col2 = st.columns([2, 1])

with col1:
    section_header('activity', 'BTC价格趋势', '近30日价格变化')
    if btc_history is not None and len(btc_history) > 0:
        dates = btc_history.index[-30:].strftime('%m-%d').tolist()
        values = btc_history['close'][-30:].tolist()
        line_area_chart(dates, values)
    else:
        st.info("📊 正在加载历史数据...")
        dates = [(datetime.now() - timedelta(days=30-i)).strftime('%m-%d') for i in range(30)]
        values = [40000 + i*200 + (i%3)*50 for i in range(30)]
        line_area_chart(dates, values)

with col2:
    section_header('wallet', '市场信息', '实时行情动向')
    if btc_data:
        tx_list([
            {'icon': 'trending-up' if btc_data.get('price_change_24h', 0) > 0 else 'trending-down', 
             'title': 'BTC 24h', 
             'tag': f"{btc_data.get('price_change_percentage_24h', 0):+.2f}%", 
             'amount': btc_data.get('price_change_24h', 0), 
             'time': '实时'},
            {'icon': 'trending-up' if eth_data and eth_data.get('price_change_24h', 0) > 0 else 'trending-down', 
             'title': 'ETH 24h', 
             'tag': f"{eth_data.get('price_change_percentage_24h', 0) if eth_data else 0:+.2f}%", 
             'amount': eth_data.get('price_change_24h', 0) if eth_data else 0, 
             'time': '实时'},
            {'icon': 'activity', 
             'title': '市场波动率', 
             'tag': '中等', 
             'amount': 0, 
             'time': ''},
        ])
    else:
        tx_list([
            {'icon': 'trending-up', 'title': '加载中...', 'tag': '-', 'amount': 0, 'time': ''},
        ])

st.divider()

# 持仓分布 - 显示真实加密货币市值占比
section_header('layers', '加密货币市场', '主要币种市值占比')

@st.cache_data(ttl=300)
def get_market_overview():
    if data_manager:
        try:
            coins = []
            for symbol in ['bitcoin', 'ethereum', 'binancecoin']:
                data = data_manager.get_asset_data('crypto', symbol, 'realtime')
                if data:
                    coins.append(data)
            return coins
        except:
            pass
    return []

coins = get_market_overview()

if coins and len(coins) >= 3:
    total_cap = sum(c.get('market_cap', 0) for c in coins)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btc_cap = coins[0].get('market_cap', 0)
        btc_pct = (btc_cap / total_cap * 100) if total_cap > 0 else 0
        btc_change = coins[0].get('price_change_percentage_24h', 0)
        st.metric('Bitcoin', f'{btc_pct:.1f}%', f'{btc_change:+.2f}% (24h)')
    
    with col2:
        eth_cap = coins[1].get('market_cap', 0)
        eth_pct = (eth_cap / total_cap * 100) if total_cap > 0 else 0
        eth_change = coins[1].get('price_change_percentage_24h', 0)
        st.metric('Ethereum', f'{eth_pct:.1f}%', f'{eth_change:+.2f}% (24h)')
    
    with col3:
        bnb_cap = coins[2].get('market_cap', 0)
        bnb_pct = (bnb_cap / total_cap * 100) if total_cap > 0 else 0
        bnb_change = coins[2].get('price_change_percentage_24h', 0)
        st.metric('BNB', f'{bnb_pct:.1f}%', f'{bnb_change:+.2f}% (24h)')
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Bitcoin', '加载中...', '-')
    with col2:
        st.metric('Ethereum', '加载中...', '-')
    with col3:
        st.metric('BNB', '加载中...', '-')

st.divider()

# AI价格预测
section_header('wand', 'AI价格预测', '机器学习方向预测 (5日)')

# 选择资产
pred_asset = st.selectbox('选择预测资产', ['BTC', 'ETH', 'BNB'], key='pred_asset')

asset_map = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin'
}

if st.button('🔮 生成预测', type='primary'):
    with st.spinner('AI模型分析中...'):
        try:
            # 获取90天历史数据
            symbol = asset_map[pred_asset]
            hist_data = data_manager.get_asset_data('crypto', symbol, 'history', period='90d')
            
            if hist_data is not None and len(hist_data) > 50:
                # 训练模型
                ml_predictor.train(hist_data)
                
                # 生成预测
                prediction = ml_predictor.predict(hist_data)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    direction = '📈 看涨' if prediction.prediction > 0.5 else '📉 看跌'
                    st.metric('预测方向', direction)
                
                with col2:
                    confidence = prediction.confidence * 100 if prediction.confidence else 0
                    st.metric('置信度', f'{confidence:.1f}%')
                
                with col3:
                    st.metric('预测周期', f'{prediction.forecast_horizon}天')
                
                # 显示特征重要性
                if ml_predictor.models.get('main'):
                    st.info(f'✨ 模型使用了 {len(prediction.features_used or [])} 个技术指标特征')
                    
            else:
                st.error('历史数据不足，需要至少50天数据')
                
        except Exception as e:
            st.error(f'预测失败: {str(e)}')
            st.info('提示：首次预测需要训练模型，可能需要10-30秒')

st.divider()

# 智能仓位计算
section_header('target', '智能仓位计算', '基于凯利公式 & 波动率调整')

with st.expander('💰 仓位管理', expanded=False):
    st.info('💡 根据历史表现和风险参数智能计算建议仓位')
    
    col1, col2 = st.columns(2)
    with col1:
        pos_asset = st.selectbox('选择资产', ['BTC', 'ETH', 'BNB'], key='pos_asset')
        pos_method = st.selectbox('计算方法', ['凯利公式', '波动率调整', '固定风险'], key='pos_method')
    
    with col2:
        if pos_method == '凯利公式':
            win_rate = st.slider('历史胜率 (%)', 30, 80, 55, 1, key='win_rate') / 100
            profit_loss_ratio = st.slider('盈亏比', 1.0, 5.0, 2.5, 0.1, key='pl_ratio')
        
        elif pos_method == '波动率调整':
            target_vol = st.slider('目标波动率 (%)', 5, 30, 15, 1, key='target_vol') / 100
        
        else:  # 固定风险
            risk_pct = st.slider('风险比例 (%)', 1, 5, 2, 1, key='risk_pct') / 100
            stop_loss = st.slider('止损幅度 (%)', 3, 15, 5, 1, key='stop_loss') / 100
    
    if st.button('🎯 计算仓位', type='primary'):
        if not position_mgr:
            st.error('持仓管理器未初始化')
        else:
            with st.spinner('正在计算...'):
                try:
                    asset_map = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin'}
                    symbol = asset_map[pos_asset]
                    
                    # 根据方法计算
                    if pos_method == '凯利公式':
                        result = position_mgr.calculate_position_kelly(
                            win_rate=win_rate,
                            profit_loss_ratio=profit_loss_ratio,
                            asset_symbol=pos_asset
                        )
                    
                    elif pos_method == '波动率调整':
                        # 获取历史数据计算波动率
                        hist_data = data_manager.get_asset_data('crypto', symbol, 'history', period='90d')
                        if hist_data is not None and len(hist_data) > 30:
                            result = position_mgr.calculate_position_volatility(
                                data=hist_data,
                                asset_symbol=pos_asset,
                                target_volatility=target_vol
                            )
                        else:
                            st.error('历史数据不足')
                            result = None
                    
                    else:  # 固定风险
                        result = position_mgr.calculate_position_fixed_risk(
                            stop_loss_pct=stop_loss,
                            asset_symbol=pos_asset,
                            risk_per_trade=risk_pct
                        )
                    
                    if result:
                        # 显示结果
                        st.success(f'✅ 计算完成 - 方法: {result.method}')
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                '建议仓位',
                                f'{result.recommended_position:.1%}',
                                delta=None
                            )
                        
                        with col2:
                            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                            st.metric(
                                '风险等级',
                                f"{risk_emoji.get(result.risk_level, '⚪')} {result.risk_level}"
                            )
                        
                        with col3:
                            st.metric(
                                '置信度',
                                f'{result.confidence:.1%}'
                            )
                        
                        # 说明
                        st.info(f'📝 {result.reason}')
                        
                        # 仓位范围
                        st.progress(result.recommended_position)
                        st.caption(f'最小仓位: {result.min_position:.1%} | 最大仓位: {result.max_position:.1%}')
                        
                        # 详细信息
                        if result.details:
                            with st.expander('详细信息'):
                                st.json(result.details)
                
                except Exception as e:
                    st.error(f'计算失败: {str(e)}')
                    import traceback
                    st.code(traceback.format_exc())


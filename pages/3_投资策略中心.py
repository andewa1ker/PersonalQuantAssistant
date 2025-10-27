"""
🎯 投资策略中心
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go
import numpy as np

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from design_system import inject_css, TOKENS
from ds_icons import icon
from ds_components import section_header, pill_badge, form_row
from utils.strategy_config_manager import StrategyConfigManager

inject_css()

# 初始化策略管理器 + 因子挖掘器 + 止损管理器
@st.cache_resource
def init_strategy_manager():
    return StrategyConfigManager()

@st.cache_resource
def init_factor_miner():
    try:
        from ai.factor_mining import FactorMiner, FactorConfig
        config = FactorConfig(
            population_size=50,
            generations=30,
            min_ic=0.02
        )
        return FactorMiner(config)
    except Exception as e:
        st.error(f"因子挖掘器初始化失败: {str(e)}")
        return None

@st.cache_resource
def init_stop_loss_manager():
    try:
        from risk_management.stop_loss_manager import StopLossManager
        return StopLossManager()
    except Exception as e:
        st.error(f"止损管理器初始化失败: {str(e)}")
        return None

strategy_mgr = init_strategy_manager()
factor_miner = init_factor_miner()
stop_loss_mgr = init_stop_loss_manager()

st.title('🎯 投资策略中心')
st.caption('自定义量化策略 · 智能参数优化')

st.divider()

# 策略列表
section_header('wand', '我的策略', '已配置策略列表')

# 获取真实策略数据
strategies = strategy_mgr.get_all_strategies()

if not strategies:
    st.info("还没有配置策略,请在下方创建新策略")
else:
    for s in strategies:
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        # 状态映射
        status_map = {
            "running": {"label": "运行中", "tone": "success"},
            "paused": {"label": "已暂停", "tone": "warning"},
            "stopped": {"label": "已停止", "tone": "info"}
        }
        status_info = status_map.get(s.get("status", "stopped"), {"label": "未知", "tone": "info"})
        
        with col1:
            st.markdown(f'<div style="font-weight:600;padding:0.5rem 0">{s.get("name", "未命名策略")}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(pill_badge(status_info["label"], status_info["tone"]), unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div style="color:{TOKENS["text_weak"]};padding:0.5rem 0">{s.get("asset", "N/A")}</div>', unsafe_allow_html=True)
        with col4:
            if st.button('编辑', key=f'edit_{s["id"]}', use_container_width=False):
                st.session_state['editing_strategy'] = s["id"]
                st.rerun()
        with col5:
            if st.button('删除', key=f'delete_{s["id"]}', type='secondary', use_container_width=False):
                if strategy_mgr.delete_strategy(s["id"]):
                    st.success(f'策略 "{s.get("name")}" 已删除')
                    st.rerun()
                else:
                    st.error('删除失败')

st.divider()

# 新建策略
section_header('sliders-vertical', '策略配置', '创建新策略或调整参数')

with st.expander('📝 创建新策略', expanded=False):
    # 获取策略类型
    strategy_types = strategy_mgr.get_strategy_types()
    type_options = {t["name"]: t["id"] for t in strategy_types}
    
    strategy_name = st.text_input('策略名称', placeholder='输入策略名称', key='new_strategy_name')
    strategy_type = st.selectbox('策略类型', list(type_options.keys()), key='strategy_type_select')
    asset = st.selectbox('交易资产', ['BTC', 'ETH', 'BNB', 'ETF'], key='asset_select')
    
    col1, col2 = st.columns(2)
    with col1:
        stop_loss = st.slider('止损比例 (%)', 0.0, 20.0, 5.0, 0.5, key='stop_loss')
    with col2:
        position_limit = st.slider('仓位上限 (%)', 0, 100, 30, 5, key='position_limit')
    
    st.markdown('<div style="margin-top:1.5rem"></div>', unsafe_allow_html=True)
    if st.button('✨ 创建策略', type='primary'):
        if not strategy_name:
            st.error('请输入策略名称')
        else:
            new_strategy = {
                "name": strategy_name,
                "type": type_options[strategy_type],
                "status": "stopped",
                "asset": asset,
                "params": {},
                "risk": {
                    "stop_loss": stop_loss / 100,
                    "position_limit": position_limit / 100
                }
            }
            
            if strategy_mgr.save_strategy(new_strategy):
                st.success(f'✅ 策略 "{strategy_name}" 创建成功!')
                st.balloons()
                st.rerun()
            else:
                st.error('创建失败,请查看日志')

st.divider()

# 策略统计
section_header('chart-histogram', '策略统计', '配置概览')

stats = strategy_mgr.get_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总策略数", stats["total"])
with col2:
    st.metric("运行中", stats["running"], delta="Active")
with col3:
    st.metric("已暂停", stats["paused"])
with col4:
    st.metric("已停止", stats["stopped"])

# 策略详情表
if strategies:
    df_data = []
    for s in strategies:
        df_data.append({
            '策略名称': s.get('name', 'N/A'),
            '类型': s.get('type', 'N/A'),
            '资产': s.get('asset', 'N/A'),
            '状态': s.get('status', 'N/A'),
            '止损': f"{s.get('risk', {}).get('stop_loss', 0)*100:.1f}%",
            '仓位上限': f"{s.get('risk', {}).get('position_limit', 0)*100:.0f}%",
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, hide_index=True)

st.divider()

# AI因子挖掘
section_header('wand', 'AI因子挖掘', '自动发现Alpha因子')

with st.expander('🔬 智能因子发现', expanded=False):
    st.info('💡 使用遗传编程自动搜索有效因子，基于IC值筛选')
    
    # 初始化数据管理器
    @st.cache_resource
    def init_data_manager():
        try:
            from data_fetcher.data_manager import DataManager
            return DataManager()
        except:
            return None
    
    data_manager = init_data_manager()
    
    col1, col2 = st.columns(2)
    with col1:
        mining_asset = st.selectbox('选择资产', ['BTC', 'ETH', 'BNB'], key='mining_asset')
    with col2:
        mining_days = st.slider('训练数据天数', 90, 365, 180, key='mining_days')
    
    if st.button('🚀 开始挖掘', type='primary'):
        if not factor_miner:
            st.error('因子挖掘器未初始化')
        elif not data_manager:
            st.error('数据管理器未初始化')
        else:
            with st.spinner('AI正在挖掘因子...可能需要1-2分钟'):
                try:
                    asset_map = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin'}
                    symbol = asset_map[mining_asset]
                    
                    # 获取历史数据
                    hist_data = data_manager.get_asset_data('crypto', symbol, 'history', period=f'{mining_days}d')
                    
                    if hist_data is not None and len(hist_data) > 100:
                        # 计算未来收益率
                        hist_data['future_return'] = hist_data['close'].pct_change(5).shift(-5)
                        
                        # 挖掘因子
                        result = factor_miner.mine(hist_data, 'future_return')
                        
                        if result and result.top_factors:
                            st.success(f'✅ 发现 {len(result.all_factors)} 个有效因子')
                            
                            # 显示最佳因子
                            st.markdown('### 🏆 最佳因子')
                            best = result.best_factor
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric('IC值', f'{best.ic:.4f}')
                            with col2:
                                st.metric('IC_IR', f'{best.ic_ir:.4f}')
                            with col3:
                                st.metric('Rank IC', f'{best.rank_ic:.4f}')
                            with col4:
                                st.metric('换手率', f'{best.turnover:.2%}')
                            
                            st.code(f'表达式: {best.expression}', language='python')
                            
                            # Top 5 因子列表
                            st.markdown('### 📊 Top 5 因子')
                            factor_table = []
                            for i, f in enumerate(result.top_factors[:5], 1):
                                factor_table.append({
                                    '排名': f'#{i}',
                                    '表达式': f.expression[:50] + '...' if len(f.expression) > 50 else f.expression,
                                    'IC': f'{f.ic:.4f}',
                                    'IC_IR': f'{f.ic_ir:.4f}',
                                    'Rank_IC': f'{f.rank_ic:.4f}'
                                })
                            
                            st.dataframe(pd.DataFrame(factor_table), hide_index=True)
                            
                            # 进化曲线
                            if result.generation_stats:
                                st.markdown('### 📈 进化曲线')
                                gen_nums = [s['generation'] for s in result.generation_stats]
                                best_ics = [s['best_ic'] for s in result.generation_stats]
                                avg_ics = [s['avg_ic'] for s in result.generation_stats]
                                
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=gen_nums, y=best_ics, mode='lines+markers', name='最佳IC', line=dict(color='#00D9FF')))
                                fig.add_trace(go.Scatter(x=gen_nums, y=avg_ics, mode='lines', name='平均IC', line=dict(color='#888', dash='dash')))
                                fig.update_layout(
                                    title='因子IC进化过程',
                                    xaxis_title='代数',
                                    yaxis_title='IC值',
                                    template='plotly_dark',
                                    height=300
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning('未发现有效因子，尝试调整参数')
                    else:
                        st.error(f'历史数据不足: 需要至少100天，当前{len(hist_data) if hist_data is not None else 0}天')
                        
                except Exception as e:
                    st.error(f'挖掘失败: {str(e)}')
                    import traceback
                    st.code(traceback.format_exc())

st.divider()

# 智能止损止盈
section_header('shield-check', '智能止损止盈', 'ATR动态止损 & 支撑阻力位')

with st.expander('🛡️ 止损止盈计算器', expanded=False):
    st.info('💡 根据ATR或支撑阻力位自动计算止损止盈位')
    
    # 初始化数据管理器
    @st.cache_resource
    def init_data_manager_sl():
        try:
            from data_fetcher.data_manager import DataManager
            return DataManager()
        except:
            return None
    
    data_manager_sl = init_data_manager_sl()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sl_asset = st.selectbox('选择资产', ['BTC', 'ETH', 'BNB'], key='sl_asset')
    with col2:
        sl_direction = st.selectbox('交易方向', ['做多 (long)', '做空 (short)'], key='sl_direction')
    with col3:
        sl_method = st.selectbox('计算方法', ['固定百分比', 'ATR动态', '支撑阻力位'], key='sl_method')
    
    # 根据方法显示参数
    if sl_method == '固定百分比':
        col1, col2 = st.columns(2)
        with col1:
            stop_loss_pct = st.slider('止损百分比 (%)', 1.0, 20.0, 5.0, 0.5, key='stop_loss_pct')
        with col2:
            risk_reward = st.slider('风险收益比', 1.0, 5.0, 3.0, 0.5, key='risk_reward')
    
    elif sl_method == 'ATR动态':
        col1, col2 = st.columns(2)
        with col1:
            atr_period = st.slider('ATR周期', 5, 30, 14, 1, key='atr_period')
        with col2:
            atr_mult = st.slider('ATR倍数', 1.0, 5.0, 2.0, 0.5, key='atr_mult')
    
    else:  # 支撑阻力位
        lookback = st.slider('回看周期', 10, 50, 20, 5, key='lookback')
    
    if st.button('📊 计算止损止盈', type='primary'):
        if not stop_loss_mgr:
            st.error('止损管理器未初始化')
        elif not data_manager_sl:
            st.error('数据管理器未初始化')
        else:
            with st.spinner('正在计算...'):
                try:
                    asset_map = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin'}
                    symbol = asset_map[sl_asset]
                    direction = 'long' if '做多' in sl_direction else 'short'
                    
                    # 获取历史数据
                    hist_data = data_manager_sl.get_asset_data('crypto', symbol, 'history', period='90d')
                    
                    if hist_data is not None and len(hist_data) > 20:
                        current_price = float(hist_data['close'].iloc[-1])
                        
                        # 根据方法计算
                        if sl_method == '固定百分比':
                            result = stop_loss_mgr.calculate_fixed_stop_loss(
                                current_price=current_price,
                                direction=direction,
                                asset_symbol=sl_asset,
                                stop_loss_pct=stop_loss_pct / 100,
                                risk_reward_ratio=risk_reward
                            )
                        
                        elif sl_method == 'ATR动态':
                            result = stop_loss_mgr.calculate_atr_stop_loss(
                                data=hist_data,
                                direction=direction,
                                asset_symbol=sl_asset,
                                atr_period=atr_period,
                                atr_stop_multiplier=atr_mult
                            )
                        
                        else:  # 支撑阻力位
                            result = stop_loss_mgr.calculate_支撑阻力_stop_loss(
                                data=hist_data,
                                direction=direction,
                                asset_symbol=sl_asset,
                                lookback=lookback
                            )
                        
                        # 显示结果
                        st.success(f'✅ 计算完成 - 方法: {result.method}')
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric('当前价格', f'${result.current_price:,.2f}')
                        
                        with col2:
                            st.metric(
                                '止损价格',
                                f'${result.stop_loss_price:,.2f}',
                                f'-{result.stop_loss_pct:.2%}'
                            )
                        
                        with col3:
                            st.metric(
                                '止盈价格',
                                f'${result.take_profit_price:,.2f}',
                                f'+{result.take_profit_pct:.2%}'
                            )
                        
                        with col4:
                            rr = result.take_profit_pct / result.stop_loss_pct if result.stop_loss_pct > 0 else 0
                            st.metric('风险收益比', f'1:{rr:.2f}')
                        
                        # 说明
                        st.info(f'📝 {result.reason}')
                        
                        # ATR值
                        if hasattr(result, 'atr_value') and result.atr_value:
                            st.code(f'ATR值: {result.atr_value:.4f} (倍数: {result.atr_multiplier:.1f}x)', language='text')
                        
                        # 详细信息
                        if result.details:
                            with st.expander('详细信息'):
                                st.json(result.details)
                    else:
                        st.error(f'历史数据不足: 需要至少20天')
                        
                except Exception as e:
                    st.error(f'计算失败: {str(e)}')
                    import traceback
                    st.code(traceback.format_exc())


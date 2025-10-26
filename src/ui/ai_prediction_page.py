"""
AI预测页面 - ML和DL预测展示
AI Prediction Page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from loguru import logger

from src.ai.ml_predictor import ReturnPredictor, DirectionPredictor
from src.ai.factor_mining import FactorMiner, FactorConfig
from src.ai.ml_framework import FeatureEngineer


def show_ai_prediction_page():
    """显示AI预测页面"""
    st.title("🤖 AI智能预测")
    
    tabs = st.tabs(["📈 收益率预测", "🎯 方向预测", "🧬 因子挖掘", "📊 模型对比"])
    
    with tabs[0]:
        show_return_prediction()
    
    with tabs[1]:
        show_direction_prediction()
    
    with tabs[2]:
        show_factor_mining()
    
    with tabs[3]:
        show_model_comparison()


def show_return_prediction():
    """显示收益率预测"""
    st.header("收益率预测")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("股票代码", value="000001", key="return_symbol")
    
    with col2:
        forecast_horizon = st.selectbox(
            "预测周期",
            options=[1, 3, 5, 10, 20],
            index=2,
            key="return_horizon"
        )
    
    if st.button("🚀 开始预测", key="return_predict"):
        with st.spinner("加载数据和训练模型..."):
            try:
                # 加载数据
                from src.data_fetcher.akshare_fetcher import AKShareDataFetcher
                fetcher = AKShareDataFetcher()
                df = fetcher.fetch_stock_daily(symbol, period="1y")
                
                if df.empty:
                    st.error("无法获取数据")
                    return
                
                st.info(f"数据加载完成: {len(df)} 条记录")
                
                # 训练预测器
                predictor = ReturnPredictor(forecast_horizon=forecast_horizon)
                training_result = predictor.train(df)
                
                # 显示训练结果
                st.success("模型训练完成！")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("测试集R²", f"{training_result['test_score']:.4f}")
                with col2:
                    st.metric("交叉验证R²", f"{training_result['cv_mean']:.4f}")
                with col3:
                    st.metric("RMSE", f"{training_result['metrics']['rmse']:.6f}")
                
                # 预测
                prediction = predictor.predict(df)
                
                st.markdown("---")
                st.subheader("📊 预测结果")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        f"预测{forecast_horizon}日收益率",
                        f"{prediction.prediction:.2%}",
                        delta=f"{prediction.prediction:.2%}"
                    )
                
                with col2:
                    if prediction.confidence:
                        st.metric(
                            "预测信心度",
                            f"{prediction.confidence:.2%}"
                        )
                
                # 批量预测回测
                st.markdown("---")
                st.subheader("📉 预测回测")
                
                batch_preds = predictor.predict_batch(df, last_n=20)
                
                pred_df = pd.DataFrame([{
                    'prediction': p.prediction,
                    'timestamp': p.timestamp
                } for p in batch_preds])
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=pred_df['prediction'],
                    mode='lines+markers',
                    name='预测收益率',
                    line=dict(color='#00D9FF')
                ))
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                fig.update_layout(
                    title="最近20次预测结果",
                    yaxis_title="收益率",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 特征重要性
                if training_result.get('feature_importance'):
                    st.markdown("---")
                    st.subheader("🎯 特征重要性 (Top 10)")
                    
                    importance = training_result['feature_importance']
                    top_features = list(importance.items())[:10]
                    
                    feat_df = pd.DataFrame(top_features, columns=['特征', '重要性'])
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=feat_df['重要性'],
                            y=feat_df['特征'],
                            orientation='h',
                            marker_color='#00D9FF'
                        )
                    ])
                    fig.update_layout(
                        title="Top 10 重要特征",
                        xaxis_title="重要性",
                        template="plotly_dark",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"预测失败: {e}")
                logger.error(f"预测失败: {e}", exc_info=True)


def show_direction_prediction():
    """显示方向预测"""
    st.header("涨跌方向预测")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("股票代码", value="000001", key="dir_symbol")
    
    with col2:
        forecast_horizon = st.selectbox(
            "预测周期",
            options=[1, 3, 5, 10],
            index=2,
            key="dir_horizon"
        )
    
    if st.button("🎯 预测方向", key="dir_predict"):
        with st.spinner("训练中..."):
            try:
                from src.data_fetcher.akshare_fetcher import AKShareDataFetcher
                fetcher = AKShareDataFetcher()
                df = fetcher.fetch_stock_daily(symbol, period="1y")
                
                if df.empty:
                    st.error("无法获取数据")
                    return
                
                predictor = DirectionPredictor(forecast_horizon=forecast_horizon)
                training_result = predictor.train(df)
                prediction = predictor.predict(df)
                
                st.success("预测完成！")
                
                # 显示结果
                direction = "📈 看涨" if prediction.prediction > 0.5 else "📉 看跌"
                confidence = prediction.prediction if prediction.prediction > 0.5 else (1 - prediction.prediction)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        f"{forecast_horizon}日方向预测",
                        direction
                    )
                with col2:
                    st.metric(
                        "预测概率",
                        f"{confidence:.2%}"
                    )
                
            except Exception as e:
                st.error(f"预测失败: {e}")


def show_factor_mining():
    """显示因子挖掘"""
    st.header("自动因子挖掘")
    
    st.info("💡 使用遗传编程自动发现Alpha因子")
    
    symbol = st.text_input("股票代码", value="000001", key="factor_symbol")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        population_size = st.slider("种群大小", 20, 200, 50)
    
    with col2:
        generations = st.slider("迭代代数", 5, 50, 10)
    
    with col3:
        min_ic = st.slider("最小IC阈值", 0.01, 0.1, 0.02, 0.01)
    
    if st.button("⚗️ 开始挖掘", key="factor_mine"):
        with st.spinner("因子挖掘中...这可能需要几分钟..."):
            try:
                from src.data_fetcher.akshare_fetcher import AKShareDataFetcher
                fetcher = AKShareDataFetcher()
                df = fetcher.fetch_stock_daily(symbol, period="2y")
                
                if df.empty:
                    st.error("无法获取数据")
                    return
                
                # 创建特征
                df['returns'] = df['close'].pct_change()
                df['ma_5'] = df['close'].rolling(5).mean()
                df['ma_20'] = df['close'].rolling(20).mean()
                df['volatility'] = df['returns'].rolling(10).std()
                df['forward_returns'] = df['close'].pct_change(5).shift(-5)
                df = df.dropna()
                
                # 配置因子挖掘
                config = FactorConfig(
                    population_size=population_size,
                    generations=generations,
                    min_ic=min_ic
                )
                
                miner = FactorMiner(config)
                result = miner.mine_factors(df, target_column='forward_returns')
                
                st.success(f"因子挖掘完成！发现 {len(result.all_factors)} 个有效因子")
                
                # 最佳因子
                if result.best_factor:
                    st.markdown("---")
                    st.subheader("🏆 最佳因子")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("IC", f"{result.best_factor.ic:.4f}")
                    with col2:
                        st.metric("IC_IR", f"{result.best_factor.ic_ir:.4f}")
                    with col3:
                        st.metric("Rank IC", f"{result.best_factor.rank_ic:.4f}")
                    
                    st.code(result.best_factor.expression, language="python")
                
                # Top因子列表
                st.markdown("---")
                st.subheader("🎯 Top 10 因子")
                
                factor_data = []
                for i, factor in enumerate(result.top_factors[:10], 1):
                    factor_data.append({
                        '排名': i,
                        'IC': f"{factor.ic:.4f}",
                        'IC_IR': f"{factor.ic_ir:.4f}",
                        '表达式': factor.expression[:80] + '...' if len(factor.expression) > 80 else factor.expression
                    })
                
                st.dataframe(pd.DataFrame(factor_data), use_container_width=True)
                
                # 迭代历史
                st.markdown("---")
                st.subheader("📈 迭代历史")
                
                gen_data = pd.DataFrame(result.generation_stats)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=gen_data['generation'],
                    y=gen_data['best_fitness'],
                    mode='lines+markers',
                    name='最佳适应度',
                    line=dict(color='#00D9FF')
                ))
                fig.update_layout(
                    title="遗传算法收敛曲线",
                    xaxis_title="代数",
                    yaxis_title="适应度",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"因子挖掘失败: {e}")
                logger.error(f"因子挖掘失败: {e}", exc_info=True)


def show_model_comparison():
    """显示模型对比"""
    st.header("模型性能对比")
    
    st.info("比较不同模型的预测性能")
    
    symbol = st.text_input("股票代码", value="000001", key="compare_symbol")
    forecast_horizon = st.selectbox("预测周期", options=[3, 5, 10], index=1)
    
    if st.button("🔬 开始对比", key="compare"):
        with st.spinner("训练多个模型..."):
            try:
                from src.data_fetcher.akshare_fetcher import AKShareDataFetcher
                from src.ai.ml_framework import MLFramework, MLConfig
                
                fetcher = AKShareDataFetcher()
                df = fetcher.fetch_stock_daily(symbol, period="1y")
                
                if df.empty:
                    st.error("无法获取数据")
                    return
                
                # 准备数据
                features = FeatureEngineer.create_technical_features(df)
                features['target'] = df['close'].pct_change(forecast_horizon).shift(-forecast_horizon)
                features = features.dropna()
                
                # 测试多个模型
                models = ['random_forest', 'gbdt', 'ridge']
                results = []
                
                progress_bar = st.progress(0)
                
                for i, model_type in enumerate(models):
                    config = MLConfig(model_type=model_type, target_column='target')
                    framework = MLFramework(config)
                    
                    X, y, feature_names = framework.prepare_data(features, 'target')
                    result = framework.train(X, y)
                    
                    results.append({
                        '模型': model_type.upper(),
                        '测试集R²': result.test_score,
                        '交叉验证R²': result.cv_mean,
                        'RMSE': result.metrics['rmse'],
                        'MAE': result.metrics['mae']
                    })
                    
                    progress_bar.progress((i + 1) / len(models))
                
                # 显示对比表格
                result_df = pd.DataFrame(results)
                
                st.subheader("📊 模型性能对比")
                st.dataframe(result_df, use_container_width=True)
                
                # 可视化对比
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='测试集R²',
                    x=result_df['模型'],
                    y=result_df['测试集R²'],
                    marker_color='#00D9FF'
                ))
                
                fig.add_trace(go.Bar(
                    name='交叉验证R²',
                    x=result_df['模型'],
                    y=result_df['交叉验证R²'],
                    marker_color='#FF6B6B'
                ))
                
                fig.update_layout(
                    title="模型R²对比",
                    barmode='group',
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"对比失败: {e}")


if __name__ == "__main__":
    show_ai_prediction_page()

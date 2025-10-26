"""
AI助手模块 - DeepSeek智能分析
提供投资建议、市场解读、策略优化等AI服务
"""
import streamlit as st
from openai import OpenAI
from typing import Dict, List, Any, Optional
import json


class AIAssistant:
    """AI助手类 - 基于DeepSeek API"""
    
    def __init__(self, api_key: str):
        """
        初始化AI助手
        
        Args:
            api_key: DeepSeek API密钥
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
        
        # 系统提示词 - Apple风格专业AI
        self.system_prompt = """你是一位资深量化金融分析师，精通：
- 技术分析（K线、均线、MACD、RSI、KDJ等指标）
- 基本面分析（市值、交易量、市场情绪）
- 风险管理（止损止盈、仓位控制）
- 加密货币与ETF市场动态

回答风格要求：
1. **简洁专业**：像Apple产品介绍一样，直击要点
2. **数据驱动**：基于用户提供的技术指标给出建议
3. **风险提示**：必须包含风险提示，符合金融合规要求
4. **结构清晰**：使用Markdown格式，分段明确

禁止：
- 不要保证收益
- 不要推荐具体买卖点位
- 不要给出100%确定的判断
"""
    
    def chat(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        与AI对话
        
        Args:
            user_message: 用户消息
            context: 上下文数据（技术指标、价格等）
            
        Returns:
            AI回复内容
        """
        try:
            # 构建上下文信息
            context_str = ""
            if context:
                context_str = f"\n\n当前数据上下文：\n```json\n{json.dumps(context, indent=2, ensure_ascii=False)}\n```"
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message + context_str}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"⚠️ AI服务暂时不可用：{str(e)}\n\n请稍后重试或检查API配置。"
    
    def analyze_market(self, asset_data: Dict[str, Any]) -> str:
        """
        分析市场数据
        
        Args:
            asset_data: 资产数据（包含价格、指标等）
            
        Returns:
            分析结果
        """
        prompt = f"""请分析以下资产的市场状况：

**资产信息：**
- 名称：{asset_data.get('name', 'N/A')}
- 当前价格：${asset_data.get('price', 0):,.2f}
- 24h涨跌：{asset_data.get('change_24h', 0):+.2f}%
- 交易量：${asset_data.get('volume', 0):,.0f}

**技术指标：**
{json.dumps(asset_data.get('indicators', {}), indent=2, ensure_ascii=False)}

请从以下角度分析：
1. 当前趋势判断
2. 技术指标解读
3. 支撑位/阻力位
4. 风险提示
"""
        return self.chat(prompt, context=asset_data)
    
    def get_investment_advice(
        self, 
        portfolio: List[Dict[str, Any]], 
        risk_level: str = 'medium'
    ) -> str:
        """
        获取投资建议
        
        Args:
            portfolio: 投资组合数据
            risk_level: 风险偏好 ('low', 'medium', 'high')
            
        Returns:
            投资建议
        """
        risk_desc = {
            'low': '保守型（优先保本，接受低收益）',
            'medium': '稳健型（平衡风险与收益）',
            'high': '激进型（追求高收益，承受高风险）'
        }
        
        prompt = f"""请为以下投资组合提供建议：

**风险偏好：** {risk_desc.get(risk_level, '稳健型')}

**当前持仓：**
{json.dumps(portfolio, indent=2, ensure_ascii=False)}

请提供：
1. 组合诊断（资产配比、风险评估）
2. 优化建议（调仓方向）
3. 风险控制策略
4. 下一步操作建议
"""
        return self.chat(prompt, context={'portfolio': portfolio, 'risk_level': risk_level})
    
    def explain_signal(self, signal_data: Dict[str, Any]) -> str:
        """
        解释交易信号
        
        Args:
            signal_data: 信号数据
            
        Returns:
            信号解释
        """
        prompt = f"""请解释以下交易信号的含义：

**信号类型：** {signal_data.get('signal', 'N/A')}
**信心度：** {signal_data.get('confidence', 0):.0f}%
**信号强度：** {signal_data.get('strength', 'N/A')}

**详细指标：**
{json.dumps(signal_data.get('details', {}), indent=2, ensure_ascii=False)}

请说明：
1. 该信号的技术原理
2. 当前市场环境下的可靠性
3. 建议的操作策略
4. 需要注意的风险点
"""
        return self.chat(prompt, context=signal_data)
    
    def compare_assets(self, assets: List[Dict[str, Any]]) -> str:
        """
        对比多个资产
        
        Args:
            assets: 资产列表
            
        Returns:
            对比分析
        """
        prompt = f"""请对比以下资产的投资价值：

{json.dumps(assets, indent=2, ensure_ascii=False)}

请从以下维度对比：
1. 风险收益比
2. 流动性
3. 成长潜力
4. 当前估值水平
5. 推荐排序及理由
"""
        return self.chat(prompt, context={'assets': assets})


@st.cache_resource
def init_ai_assistant(api_key: str) -> Optional[AIAssistant]:
    """
    初始化AI助手（缓存单例）
    
    Args:
        api_key: DeepSeek API密钥
        
    Returns:
        AI助手实例
    """
    try:
        if not api_key or api_key == "your_deepseek_api_key_here":
            return None
        return AIAssistant(api_key)
    except Exception as e:
        st.error(f"AI助手初始化失败: {str(e)}")
        return None


def show_ai_chat_interface(ai_assistant: AIAssistant, context: Dict[str, Any] = None):
    """
    显示AI对话界面（Apple风格）
    
    Args:
        ai_assistant: AI助手实例
        context: 上下文数据
    """
    st.markdown("""
    <div style="text-align: center; margin-bottom: 32px;">
        <h2 style="font-size: 48px; font-weight: 700; color: #F5F5F7; 
            letter-spacing: -0.03em; margin-bottom: 12px;">
            🤖 AI投资顾问
        </h2>
        <p style="font-size: 17px; color: #86868B; max-width: 560px; margin: 0 auto;">
            基于DeepSeek的智能分析助手，为您提供专业的投资建议
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化对话历史
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 快捷问题按钮
    st.markdown("### 💡 快捷问题")
    col1, col2, col3 = st.columns(3)
    
    quick_questions = [
        "分析当前市场趋势",
        "如何优化我的投资组合？",
        "如何设置止损止盈？"
    ]
    
    for idx, (col, question) in enumerate(zip([col1, col2, col3], quick_questions)):
        with col:
            if st.button(question, key=f"quick_{idx}", use_container_width=True):
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': question
                })
                with st.spinner('🤔 AI正在思考...'):
                    response = ai_assistant.chat(question, context)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                st.rerun()
    
    # 对话历史显示
    st.markdown("### 💬 对话记录")
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="modern-card" style="background: rgba(0, 113, 227, 0.1); 
                border-left: 3px solid #0071E3; margin-bottom: 16px;">
                <strong style="color: #0071E3;">👤 您：</strong><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="modern-card" style="background: rgba(48, 209, 88, 0.1); 
                border-left: 3px solid #30D158; margin-bottom: 16px;">
                <strong style="color: #30D158;">🤖 AI顾问：</strong><br>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # 输入框
    st.markdown("### ✍️ 提问")
    user_input = st.text_area(
        "输入您的问题",
        placeholder="例如：BTC现在适合买入吗？如何判断ETF的买卖时机？",
        height=100,
        key="ai_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🚀 发送", type="primary", use_container_width=True):
            if user_input.strip():
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                with st.spinner('🤔 AI正在分析...'):
                    response = ai_assistant.chat(user_input, context)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                st.rerun()
    
    with col2:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

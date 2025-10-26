"""
Lottie 动画示例和加载工具
用于 Premium UI 的加载和空态动画
"""
import streamlit as st

# Lottie 动画 URL 集合
LOTTIE_ANIMATIONS = {
    # 加载动画
    'loading': 'https://assets10.lottiefiles.com/packages/lf20_hxart6lz.json',
    'loading_dots': 'https://assets3.lottiefiles.com/packages/lf20_yyytcpk0.json',
    'loading_chart': 'https://assets9.lottiefiles.com/packages/lf20_nxjfr4ma.json',
    
    # 成功动画
    'success': 'https://assets9.lottiefiles.com/packages/lf20_jbrw3hcz.json',
    'checkmark': 'https://assets4.lottiefiles.com/packages/lf20_atipq6bq.json',
    
    # 空态动画
    'empty': 'https://assets4.lottiefiles.com/packages/lf20_uu3p3ahq.json',
    'no_data': 'https://assets5.lottiefiles.com/packages/lf20_qvcmm4on.json',
    
    # 错误动画
    'error': 'https://assets9.lottiefiles.com/packages/lf20_ddxv3rxw.json',
    
    # 金融相关
    'money': 'https://assets3.lottiefiles.com/packages/lf20_06a6pf9i.json',
    'chart_up': 'https://assets1.lottiefiles.com/packages/lf20_zw0djhar.json',
    'wallet': 'https://assets2.lottiefiles.com/packages/lf20_yw5n3o9m.json',
}


def load_lottie_url(url: str):
    """从 URL 加载 Lottie 动画"""
    try:
        import requests
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"加载 Lottie 动画失败: {str(e)}")
        return None


def show_lottie_animation(animation_key: str, height: int = 200, key: str = None):
    """
    显示 Lottie 动画
    
    参数:
        animation_key: LOTTIE_ANIMATIONS 中的键
        height: 动画高度
        key: Streamlit 组件的唯一键
    """
    try:
        from streamlit_lottie import st_lottie
        
        if animation_key not in LOTTIE_ANIMATIONS:
            st.warning(f"动画 '{animation_key}' 不存在")
            return
        
        url = LOTTIE_ANIMATIONS[animation_key]
        lottie_json = load_lottie_url(url)
        
        if lottie_json:
            st_lottie(
                lottie_json,
                height=height,
                key=key,
                quality='high',
                speed=1.0,
            )
        else:
            st.info("加载动画中...")
            
    except ImportError:
        st.warning("streamlit-lottie 未安装。运行: pip install streamlit-lottie")


def show_loading_state(message: str = "加载中...", animation: str = 'loading'):
    """
    显示加载状态（带 Lottie 动画）
    
    参数:
        message: 提示信息
        animation: 动画键
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        show_lottie_animation(animation, height=150)
        st.markdown(f"""
        <div style="text-align: center; color: rgba(255,255,255,0.78); margin-top: 1rem;">
            {message}
        </div>
        """, unsafe_allow_html=True)


def show_empty_state(title: str = "暂无数据", message: str = "", animation: str = 'empty'):
    """
    显示空态（带 Lottie 动画）
    
    参数:
        title: 标题
        message: 说明信息
        animation: 动画键
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        show_lottie_animation(animation, height=200)
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <h3 style="color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: rgba(255,255,255,0.56);">{message}</p>
        </div>
        """, unsafe_allow_html=True)


def show_success_animation(message: str = "操作成功！", duration: float = 2.0):
    """
    显示成功动画
    
    参数:
        message: 提示信息
        duration: 显示时长（秒）
    """
    import time
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        show_lottie_animation('success', height=150, key=f"success_{time.time()}")
        st.success(message)
    
    time.sleep(duration)


# ==================== 使用示例 ====================
def demo_lottie_animations():
    """演示所有 Lottie 动画"""
    st.title("Lottie 动画示例")
    
    st.markdown("### 加载动画")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Loading**")
        show_lottie_animation('loading', height=150, key='demo_loading')
    with cols[1]:
        st.markdown("**Loading Dots**")
        show_lottie_animation('loading_dots', height=150, key='demo_loading_dots')
    with cols[2]:
        st.markdown("**Loading Chart**")
        show_lottie_animation('loading_chart', height=150, key='demo_loading_chart')
    
    st.markdown("---")
    st.markdown("### 状态动画")
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Success**")
        show_lottie_animation('success', height=150, key='demo_success')
    with cols[1]:
        st.markdown("**Empty**")
        show_lottie_animation('empty', height=150, key='demo_empty')
    with cols[2]:
        st.markdown("**Error**")
        show_lottie_animation('error', height=150, key='demo_error')
    
    st.markdown("---")
    st.markdown("### 金融动画")
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Money**")
        show_lottie_animation('money', height=150, key='demo_money')
    with cols[1]:
        st.markdown("**Chart Up**")
        show_lottie_animation('chart_up', height=150, key='demo_chart_up')
    with cols[2]:
        st.markdown("**Wallet**")
        show_lottie_animation('wallet', height=150, key='demo_wallet')
    
    st.markdown("---")
    st.markdown("### 使用示例")
    
    if st.button("显示加载状态"):
        show_loading_state("正在获取数据...")
    
    if st.button("显示空态"):
        show_empty_state("暂无交易记录", "请先添加一些交易数据")
    
    if st.button("显示成功动画"):
        show_success_animation("数据同步成功！")


# ==================== 内联 Lottie JSON（备用方案）====================
# 如果无法访问外部 URL，可以使用内联 JSON

INLINE_LOADING_ANIMATION = {
    "v": "5.5.7",
    "fr": 60,
    "ip": 0,
    "op": 180,
    "w": 200,
    "h": 200,
    "nm": "Loading",
    "ddd": 0,
    "assets": [],
    "layers": [
        {
            "ddd": 0,
            "ind": 1,
            "ty": 4,
            "nm": "circle",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 1, "k": [
                    {"i": {"x": [0.833], "y": [0.833]}, "o": {"x": [0.167], "y": [0.167]}, "t": 0, "s": [0]},
                    {"t": 180, "s": [360]}
                ]},
                "p": {"a": 0, "k": [100, 100, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "shapes": [
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "el",
                            "s": {"a": 0, "k": [60, 60]},
                            "p": {"a": 0, "k": [0, 0]}
                        },
                        {
                            "ty": "st",
                            "c": {"a": 0, "k": [1, 0.478, 0.161, 1]},
                            "o": {"a": 0, "k": 100},
                            "w": {"a": 0, "k": 8}
                        }
                    ]
                }
            ]
        }
    ]
}


def show_inline_loading():
    """显示内联加载动画（不需要网络）"""
    try:
        from streamlit_lottie import st_lottie
        st_lottie(INLINE_LOADING_ANIMATION, height=150)
    except ImportError:
        st.spinner("加载中...")


if __name__ == "__main__":
    # 运行演示
    demo_lottie_animations()

"""
Streamlit错误显示辅助函数
提供统一的错误UI展示
"""
import streamlit as st
from typing import Optional


def show_error_with_solutions(
    message: str,
    solutions: list,
    detailed_trace: Optional[str] = None
):
    """
    显示带解决方案的错误信息
    
    Args:
        message: 错误消息
        solutions: 解决方案列表
        detailed_trace: 详细堆栈跟踪(可选)
    """
    # 显示主错误消息
    st.error(message)
    
    # 显示解决方案
    if solutions:
        st.markdown("**💡 建议的解决方案:**")
        for i, solution in enumerate(solutions, 1):
            st.markdown(f"{i}. {solution}")
    
    # 可展开的详细错误信息
    if detailed_trace:
        with st.expander("🔍 查看详细错误信息 (供开发者参考)"):
            st.code(detailed_trace, language="python")


def show_error_dict(error_dict: dict):
    """
    显示错误信息字典
    
    Args:
        error_dict: 包含message, solutions, detailed_trace的字典
    """
    show_error_with_solutions(
        error_dict.get('message', '发生未知错误'),
        error_dict.get('solutions', []),
        error_dict.get('detailed_trace')
    )


def show_warning_with_info(message: str, info_items: list):
    """
    显示警告信息和说明
    
    Args:
        message: 警告消息
        info_items: 信息列表
    """
    st.warning(message)
    if info_items:
        st.markdown("**ℹ️ 相关信息:**")
        for item in info_items:
            st.markdown(f"• {item}")


def show_data_quality_warning(issues: list):
    """
    显示数据质量警告
    
    Args:
        issues: 数据质量问题列表
    """
    st.warning("⚠️ 数据质量问题")
    st.markdown("检测到以下数据质量问题,可能影响分析结果:")
    for issue in issues:
        st.markdown(f"• {issue}")
    st.info("💡 建议: 尝试更换时间范围或等待数据更新后重试")


def show_network_error():
    """显示网络错误的标准消息"""
    show_error_with_solutions(
        "🌐 网络连接失败",
        [
            "检查您的网络连接",
            "如果使用VPN,请尝试切换节点",
            "点击刷新按钮重试",
            "如果问题持续,可能是数据源暂时不可用"
        ]
    )


def show_data_insufficient_error(min_required: int, actual: int):
    """
    显示数据不足错误
    
    Args:
        min_required: 最少需要的数据点数
        actual: 实际获取的数据点数
    """
    show_error_with_solutions(
        f"📉 数据不足: 需要至少 {min_required} 个数据点,当前只有 {actual} 个",
        [
            "尝试选择更长的时间范围",
            "该资产可能是新上市的,历史数据有限",
            "选择其他资产进行分析"
        ]
    )


def show_api_error(api_name: str, status_code: Optional[int] = None):
    """
    显示API错误
    
    Args:
        api_name: API名称
        status_code: HTTP状态码(可选)
    """
    message = f"🔌 {api_name} API 请求失败"
    if status_code:
        message += f" (HTTP {status_code})"
    
    solutions = [
        f"{api_name} 可能暂时不可用",
        "等待 5-10 分钟后重试",
        "检查 API 配置是否正确"
    ]
    
    if status_code == 429:
        solutions.insert(0, "API 请求频率超限,请稍后再试")
    elif status_code == 401 or status_code == 403:
        solutions.insert(0, "API 认证失败,请检查 API Key 配置")
    
    show_error_with_solutions(message, solutions)


def show_cache_info():
    """显示缓存信息提示"""
    st.info("""
    💾 **关于数据缓存**
    
    为提升性能和减少API调用,系统使用了智能缓存:
    - 实时数据: 缓存 5 分钟
    - 历史数据: 缓存 1 小时  
    - 估值数据: 缓存 24 小时
    
    如需获取最新数据,请点击刷新按钮清除缓存。
    """)


def show_loading_status(message: str, progress: Optional[float] = None):
    """
    显示加载状态
    
    Args:
        message: 状态消息
        progress: 进度 (0-1之间的浮点数,可选)
    """
    if progress is not None:
        st.progress(progress, text=message)
    else:
        with st.spinner(message):
            pass

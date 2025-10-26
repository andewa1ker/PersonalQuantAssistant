"""
增强的错误处理模块
提供友好的错误消息和解决方案建议
"""
from typing import Tuple, Optional
import traceback as tb


class ErrorHandler:
    """统一错误处理器"""
    
    # 常见错误类型及解决方案
    ERROR_SOLUTIONS = {
        'ConnectionError': {
            'message': '🌐 网络连接失败',
            'solutions': [
                '检查网络连接是否正常',
                '如果使用VPN,请尝试切换节点',
                '稍后重试或点击刷新按钮',
                '检查防火墙设置'
            ]
        },
        'Timeout': {
            'message': '⏱️ 请求超时',
            'solutions': [
                '网络响应较慢,请稍后重试',
                '尝试刷新页面',
                '检查网络连接速度'
            ]
        },
        'HTTPError': {
            'message': '🔌 API请求失败',
            'solutions': [
                '数据源可能暂时不可用',
                '检查API配置是否正确',
                '等待5-10分钟后重试',
                '如持续失败,请联系管理员'
            ]
        },
        'KeyError': {
            'message': '📊 数据格式异常',
            'solutions': [
                '数据源返回格式可能已变更',
                '尝试刷新获取最新数据',
                '如果问题持续,请反馈给开发者'
            ]
        },
        'ValueError': {
            'message': '⚠️ 数据值异常',
            'solutions': [
                '收到的数据无效或不完整',
                '尝试切换其他资产查看',
                '清除缓存后重新获取'
            ]
        },
        'IndexError': {
            'message': '📉 数据不足',
            'solutions': [
                '历史数据量不足以进行分析',
                '该资产可能是新上市的',
                '尝试选择其他时间范围'
            ]
        },
        'AttributeError': {
            'message': '🔧 系统组件异常',
            'solutions': [
                '系统组件可能未正确初始化',
                '尝试刷新页面',
                '如果问题持续,请检查日志文件'
            ]
        }
    }
    
    @staticmethod
    def get_friendly_error(
        exception: Exception,
        context: str = ""
    ) -> Tuple[str, list, str]:
        """
        获取友好的错误信息
        
        Args:
            exception: 异常对象
            context: 错误上下文描述
            
        Returns:
            (错误消息, 解决方案列表, 详细堆栈)
        """
        error_type = type(exception).__name__
        error_str = str(exception)
        
        # 获取预定义的错误信息
        error_info = ErrorHandler.ERROR_SOLUTIONS.get(
            error_type,
            {
                'message': f'❌ 系统错误: {error_type}',
                'solutions': [
                    '这是一个未知错误',
                    '请尝试刷新页面',
                    '如问题持续,请查看详细错误信息或联系技术支持'
                ]
            }
        )
        
        # 构建完整错误消息
        message = error_info['message']
        if context:
            message = f"{message} ({context})"
        if error_str and len(error_str) < 100:
            message += f"\n详情: {error_str}"
        
        # 获取解决方案
        solutions = error_info['solutions']
        
        # 获取详细堆栈
        detailed_trace = tb.format_exc()
        
        return message, solutions, detailed_trace
    
    @staticmethod
    def get_data_fetch_error(asset_type: str, symbol: str) -> Tuple[str, list]:
        """
        获取数据获取失败的错误信息
        
        Args:
            asset_type: 资产类型
            symbol: 资产代码
            
        Returns:
            (错误消息, 解决方案列表)
        """
        asset_names = {
            'etf': 'ETF',
            'stock': '股票',
            'crypto': '加密货币'
        }
        asset_name = asset_names.get(asset_type, asset_type)
        
        message = f"📡 无法获取 {symbol} 的{asset_name}数据"
        
        solutions = [
            f'确认 {symbol} 代码是否正确',
            '检查网络连接',
            '数据源可能暂时不可用,请稍后重试',
        ]
        
        if asset_type == 'etf':
            solutions.append('确认该ETF是否在交易时间内')
        elif asset_type == 'crypto':
            solutions.extend([
                '加密货币市场7x24小时运行,但API可能有维护',
                '尝试使用其他币种'
            ])
        
        return message, solutions
    
    @staticmethod
    def get_analysis_error(analysis_type: str) -> Tuple[str, list]:
        """
        获取分析失败的错误信息
        
        Args:
            analysis_type: 分析类型 (technical, signal等)
            
        Returns:
            (错误消息, 解决方案列表)
        """
        analysis_names = {
            'technical': '技术分析',
            'signal': '信号生成',
            'trend': '趋势分析',
            'volatility': '波动率分析'
        }
        analysis_name = analysis_names.get(analysis_type, analysis_type)
        
        message = f"📊 {analysis_name}失败"
        
        solutions = [
            '数据可能不足或格式异常',
            '尝试选择更长的时间范围',
            '刷新页面重新获取数据',
            '如果问题持续,请检查数据质量'
        ]
        
        return message, solutions
    
    @staticmethod
    def format_error_display(
        message: str,
        solutions: list,
        detailed_trace: Optional[str] = None,
        show_details: bool = False
    ) -> dict:
        """
        格式化错误显示信息
        
        Args:
            message: 错误消息
            solutions: 解决方案列表
            detailed_trace: 详细堆栈跟踪
            show_details: 是否默认显示详情
            
        Returns:
            格式化后的错误信息字典
        """
        return {
            'message': message,
            'solutions': solutions,
            'detailed_trace': detailed_trace,
            'show_details': show_details
        }


def handle_exception(
    exception: Exception,
    context: str = "",
    return_trace: bool = True
) -> dict:
    """
    快捷函数:处理异常并返回格式化信息
    
    Args:
        exception: 异常对象
        context: 上下文
        return_trace: 是否返回详细堆栈
        
    Returns:
        错误信息字典
    """
    message, solutions, trace = ErrorHandler.get_friendly_error(exception, context)
    return ErrorHandler.format_error_display(
        message,
        solutions,
        trace if return_trace else None
    )


def handle_data_error(asset_type: str, symbol: str) -> dict:
    """
    快捷函数:处理数据获取错误
    
    Args:
        asset_type: 资产类型
        symbol: 资产代码
        
    Returns:
        错误信息字典
    """
    message, solutions = ErrorHandler.get_data_fetch_error(asset_type, symbol)
    return ErrorHandler.format_error_display(message, solutions)


def handle_analysis_error(analysis_type: str, exception: Exception = None) -> dict:
    """
    快捷函数:处理分析错误
    
    Args:
        analysis_type: 分析类型
        exception: 异常对象(可选)
        
    Returns:
        错误信息字典
    """
    message, solutions = ErrorHandler.get_analysis_error(analysis_type)
    
    detailed_trace = None
    if exception:
        detailed_trace = tb.format_exc()
    
    return ErrorHandler.format_error_display(message, solutions, detailed_trace)

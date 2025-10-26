"""
日志配置模块
使用loguru提供更好的日志体验
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, log_level: str = "INFO", log_dir: Optional[Path] = None):
        """
        初始化日志管理器
        
        Args:
            log_level: 日志级别
            log_dir: 日志目录
        """
        self.log_level = log_level.upper()
        
        if log_dir is None:
            self.log_dir = Path(__file__).parent.parent.parent / "data" / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=self.log_level,
            colorize=True,
        )
        
        # 添加文件处理器 - 所有日志
        logger.add(
            self.log_dir / "app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=self.log_level,
            rotation="00:00",  # 每天午夜轮换
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            encoding="utf-8",
        )
        
        # 添加错误日志文件
        logger.add(
            self.log_dir / "error_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="00:00",
            retention="90 days",  # 错误日志保留更久
            compression="zip",
            encoding="utf-8",
        )
        
        logger.info(f"日志系统初始化完成 - 级别: {self.log_level}, 目录: {self.log_dir}")
    
    def get_logger(self):
        """获取logger实例"""
        return logger


def setup_logger(log_level: str = "INFO", log_dir: Optional[Path] = None):
    """
    设置日志系统
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
        
    Returns:
        logger实例
    """
    manager = LoggerManager(log_level, log_dir)
    return manager.get_logger()


# 默认logger实例
log = logger


if __name__ == "__main__":
    # 测试日志
    test_logger = setup_logger("DEBUG")
    
    test_logger.debug("这是一条DEBUG消息")
    test_logger.info("这是一条INFO消息")
    test_logger.warning("这是一条WARNING消息")
    test_logger.error("这是一条ERROR消息")
    test_logger.success("这是一条SUCCESS消息")

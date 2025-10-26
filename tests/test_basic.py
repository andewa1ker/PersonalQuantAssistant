"""
单元测试示例
运行: pytest tests/
"""
import pytest
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestConfigLoader:
    """测试配置加载器"""
    
    def test_config_loader_import(self):
        """测试能否导入配置模块"""
        from utils.config_loader import get_config
        config = get_config()
        assert config is not None
    
    def test_app_config(self):
        """测试应用配置"""
        from utils.config_loader import get_config
        config = get_config()
        assert config.app_name == "Personal Quant Assistant"
        assert config.app_version == "1.0.0"
    
    def test_enabled_assets(self):
        """测试启用的资产"""
        from utils.config_loader import get_config
        config = get_config()
        enabled_assets = config.get_enabled_assets()
        assert isinstance(enabled_assets, dict)
        assert len(enabled_assets) >= 0


class TestLogger:
    """测试日志系统"""
    
    def test_logger_import(self):
        """测试能否导入日志模块"""
        # 由于loguru可能未安装，这里只测试导入
        try:
            from utils.logger import setup_logger
            logger = setup_logger("DEBUG")
            assert logger is not None
        except ImportError:
            pytest.skip("loguru未安装")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

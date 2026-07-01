"""
WiFi可视化安全学习工具 v2 - 测试文件
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports(unittest.TestCase):
    """测试模块导入"""

    def test_core_imports(self):
        """测试核心模块导入"""
        from src.core.logger import get_logger
        from src.core.config import ConfigManager
        from src.core.safety import SafetyManager, OperationLevel
        self.assertIsNotNone(get_logger)
        self.assertIsNotNone(ConfigManager)
        self.assertIsNotNone(SafetyManager)
        self.assertIsNotNone(OperationLevel)

    def test_modules_imports(self):
        """测试功能模块导入"""
        from src.modules.wifi_scanner import WiFiScanner, get_wifi_scanner
        from src.modules.security_eval import NetworkSecurityEvaluator
        self.assertIsNotNone(WiFiScanner)
        self.assertIsNotNone(get_wifi_scanner)
        self.assertIsNotNone(NetworkSecurityEvaluator)

    def test_ai_imports(self):
        """测试AI模块导入"""
        from src.ai.api_client import AIClient
        from src.ai.prompts import PromptManager
        self.assertIsNotNone(AIClient)
        self.assertIsNotNone(PromptManager)


class TestLogger(unittest.TestCase):
    """测试日志模块"""

    def test_get_logger(self):
        """测试获取日志记录器"""
        from src.core.logger import get_logger
        logger = get_logger("test")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test")


class TestConfig(unittest.TestCase):
    """测试配置管理"""

    def test_config_default(self):
        """测试默认配置"""
        from src.core.config import ConfigManager
        config = ConfigManager()
        self.assertIsNotNone(config)
        self.assertEqual(config.get("theme"), "cyberpunk")
        self.assertEqual(config.get("gentle_mode"), True)


class TestSafety(unittest.TestCase):
    """测试安全框架"""

    def test_safety_manager_init(self):
        """测试安全管理器初始化"""
        from src.core.safety import SafetyManager, OperationLevel
        safety = SafetyManager(gentle_mode=True)
        self.assertTrue(safety.gentle_mode)
        self.assertIsNotNone(safety._operations)

    def test_register_operation(self):
        """测试注册操作"""
        from src.core.safety import SafetyManager, OperationLevel
        safety = SafetyManager()
        safety.register_operation("test_op", OperationLevel.SAFE, "测试操作")
        self.assertIn("test_op", safety._operations)

    def test_check_safe_operation(self):
        """测试检查安全操作"""
        from src.core.safety import SafetyManager, OperationLevel
        safety = SafetyManager()
        safety.register_operation("safe_op", OperationLevel.SAFE, "安全操作")
        self.assertTrue(safety.check_operation("safe_op"))

    def test_check_dangerous_in_gentle_mode(self):
        """测试温和模式下危险操作"""
        from src.core.safety import SafetyManager, OperationLevel
        safety = SafetyManager(gentle_mode=True)
        safety.register_operation("dangerous_op", OperationLevel.DANGEROUS, "危险操作")
        self.assertFalse(safety.check_operation("dangerous_op"))

    def test_dual_password_set_check(self):
        """测试双密码设置检查"""
        from src.core.safety import SafetyManager
        safety = SafetyManager()
        self.assertFalse(safety.is_dual_password_set())


class TestWiFiScanner(unittest.TestCase):
    """测试WiFi扫描"""

    def test_get_wifi_scanner(self):
        """测试获取WiFi扫描器"""
        from src.modules.wifi_scanner import get_wifi_scanner, WiFiScanner
        scanner = get_wifi_scanner()
        self.assertIsInstance(scanner, WiFiScanner)

    def test_wifi_scanner_init(self):
        """测试WiFi扫描器初始化"""
        from src.modules.wifi_scanner import WindowsWiFiScanner
        scanner = WindowsWiFiScanner()
        self.assertIsNotNone(scanner)


class TestSecurityEval(unittest.TestCase):
    """测试安全评估"""

    def test_evaluator_init(self):
        """测试评估器初始化"""
        from src.modules.security_eval import NetworkSecurityEvaluator
        evaluator = NetworkSecurityEvaluator()
        self.assertIsNotNone(evaluator)

    def test_encryption_rating(self):
        """测试加密方式评级"""
        from src.modules.security_eval import NetworkSecurityEvaluator
        evaluator = NetworkSecurityEvaluator()
        rating = evaluator.rate_encryption("WEP")
        self.assertEqual(rating.level, "危险")
        self.assertEqual(rating.score, 0)

        rating = evaluator.rate_encryption("WPA2")
        self.assertEqual(rating.level, "中")
        self.assertEqual(rating.score, 70)

    def test_password_strength_weak(self):
        """测试弱密码检测"""
        from src.modules.security_eval import NetworkSecurityEvaluator
        evaluator = NetworkSecurityEvaluator()
        result = evaluator.evaluate_password("123456")
        self.assertLess(result.total_score, 40)
        self.assertEqual(result.level, "弱")

    def test_password_strength_strong(self):
        """测试强密码检测"""
        from src.modules.security_eval import NetworkSecurityEvaluator
        evaluator = NetworkSecurityEvaluator()
        result = evaluator.evaluate_password("MyStr0ng!Pass#2024")
        self.assertGreater(result.total_score, 60)


class TestAIClient(unittest.TestCase):
    """测试AI客户端"""

    def test_prompt_manager_init(self):
        """测试提示词管理器初始化"""
        from src.ai.prompts import PromptManager
        pm = PromptManager()
        self.assertIsNotNone(pm)

    def test_get_system_prompt(self):
        """测试获取系统提示词"""
        from src.ai.prompts import PromptManager
        pm = PromptManager()
        prompt = pm.get_system_prompt("default")
        self.assertIn("WiFi网络安全", prompt)

    def test_list_scenarios(self):
        """测试列出场景"""
        from src.ai.prompts import PromptManager
        pm = PromptManager()
        scenarios = pm.list_scenarios()
        self.assertIn("default", scenarios)
        self.assertIn("teaching", scenarios)
        self.assertIn("ctf", scenarios)


class TestProjectStructure(unittest.TestCase):
    """测试项目结构"""

    def test_directory_structure(self):
        """测试目录结构"""
        root = Path(__file__).parent.parent

        # 检查关键目录
        self.assertTrue((root / "src").exists(), "src目录不存在")
        self.assertTrue((root / "src" / "core").exists(), "core目录不存在")
        self.assertTrue((root / "src" / "modules").exists(), "modules目录不存在")
        self.assertTrue((root / "src" / "ai").exists(), "ai目录不存在")
        self.assertTrue((root / "src" / "gui").exists(), "gui目录不存在")
        self.assertTrue((root / "src" / "web").exists(), "web目录不存在")

    def test_requirements_exists(self):
        """测试requirements.txt存在"""
        root = Path(__file__).parent.parent
        self.assertTrue((root / "requirements.txt").exists(), "requirements.txt不存在")


def run_tests():
    """运行所有测试"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    print("=" * 50)
    print("WiFi可视化安全学习工具 v2 - 测试")
    print("=" * 50)
    print()
    run_tests()

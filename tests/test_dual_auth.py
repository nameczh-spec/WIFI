"""
双密码验证系统测试
"""

import unittest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDualAuth(unittest.TestCase):
    """双密码验证测试"""

    def test_safety_dual_password_default(self):
        """测试默认双密码未设置状态"""
        from src.core.safety import SafetyManager
        safety = SafetyManager()
        self.assertFalse(safety.is_dual_password_set())
        self.assertFalse(safety.is_verified())

    def test_safety_set_and_verify_password(self):
        """测试设置和验证双密码"""
        from src.core.safety import SafetyManager
        from src.core.config import ConfigManager
        import tempfile
        import os

        # 使用临时配置
        safety = SafetyManager()
        config = ConfigManager()

        # 设置密码
        safety.set_dual_password("test123", "test456")

        # 检查是否设置
        self.assertTrue(safety.is_dual_password_set())

        # 验证正确密码
        result = safety.verify_dual_password("test123", "test456")
        self.assertTrue(result)
        self.assertTrue(safety.is_verified())

        # 验证错误密码
        safety.clear_dual_password_verification()
        result = safety.verify_dual_password("wrong1", "test456")
        self.assertFalse(result)
        self.assertFalse(safety.is_verified())

        # 清除
        safety.clear_dual_password_verification()
        self.assertFalse(safety.is_verified())

    def test_authorization(self):
        """测试授权功能"""
        from src.core.safety import SafetyManager
        safety = SafetyManager()

        self.assertFalse(safety.is_network_authorized())

        safety.authorize_network()
        self.assertTrue(safety.is_network_authorized())

        safety.clear_authorization()
        self.assertFalse(safety.is_network_authorized())
        self.assertFalse(safety.is_verified())

    def test_get_status(self):
        """测试获取状态"""
        from src.core.safety import SafetyManager
        safety = SafetyManager()

        status = safety.get_status()
        self.assertIn("gentle_mode", status)
        self.assertIn("dual_password_verified", status)
        self.assertIn("network_authorized", status)

    def test_password_strength_check(self):
        """测试密码强度检测"""
        try:
            from src.gui.dual_auth import PasswordStrengthBar
        except ImportError:
            self.skipTest("PyQt5 not installed")

        bar = PasswordStrengthBar()

        # 弱密码
        score = bar.check_password_strength("123456")
        self.assertLess(score, 30)

        # 中等等密码
        score = bar.check_password_strength("abc123def")
        self.assertGreater(score, 30)

        # 强密码
        score = bar.check_password_strength("MyStr0ng!Pass")
        self.assertGreater(score, 60)

    def test_operation_requires_auth(self):
        """测试需要认证的操作"""
        from src.core.safety import SafetyManager, OperationLevel

        safety = SafetyManager(gentle_mode=False)

        # 注册需要认证的操作
        safety.register_operation("advanced", OperationLevel.DANGEROUS, "高级操作", True)

        # 未认证时不允许
        self.assertFalse(safety.check_operation("advanced"))

        # 认证后允许（但仍受温和模式限制）
        safety._dual_password_verified = True
        safety.authorize_network()
        # 温和模式下危险操作不允许
        safety.gentle_mode = True
        self.assertFalse(safety.check_operation("advanced"))

        # 关闭温和模式后允许
        safety.gentle_mode = False
        self.assertTrue(safety.check_operation("advanced"))


if __name__ == '__main__':
    unittest.main(verbosity=2)

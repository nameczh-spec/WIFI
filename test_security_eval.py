"""
安全评估模块测试
测试密码强度评估、加密评级、综合网络评估等功能
"""
import sys
import unittest

sys.path.insert(0, '.')


class TestSecurityEval(unittest.TestCase):
    """安全评估模块测试"""

    def setUp(self):
        from src.modules.security_eval import NetworkSecurityEvaluator
        self.evaluator = NetworkSecurityEvaluator()

    def test_password_strength_weak(self):
        """测试弱密码评估"""
        result = self.evaluator.evaluate_password("123456")
        self.assertLessEqual(result.total_score, 30)
        self.assertEqual(result.level, "弱")

    def test_password_strength_strong(self):
        """测试强密码评估"""
        result = self.evaluator.evaluate_password("Tr0ub4dor&3")
        self.assertGreaterEqual(result.total_score, 60)
        self.assertIn(result.level, ["强", "很强"])

    def test_password_strength_empty(self):
        """测试空密码评估"""
        result = self.evaluator.evaluate_password("")
        self.assertLessEqual(result.total_score, 50)
        self.assertGreater(len(result.suggestions), 0)

    def test_encryption_rating_wep(self):
        """测试WEP加密评级"""
        result = self.evaluator.rate_encryption("WEP")
        self.assertEqual(result.encryption_type, "WEP")
        self.assertEqual(result.score, 0)
        self.assertEqual(result.level, "危险")

    def test_encryption_rating_wpa2(self):
        """测试WPA2加密评级"""
        result = self.evaluator.rate_encryption("WPA2-CCMP")
        self.assertEqual(result.encryption_type, "WPA2-AES")
        self.assertEqual(result.score, 70)

    def test_encryption_rating_open(self):
        """测试开放网络评级"""
        result = self.evaluator.rate_encryption("Open")
        self.assertEqual(result.score, 0)
        self.assertEqual(result.level, "危险")

    def test_evaluate_network_weak(self):
        """测试弱网络综合评估"""
        result = self.evaluator.evaluate_network("TestNet", "123456", "WEP")
        self.assertLess(result.overall_score, 40)
        self.assertEqual(result.overall_level, "危险")
        self.assertGreater(len(result.risks), 0)

    def test_evaluate_network_strong(self):
        """测试强网络综合评估"""
        result = self.evaluator.evaluate_network("TestNet", "Tr0ub4dor&3xyz", "WPA2-CCMP")
        self.assertGreaterEqual(result.overall_score, 60)
        self.assertIn(result.overall_level, ["中", "强"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

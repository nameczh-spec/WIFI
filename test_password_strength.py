"""
密码强度测试练习模块测试
"""
import sys
import unittest
sys.path.insert(0, '.')


class TestPasswordStrengthTester(unittest.TestCase):
    """密码强度测试器测试"""

    def setUp(self):
        from src.modules.password_strength import PasswordStrengthTester
        self.tester = PasswordStrengthTester()

    def test_basic_strength_evaluation(self):
        """测试基本密码强度评估"""
        # 弱密码
        weak = self.tester.evaluate("123456")
        self.assertIn("score", weak)
        self.assertLessEqual(weak["score"], 30)
        self.assertEqual(weak["level"], "极弱")
        
        # 中等密码
        medium = self.tester.evaluate("MyDog1234")
        self.assertGreater(medium["score"], 40)
        self.assertLess(medium["score"], 80)
        
        # 强密码
        strong = self.tester.evaluate("Kx9$mP2#vL7@nQ")
        self.assertGreaterEqual(strong["score"], 80)
        self.assertIn(strong["level"], ["强", "极强"])

    def test_character_types_detection(self):
        """测试字符类型检测"""
        result = self.tester.evaluate("Abc123!", detail_level="detailed")
        self.assertIn("char_types", result)
        self.assertIn("lowercase", result["char_types"])
        self.assertIn("uppercase", result["char_types"])
        self.assertIn("digits", result["char_types"])
        self.assertIn("symbols", result["char_types"])
        self.assertTrue(result["char_types"]["lowercase"])
        self.assertTrue(result["char_types"]["uppercase"])
        self.assertTrue(result["char_types"]["digits"])
        self.assertTrue(result["char_types"]["symbols"])

    def test_weak_password_patterns(self):
        """测试弱密码模式识别"""
        patterns = self.tester.detect_weak_patterns("password")
        pattern_types = [p["type"] for p in patterns]
        self.assertIn("common_password", pattern_types)
        
        patterns2 = self.tester.detect_weak_patterns("12345678")
        pattern_types2 = [p["type"] for p in patterns2]
        self.assertIn("sequential", pattern_types2)
        
        patterns3 = self.tester.detect_weak_patterns("aaaaaaa")
        pattern_types3 = [p["type"] for p in patterns3]
        self.assertIn("repeating", pattern_types3)

    def test_crack_time_estimation(self):
        """测试破解时间估算"""
        # 弱密码：秒级或分钟级
        weak_time = self.tester.estimate_crack_time("123456")
        self.assertIn("time_human", weak_time)
        self.assertIn("time_seconds", weak_time)
        
        # 强密码：年级
        strong_time = self.tester.estimate_crack_time("Kx9$mP2#vL7@nQ4!")
        self.assertIn("time_human", strong_time)
        self.assertGreater(strong_time["time_seconds"], 365 * 24 * 3600)

    def test_password_advice(self):
        """测试密码改进建议"""
        advice = self.tester.get_improvement_advice("abc")
        self.assertIn("advice", advice)
        self.assertGreater(len(advice["advice"]), 2)
        
        for item in advice["advice"]:
            self.assertIn("type", item)
            self.assertIn("description", item)

    def test_dictionary_check(self):
        """测试字典检查"""
        result = self.tester.check_dictionary("password")
        self.assertIn("found", result)
        self.assertTrue(result["found"])
        
        result2 = self.tester.check_dictionary("Xy9#kL2$mP7!")
        self.assertIn("found", result2)
        self.assertFalse(result2["found"])

    def test_strength_curve(self):
        """测试密码强度曲线数据"""
        curve = self.tester.get_strength_curve()
        self.assertIn("lengths", curve)
        self.assertIn("strengths", curve)
        self.assertGreater(len(curve["lengths"]), 5)
        self.assertIsInstance(curve["strengths"], dict)
        self.assertGreater(len(curve["strengths"]), 1)

    def test_progressive_info(self):
        """测试渐进式信息展示"""
        result = self.tester.evaluate("test123", detail_level="basic")
        self.assertIn("score", result)
        self.assertIn("level", result)
        self.assertLess(len(str(result)), 500)
        
        result2 = self.tester.evaluate("test123", detail_level="detailed")
        self.assertGreater(len(str(result2)), len(str(result)))
        
        result3 = self.tester.evaluate("test123", detail_level="full")
        self.assertGreater(len(str(result3)), len(str(result2)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
WEP破解练习强化测试
按照TDD原则：先写测试，再实现
"""
import sys
import unittest
sys.path.insert(0, '.')


class TestWEPPracticeEnhanced(unittest.TestCase):
    """WEP破解练习强化功能测试"""

    def setUp(self):
        from src.modules.wep_practice import WEPPracticeSimulator
        self.sim = WEPPracticeSimulator()
        self.sim.start_practice("abc12345", "TestWEP")

    def test_iv_collection_phases(self):
        """测试IV收集分阶段速率模拟"""
        status = self.sim.get_progress()
        self.assertIn("ivs_collected", status)
        
        # 第一阶段：慢速收集
        result = self.sim.capture_ivs_phase("slow", 500)
        self.assertTrue(result["success"])
        self.assertLessEqual(result["ivs_captured"], 500)
        
        # 第二阶段：中速收集
        result = self.sim.capture_ivs_phase("medium", 1000)
        self.assertTrue(result["success"])
        
        # 第三阶段：快速收集
        result = self.sim.capture_ivs_phase("fast", 2000)
        self.assertTrue(result["success"])

    def test_fms_attack_byte_by_byte(self):
        """测试FMS攻击逐字节破解演示"""
        self.sim.capture_ivs(20000)
        
        result = self.sim.get_fms_attack_detail()
        self.assertIn("bytes_detail", result)
        self.assertIsInstance(result["bytes_detail"], list)
        
        # 每个字节都有详细信息
        for byte_info in result["bytes_detail"]:
            self.assertIn("byte_index", byte_info)
            self.assertIn("status", byte_info)
            self.assertIn("votes", byte_info)
            self.assertIn("top_candidate", byte_info)

    def test_weak_iv_visualization_data(self):
        """测试弱IV可视化数据"""
        self.sim.capture_ivs(5000)
        
        viz_data = self.sim.get_weak_iv_visualization()
        self.assertIn("weak_iv_distribution", viz_data)
        self.assertIn("iv_prefix_counts", viz_data)
        self.assertIn("total_weak_ivs", viz_data)
        self.assertGreater(viz_data["total_weak_ivs"], 0)

    def test_crack_success_rate_curve(self):
        """测试破解成功率与IV数量关系曲线"""
        curve = self.sim.get_success_rate_curve()
        self.assertIn("data_points", curve)
        self.assertGreater(len(curve["data_points"]), 5)
        
        # 成功率随IV数量增加而上升
        prev_rate = 0
        for point in curve["data_points"]:
            self.assertIn("iv_count", point)
            self.assertIn("success_rate", point)
            self.assertGreaterEqual(point["success_rate"], prev_rate)
            prev_rate = point["success_rate"]

    def test_key_length_break_time(self):
        """测试不同密钥长度的破解时间对比"""
        comparison = self.sim.get_key_length_comparison()
        self.assertIn("comparisons", comparison)
        self.assertGreaterEqual(len(comparison["comparisons"]), 3)
        
        for item in comparison["comparisons"]:
            self.assertIn("key_length", item)
            self.assertIn("estimated_time", item)
            self.assertIn("iv_required", item)

    def test_educational_explanations(self):
        """测试教学讲解内容"""
        # 每个阶段都有讲解
        explanations = self.sim.get_step_explanations()
        self.assertIn("iv_collection", explanations)
        self.assertIn("weak_iv_detection", explanations)
        self.assertIn("fms_attack", explanations)
        self.assertIn("key_verification", explanations)
        
        # 讲解内容不为空
        for key, content in explanations.items():
            self.assertIn("principle", content)
            self.assertIn("defense", content)
            self.assertTrue(len(content["principle"]) > 50)
            self.assertTrue(len(content["defense"]) > 50)

    def test_progressive_info_mode(self):
        """测试渐进式信息展示模式"""
        # 基本信息模式
        basic = self.sim.get_progress(detail_level="basic")
        self.assertLess(len(str(basic)), 500)  # 信息较少
        
        # 详细信息模式
        detailed = self.sim.get_progress(detail_level="detailed")
        self.assertGreater(len(str(detailed)), len(str(basic)))
        
        # 完整信息模式
        full = self.sim.get_progress(detail_level="full")
        self.assertGreater(len(str(full)), len(str(detailed)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
PMK/PTK密钥推导演示强化测试
"""
import sys
import unittest
sys.path.insert(0, '.')


class TestKeyDerivationEnhanced(unittest.TestCase):
    """密钥推导演示强化测试"""

    def setUp(self):
        from src.modules.handshake_sim import WPAHandshakeSimulator
        self.sim = WPAHandshakeSimulator()

    def test_pbkdf2_step_by_step(self):
        """测试PBKDF2逐步骤计算演示"""
        result = self.sim.get_pbkdf2_detail("testpassword", "TestSSID")
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("steps", result)
        self.assertGreater(len(result["steps"]), 3)
        
        for step in result["steps"]:
            self.assertIn("step_num", step)
            self.assertIn("title", step)
            self.assertIn("description", step)
            self.assertIn("input_preview", step)
            self.assertIn("output_preview", step)

    def test_prf_detail(self):
        """测试PRF-X函数详细演示"""
        pmk = "00" * 32
        ap_mac = "aa:bb:cc:dd:ee:ff"
        client_mac = "11:22:33:44:55:66"
        anonce = "aa" * 32
        snonce = "bb" * 32
        
        result = self.sim.get_prf_detail(pmk, ap_mac, client_mac, anonce, snonce)
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("ptk", result)
        self.assertIn("steps", result)
        self.assertGreater(len(result["steps"]), 2)

    def test_ptk_decomposition(self):
        """测试PTK分解为各子密钥"""
        pmk = "00" * 32
        ap_mac = "aa:bb:cc:dd:ee:ff"
        client_mac = "11:22:33:44:55:66"
        anonce = "aa" * 32
        snonce = "bb" * 32
        
        result = self.sim.get_prf_detail(pmk, ap_mac, client_mac, anonce, snonce)
        ptk = result["ptk"]
        
        decomposed = self.sim.decompose_ptk(ptk)
        self.assertIn("kck", decomposed)
        self.assertIn("kek", decomposed)
        self.assertIn("tk", decomposed)
        self.assertIn("mic_tx", decomposed)
        self.assertIn("mic_rx", decomposed)

    def test_derivation_chain_visualization(self):
        """测试密钥推导链可视化数据"""
        viz = self.sim.get_derivation_chain()
        self.assertIn("nodes", viz)
        self.assertIn("edges", viz)
        self.assertGreater(len(viz["nodes"]), 5)
        self.assertGreater(len(viz["edges"]), 4)
        
        for node in viz["nodes"]:
            self.assertIn("id", node)
            self.assertIn("label", node)
            self.assertIn("level", node)

    def test_iteration_animation_data(self):
        """测试PBKDF2迭代动画数据"""
        anim = self.sim.get_pbkdf2_animation_data("test", "Test", 10)
        self.assertIn("iterations", anim)
        self.assertGreater(len(anim["iterations"]), 5)
        
        first_iter = anim["iterations"][0]
        self.assertIn("iteration", first_iter)
        self.assertIn("input_hash", first_iter)
        self.assertIn("output_hash", first_iter)

    def test_key_security_explanation(self):
        """测试密钥安全原理解释"""
        explanations = self.sim.get_key_security_explanations()
        self.assertIn("pmk_security", explanations)
        self.assertIn("ptk_security", explanations)
        self.assertIn("forward_secrecy", explanations)
        
        for key, content in explanations.items():
            self.assertIn("title", content)
            self.assertIn("principle", content)
            self.assertIn("why_secure", content)

    def test_progressive_derivation_info(self):
        """测试渐进式密钥推导信息"""
        pmk = "00" * 32
        ap_mac = "aa:bb:cc:dd:ee:ff"
        client_mac = "11:22:33:44:55:66"
        anonce = "aa" * 32
        snonce = "bb" * 32
        
        basic = self.sim.get_derivation_info_basic(pmk, ap_mac, client_mac, anonce, snonce)
        self.assertIn("pmk_preview", basic)
        self.assertLess(len(str(basic)), 1000)
        
        detailed = self.sim.get_derivation_info_basic(pmk, ap_mac, client_mac, anonce, snonce, "detailed")
        self.assertGreater(len(str(detailed)), len(str(basic)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

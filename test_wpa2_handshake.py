"""
WPA2握手包分析练习模块测试
纯离线分析，不涉及任何真实捕获
"""
import sys
import unittest
sys.path.insert(0, '.')


class TestWPA2HandshakeAnalyzer(unittest.TestCase):
    """WPA2握手包分析器测试"""

    def setUp(self):
        from src.modules.wpa2_handshake_analyzer import WPA2HandshakeAnalyzer
        self.analyzer = WPA2HandshakeAnalyzer()

    def test_create_sample_handshake(self):
        """测试生成示例握手包数据"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        self.assertIn("success", handshake)
        self.assertTrue(handshake["success"])
        self.assertIn("ssid", handshake)
        self.assertIn("bssid", handshake)
        self.assertIn("client_mac", handshake)
        self.assertIn("eapol_frames", handshake)
        self.assertEqual(len(handshake["eapol_frames"]), 4)

    def test_eapol_frame_structure(self):
        """测试EAPOL帧结构解析"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        frames = handshake["eapol_frames"]
        
        # 检查四个握手包
        msg1 = frames[0]
        self.assertEqual(msg1["message_number"], 1)
        self.assertIn("anonce", msg1)
        self.assertIn("ap_mac", msg1)
        
        msg2 = frames[1]
        self.assertEqual(msg2["message_number"], 2)
        self.assertIn("snonce", msg2)
        self.assertIn("client_mac", msg2)
        self.assertIn("mic", msg2)
        
        msg3 = frames[2]
        self.assertEqual(msg3["message_number"], 3)
        self.assertIn("anonce", msg3)
        self.assertIn("mic", msg3)
        
        msg4 = frames[3]
        self.assertEqual(msg4["message_number"], 4)
        self.assertIn("mic", msg4)

    def test_handshake_sequence_diagram(self):
        """测试握手时序图数据"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        diagram = self.analyzer.get_sequence_diagram(handshake)
        
        self.assertIn("success", diagram)
        self.assertTrue(diagram["success"])
        self.assertIn("messages", diagram)
        self.assertGreaterEqual(len(diagram["messages"]), 4)
        
        for msg in diagram["messages"]:
            self.assertIn("from", msg)
            self.assertIn("to", msg)
            self.assertIn("description", msg)
            self.assertIn("key_fields", msg)

    def test_key_extraction(self):
        """测试从握手包中提取密钥参数"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        key_params = self.analyzer.extract_key_params(handshake)
        
        self.assertIn("success", key_params)
        self.assertTrue(key_params["success"])
        self.assertIn("ssid", key_params)
        self.assertIn("ap_mac", key_params)
        self.assertIn("client_mac", key_params)
        self.assertIn("anonce", key_params)
        self.assertIn("snonce", key_params)
        self.assertIn("mic", key_params)
        self.assertIn("data", key_params)

    def test_verify_handshake_integrity(self):
        """测试握手包完整性验证"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        result = self.analyzer.verify_handshake_integrity(handshake)
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("is_valid", result)
        self.assertTrue(result["is_valid"])
        self.assertIn("checks", result)
        self.assertGreater(len(result["checks"]), 3)

    def test_mic_verification_demo(self):
        """测试MIC验证演示（纯教学，不真实破解）"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        result = self.analyzer.mic_verification_demo(handshake, "wrongpassword")
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("is_valid", result)
        self.assertFalse(result["is_valid"])
        self.assertIn("computed_mic", result)
        self.assertIn("expected_mic", result)

    def test_handshake_explanations(self):
        """测试握手包教学讲解"""
        explanations = self.analyzer.get_handshake_explanations()
        
        self.assertIn("message1", explanations)
        self.assertIn("message2", explanations)
        self.assertIn("message3", explanations)
        self.assertIn("message4", explanations)
        
        for key, content in explanations.items():
            self.assertIn("title", content)
            self.assertIn("principle", content)
            self.assertIn("security", content)

    def test_progressive_detail(self):
        """测试渐进式信息展示"""
        handshake = self.analyzer.create_sample_handshake("TestWiFi", "password123")
        
        basic = self.analyzer.get_handshake_info(handshake, detail_level="basic")
        self.assertLess(len(str(basic)), 1000)
        
        detailed = self.analyzer.get_handshake_info(handshake, detail_level="detailed")
        self.assertGreater(len(str(detailed)), len(str(basic)))
        
        full = self.analyzer.get_handshake_info(handshake, detail_level="full")
        self.assertGreater(len(str(full)), len(str(detailed)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

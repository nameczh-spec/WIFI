"""
WPA2握手包分析练习模块
纯离线分析，仅供学习研究使用
不进行任何密码破解计算，仅展示握手包结构和原理
"""

import hashlib
import hmac
import random
import struct
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class WPA2HandshakeAnalyzer:
    """
    WPA2四次握手分析器
    纯教学演示：解析握手包结构、展示密钥推导过程
    不进行任何密码破解
    """

    def __init__(self):
        self.current_handshake = None

    def create_sample_handshake(self, ssid: str, password: str) -> Dict:
        """生成示例握手包数据（用于教学演示）"""
        ap_mac = self._generate_mac("AP")
        client_mac = self._generate_mac("Client")
        anonce = self._generate_random_hex(32)
        snonce = self._generate_random_hex(32)

        pmk = hashlib.pbkdf2_hmac('sha1', password.encode(), ssid.encode(), 4096, 32)

        eapol_frames = []

        frame1 = {
            "message_number": 1,
            "from": "AP",
            "to": "Client",
            "timestamp": 0.0,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "key_info": "0x008a",
            "key_length": 16,
            "replay_counter": 1,
            "wpa_key_length": 0,
            "mic": "",
            "description": "消息1：AP发送ANonce，开始握手"
        }
        eapol_frames.append(frame1)

        mic2 = self._compute_mic_demo(pmk, ap_mac, client_mac, anonce, snonce, 2)
        frame2 = {
            "message_number": 2,
            "from": "Client",
            "to": "AP",
            "timestamp": 0.1,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "snonce": snonce,
            "key_info": "0x010a",
            "key_length": 16,
            "replay_counter": 2,
            "wpa_key_length": 224,
            "mic": mic2,
            "description": "消息2：客户端发送SNonce + MIC，证明知道PMK"
        }
        eapol_frames.append(frame2)

        mic3 = self._compute_mic_demo(pmk, ap_mac, client_mac, anonce, snonce, 3)
        frame3 = {
            "message_number": 3,
            "from": "AP",
            "to": "Client",
            "timestamp": 0.2,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "snonce": snonce,
            "key_info": "0x13ca",
            "key_length": 16,
            "replay_counter": 3,
            "wpa_key_length": 224,
            "mic": mic3,
            "install": True,
            "description": "消息3：AP确认 + 安装密钥 + GTK"
        }
        eapol_frames.append(frame3)

        mic4 = self._compute_mic_demo(pmk, ap_mac, client_mac, anonce, snonce, 4)
        frame4 = {
            "message_number": 4,
            "from": "Client",
            "to": "AP",
            "timestamp": 0.3,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "snonce": snonce,
            "key_info": "0x030a",
            "key_length": 16,
            "replay_counter": 4,
            "wpa_key_length": 0,
            "mic": mic4,
            "install_ack": True,
            "description": "消息4：客户端确认安装，握手完成"
        }
        eapol_frames.append(frame4)

        self.current_handshake = {
            "success": True,
            "ssid": ssid,
            "bssid": ap_mac,
            "client_mac": client_mac,
            "encryption": "WPA2-PSK",
            "key_type": "CCMP",
            "eapol_frames": eapol_frames,
            "anonce": anonce,
            "snonce": snonce,
            "handshake_complete": True,
            "captured_at": "模拟数据",
        }

        return self.current_handshake

    def _generate_mac(self, prefix: str = "") -> str:
        """生成随机MAC地址"""
        parts = [f"{random.randint(0x00, 0xff):02x}" for _ in range(6)]
        return ":".join(parts)

    def _generate_random_hex(self, length: int) -> str:
        """生成指定长度的十六进制随机数"""
        return "".join(f"{random.randint(0, 255):02x}" for _ in range(length))

    def _compute_mic_demo(self, pmk: bytes, ap_mac: str, client_mac: str,
                          anonce: str, snonce: str, msg_num: int) -> str:
        """演示MIC计算（教学用，非真实EAPOL MIC计算）"""
        data = f"{ap_mac}{client_mac}{anonce}{snonce}{msg_num}".encode()
        mic = hmac.new(pmk, data, hashlib.sha1).hexdigest()[:32]
        return mic

    def get_sequence_diagram(self, handshake: Dict) -> Dict:
        """获取握手时序图数据"""
        if not handshake or "eapol_frames" not in handshake:
            return {"success": False, "error": "无效的握手数据"}

        messages = []
        frames = handshake["eapol_frames"]

        for i, frame in enumerate(frames):
            key_fields = []
            if "anonce" in frame and frame["anonce"]:
                key_fields.append("ANonce")
            if "snonce" in frame and frame["snonce"]:
                key_fields.append("SNonce")
            if "mic" in frame and frame["mic"]:
                key_fields.append("MIC")
            if frame.get("install"):
                key_fields.append("Install")
            if frame.get("install_ack"):
                key_fields.append("Install Ack")

            messages.append({
                "id": i + 1,
                "from": frame["from"],
                "to": frame["to"],
                "description": frame["description"],
                "key_fields": key_fields,
                "timestamp": frame.get("timestamp", 0),
            })

        return {
            "success": True,
            "messages": messages,
            "participants": ["AP（接入点）", "Client（客户端）"],
            "total_messages": len(messages),
            "handshake_type": "WPA2 4-Way Handshake",
        }

    def extract_key_params(self, handshake: Dict) -> Dict:
        """从握手包中提取密钥推导参数"""
        if not handshake or "eapol_frames" not in handshake:
            return {"success": False, "error": "无效的握手数据"}

        frames = handshake["eapol_frames"]
        ap_mac = handshake["bssid"]
        client_mac = handshake["client_mac"]

        anonce = ""
        snonce = ""
        mic = ""
        data = ""

        for frame in frames:
            if frame["message_number"] == 1:
                anonce = frame.get("anonce", "")
            elif frame["message_number"] == 2:
                snonce = frame.get("snonce", "")
                mic = frame.get("mic", "")

        return {
            "success": True,
            "ssid": handshake["ssid"],
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "snonce": snonce,
            "mic": mic,
            "data": data,
            "key_derivation_steps": [
                "PMK = PBKDF2(密码, SSID, 4096次迭代)",
                "PTK = PRF-X(PMK, 'Pairwise key expansion', Min(AP_MAC,STA_MAC)||Max(AP_MAC,STA_MAC)||Min(ANonce,SNonce)||Max(ANonce,SNonce))",
                "KCK = PTK[0:128]  (密钥确认密钥)",
                "KEK = PTK[128:256]  (密钥加密密钥)",
                "TK = PTK[256:384]  (临时密钥，用于加密数据)",
            ]
        }

    def verify_handshake_integrity(self, handshake: Dict) -> Dict:
        """验证握手包完整性"""
        if not handshake or "eapol_frames" not in handshake:
            return {"success": False, "error": "无效的握手数据"}

        frames = handshake["eapol_frames"]
        checks = []

        check1 = {
            "name": "消息数量检查",
            "passed": len(frames) >= 2,
            "description": f"捕获到 {len(frames)} 个EAPOL帧（至少需要消息1+2）",
            "required": "消息1+2（可选+3+4）",
        }
        checks.append(check1)

        has_anonce = any(f.get("anonce") for f in frames)
        check2 = {
            "name": "ANonce存在性检查",
            "passed": has_anonce,
            "description": "AP的Nonce（随机数）已捕获",
            "required": "必须有ANonce",
        }
        checks.append(check2)

        has_snonce = any(f.get("snonce") for f in frames)
        check3 = {
            "name": "SNonce存在性检查",
            "passed": has_snonce,
            "description": "客户端的Nonce（随机数）已捕获",
            "required": "必须有SNonce",
        }
        checks.append(check3)

        has_mic = any(f.get("mic") for f in frames)
        check4 = {
            "name": "MIC存在性检查",
            "passed": has_mic,
            "description": "消息完整性校验码已捕获",
            "required": "必须有MIC才能验证密码",
        }
        checks.append(check4)

        is_valid = all(c["passed"] for c in checks)

        return {
            "success": True,
            "is_valid": is_valid,
            "checks": checks,
            "total_checks": len(checks),
            "passed_checks": sum(1 for c in checks if c["passed"]),
            "quality": "完整（4个消息）" if len(frames) == 4 else ("部分（2个消息）" if len(frames) == 2 else "不完整"),
        }

    def mic_verification_demo(self, handshake: Dict, test_password: str) -> Dict:
        """MIC验证演示（纯教学，展示验证过程，不破解）"""
        if not handshake:
            return {"success": False, "error": "无效的握手数据"}

        ssid = handshake["ssid"]
        params = self.extract_key_params(handshake)

        pmk = hashlib.pbkdf2_hmac('sha1', test_password.encode(), ssid.encode(), 4096, 32)

        expected_mic = params["mic"]
        computed_mic = self._compute_mic_demo(
            pmk, params["ap_mac"], params["client_mac"],
            params["anonce"], params["snonce"], 2
        )

        is_valid = (computed_mic == expected_mic)

        return {
            "success": True,
            "is_valid": is_valid,
            "test_password_length": len(test_password),
            "computed_mic": computed_mic,
            "expected_mic": expected_mic,
            "pmk_hex": pmk.hex(),
            "ssid": ssid,
            "iterations": 4096,
            "hash_algorithm": "HMAC-SHA1",
            "note": "此为教学演示。真实破解需要尝试大量密码，强密码实际上不可破解。",
        }

    def get_handshake_explanations(self) -> Dict:
        """获取握手包教学讲解"""
        return {
            "message1": {
                "title": "消息1：AP → 客户端（ANonce）",
                "principle": """
                    <h4>消息1的作用</h4>
                    <p>四次握手从AP发送ANonce（Authenticator Nonce，认证端随机数）开始。这是一个32字节的随机数。</p>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li><strong>发送方</strong>：AP（接入点）</li>
                        <li><strong>接收方</strong>：客户端（Station）</li>
                        <li><strong>主要内容</strong>：ANonce（32字节随机数）</li>
                        <li><strong>密钥信息</strong>：0x008a（表示这是第1个握手消息）</li>
                        <li><strong>重放计数器</strong>：递增的序列号，防止重放攻击</li>
                    </ul>
                    
                    <h4>为什么需要Nonce？</h4>
                    <p>Nonce（Number used once）是只使用一次的随机数。它的作用是：</p>
                    <ol>
                        <li>确保每次握手生成的密钥都不同（前向保密性）</li>
                        <li>防止重放攻击（攻击者不能重复使用旧的握手消息）</li>
                        <li>为密钥派生提供随机输入</li>
                    </ol>
                """,
                "security": """
                    <h4>安全性分析</h4>
                    <p>消息1本身不包含任何机密信息，ANonce以明文传输。攻击者可以看到ANonce，但这不会直接泄露密钥。</p>
                    
                    <h4>攻击面</h4>
                    <ul>
                        <li>攻击者可以通过发送伪造的消息1干扰握手过程</li>
                        <li>但这不会导致密钥泄露，只会导致握手失败</li>
                        <li>真正的威胁是在获取完整握手后进行离线字典攻击</li>
                    </ul>
                """,
            },
            "message2": {
                "title": "消息2：客户端 → AP（SNonce + MIC）",
                "principle": """
                    <h4>消息2的作用</h4>
                    <p>客户端收到ANonce后，生成自己的SNonce（Supplicant Nonce，请求端随机数），然后计算MIC并连同SNonce一起发送回AP。</p>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li><strong>发送方</strong>：客户端</li>
                        <li><strong>接收方</strong>：AP</li>
                        <li><strong>主要内容</strong>：SNonce（32字节随机数）+ MIC（16字节消息完整性校验）</li>
                        <li><strong>密钥信息</strong>：0x010a</li>
                    </ul>
                    
                    <h4>MIC是什么？</h4>
                    <p>MIC（Message Integrity Code，消息完整性码）是使用KCK（密钥确认密钥）对整个EAPOL消息计算的HMAC-SHA1值。</p>
                    
                    <h4>为什么这一步很关键？</h4>
                    <p>消息2是攻击者最感兴趣的消息，因为它包含了MIC。有了MIC + ANonce + SNonce + MAC地址，攻击者就可以进行离线密码验证：</p>
                    <ol>
                        <li>猜测一个密码</li>
                        <li>用PBKDF2计算PMK</li>
                        <li>从PMK派生PTK，得到KCK</li>
                        <li>用KCK计算MIC</li>
                        <li>与捕获的MIC比较，如果相同则密码正确</li>
                    </ol>
                """,
                "security": """
                    <h4>安全性分析</h4>
                    <p>消息2包含MIC，这是WPA2离线字典攻击的基础。但请注意：</p>
                    <ul>
                        <li>只有获取完整的握手包（至少消息1+2）才能进行验证</li>
                        <li>密码强度决定了破解难度</li>
                        <li>12位以上的强密码，即使有握手包也实际上无法破解</li>
                    </ul>
                    
                    <h4>防御措施</h4>
                    <ol>
                        <li><strong>使用强密码</strong>：12位以上，混合大小写+数字+符号</li>
                        <li><strong>升级到WPA3</strong>：SAE认证抵御离线字典攻击</li>
                        <li><strong>定期更换密码</strong>：降低被破解的风险窗口</li>
                    </ol>
                """,
            },
            "message3": {
                "title": "消息3：AP → 客户端（确认 + 安装 + GTK）",
                "principle": """
                    <h4>消息3的作用</h4>
                    <p>AP验证消息2的MIC正确后，发送消息3。这条消息确认了AP也知道PMK，并通知客户端可以安装密钥了。</p>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li><strong>发送方</strong>：AP</li>
                        <li><strong>接收方</strong>：客户端</li>
                        <li><strong>主要内容</strong>：ANonce + MIC + GTK（组临时密钥）</li>
                        <li><strong>密钥信息</strong>：0x13ca（Install位为1）</li>
                        <li><strong>Install标志</strong>：表示可以安装PTK了</li>
                    </ul>
                    
                    <h4>GTK是什么？</h4>
                    <p>GTK（Group Temporal Key，组临时密钥）用于加密广播/组播流量。所有连接到同一AP的客户端共享同一个GTK。</p>
                    
                    <h4>为什么需要Install标志？</h4>
                    <p>Install标志告诉客户端："AP这边已经准备好使用新密钥了，你那边也可以切换了。" 这确保了双方同时切换密钥，不会出现一方用新密钥、一方用旧密钥的情况。</p>
                """,
                "security": """
                    <h4>安全性分析</h4>
                    <p>消息3中的GTK使用KEK（密钥加密密钥）加密后传输。只有拥有正确PTK的客户端才能解密得到GTK。</p>
                    
                    <h4>为什么消息3不用于破解？</h4>
                    <p>消息3也包含MIC，但它和消息2的MIC是用同一个KCK计算的。所以只要有消息2的MIC就足够进行密码验证了，消息3不是必须的。</p>
                    
                    <p>不过，消息3可以用于确认握手的完整性，并且提供了GTK信息。</p>
                """,
            },
            "message4": {
                "title": "消息4：客户端 → AP（确认安装）",
                "principle": """
                    <h4>消息4的作用</h4>
                    <p>消息4是握手的最后一步。客户端发送确认，表示它已经安装了密钥，可以开始加密通信了。</p>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li><strong>发送方</strong>：客户端</li>
                        <li><strong>接收方</strong>：AP</li>
                        <li><strong>主要内容</strong>：MIC（没有密钥数据）</li>
                        <li><strong>密钥信息</strong>：0x030a</li>
                        <li><strong>意义</strong>："我已经安装好密钥了，我们可以开始加密通信了"</li>
                    </ul>
                    
                    <h4>握手完成后</h4>
                    <p>四次握手完成后：</p>
                    <ol>
                        <li>双方都拥有了PTK（成对临时密钥）</li>
                        <li>数据流量使用TK（临时密钥）进行加密</li>
                        <li>单播数据使用CCMP（AES-CCM）加密</li>
                        <li>广播/组播数据使用GTK加密</li>
                    </ol>
                    
                    <h4>前向保密性</h4>
                    <p>因为每次握手都使用新的Nonce，所以每次连接的PTK都不同。即使某个会话的密钥泄露了，也不会影响之前或之后的会话安全。这就是前向保密性（Forward Secrecy）。</p>
                """,
                "security": """
                    <h4>安全性总结</h4>
                    <p>WPA2四次握手的设计是经过严格密码学分析的。它的安全性基于：</p>
                    <ul>
                        <li>PBKDF2的高迭代次数（4096次）</li>
                        <li>HMAC-SHA1的密码学强度</li>
                        <li>AES-CCMP的强壮加密</li>
                        <li>Nonce保证的前向保密性</li>
                    </ul>
                    
                    <h4>唯一的弱点</h4>
                    <p>WPA2-PSK的唯一弱点是：如果用户使用了弱密码，攻击者可以通过捕获握手包进行离线字典攻击。但这不是协议的问题，而是密码强度的问题。</p>
                    
                    <p><strong>使用12位以上的强密码，WPA2实际上是不可破解的。</strong></p>
                """,
            },
        }

    def get_handshake_info(self, handshake: Dict, detail_level: str = "basic") -> Dict:
        """获取握手包信息（支持渐进式展示）"""
        if not handshake:
            return {"success": False, "error": "无效的握手数据"}

        basic = {
            "success": True,
            "ssid": handshake.get("ssid", ""),
            "bssid": handshake.get("bssid", ""),
            "client_mac": handshake.get("client_mac", ""),
            "encryption": handshake.get("encryption", ""),
            "frames_count": len(handshake.get("eapol_frames", [])),
            "complete": handshake.get("handshake_complete", False),
        }

        if detail_level == "basic":
            return basic

        frames = handshake.get("eapol_frames", [])
        detailed = {
            **basic,
            "anonce": frames[0].get("anonce", "") if len(frames) > 0 else "",
            "snonce": frames[1].get("snonce", "") if len(frames) > 1 else "",
            "has_mic": any(f.get("mic") for f in frames),
            "key_type": handshake.get("key_type", ""),
        }

        if detail_level == "detailed":
            return detailed

        full = {
            **detailed,
            "eapol_frames": frames,
            "integrity_check": self.verify_handshake_integrity(handshake),
            "key_params": self.extract_key_params(handshake),
            "sequence_diagram": self.get_sequence_diagram(handshake),
        }

        return full


_wpa2_handshake_analyzer = None


def get_wpa2_handshake_analyzer() -> WPA2HandshakeAnalyzer:
    """获取WPA2握手分析器单例"""
    global _wpa2_handshake_analyzer
    if _wpa2_handshake_analyzer is None:
        _wpa2_handshake_analyzer = WPA2HandshakeAnalyzer()
    return _wpa2_handshake_analyzer

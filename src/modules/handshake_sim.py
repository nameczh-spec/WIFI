"""
握手过程模拟教学模块
详细模拟WPA四次握手过程，用于教学
完全模拟真实流程但不涉及任何实际攻击
"""

import time
import hashlib
import hmac
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class KeyDerivationStep:
    """密钥派生步骤"""
    step_name: str
    description: str
    input_data: str
    output_data: str
    algorithm: str


@dataclass
class HandshakePacket:
    """握手数据包"""
    packet_number: int
    from_ap: bool  # True=AP发出, False=客户端发出
    eapol_key_info: str
    key_information: Dict[str, bool]
    key_length: int
    replay_counter: int
    nonce: str  # hex
    iv: str
    rsc: str  # 接收序列号计数器
    mic: str  # 消息完整性校验
    key_data_length: int
    key_data: str

    def __str__(self):
        direction = "AP -> Client" if self.from_ap else "Client -> AP"
        return f"Msg{self.packet_number} ({direction})"


@dataclass
class HandshakeLesson:
    """握手教学课程"""
    lesson_id: str
    title: str
    description: str
    content: str
    key_points: List[str]
    warning: str = "仅供学习研究，禁止用于未授权网络"


class WPAHandshakeSimulator:
    """
    WPA四次握手模拟器
    用于教学目的，详细展示握手过程中的每一步
    """

    def __init__(self):
        self.step = 0
        self.completed = False
        self.packets: List[HandshakePacket] = []
        self.derivation_steps: List[KeyDerivationStep] = []

        # 模拟参数（教学用）
        self._ssid = "TestNetwork"
        self._password = "password123"
        self._anonce = ""
        self._snonce = ""
        self._ap_mac = "aa:bb:cc:dd:ee:ff"
        self._client_mac = "11:22:33:44:55:66"
        self._pmk = ""
        self._ptk = ""
        self._gtk = ""

        self._init_lessons()

    def _init_lessons(self):
        """初始化教学课程"""
        self.lessons = [
            HandshakeLesson(
                lesson_id="handshake-intro",
                title="WPA四次握手简介",
                description="了解WPA/WPA2的四次握手过程",
                content="""
                    <h3>什么是四次握手？</h3>
                    <p>四次握手（4-Way Handshake）是WPA/WPA2中客户端连接到加密AP时的密钥协商过程。</p>
                    
                    <h4>握手的目的：</h4>
                    <ol>
                        <li>验证双方都知道预共享密钥（密码）</li>
                        <li>安全地生成PTK（成对临时密钥）</li>
                        <li>分发GTK（组临时密钥）</li>
                        <li>确认密钥安装成功</li>
                    </ol>
                    
                    <h4>为什么需要四次？</h4>
                    <p>因为WiFi是无线媒介，双方都需要确认对方确实拥有正确的密钥，并且都需要生成和确认会话密钥。</p>
                """,
                key_points=[
                    "四次握手用于验证密码和生成会话密钥",
                    "AP和客户端都需要确认对方身份",
                    "过程中不会传输密码本身",
                    "握手包可以用来离线破解密码（仅在密码弱时）",
                ]
            ),
            HandshakeLesson(
                lesson_id="handshake-msg1",
                title="消息1：AP发送ANonce",
                description="AP生成随机数并发送给客户端",
                content="""
                    <h3>消息1 (EAPOL-Key Message 1)</h3>
                    <p><strong>方向：AP → 客户端</strong></p>
                    
                    <h4>发送内容：</h4>
                    <ul>
                        <li><strong>ANonce</strong>：AP生成的随机数（32字节）</li>
                        <li><strong>Key Information</strong>：密钥信息字段</li>
                        <li><strong>RSC</strong>：接收序列号计数器</li>
                        <li><strong>Replay Counter</strong>：重放计数器</li>
                    </ul>
                    
                    <h4>作用：</h4>
                    <p>AP向客户端发起握手，提供自己的随机数。此时客户端可以开始计算PTK。</p>
                    
                    <h4>安全性说明：</h4>
                    <p>这个消息不包含敏感信息，ANonce本身是公开的。密钥的安全性依赖于PSK（密码）的强度。</p>
                """,
                key_points=[
                    "ANonce是AP生成的随机数",
                    "消息1不加密，不包含敏感信息",
                    "收到ANonce后客户端就可以开始计算PTK",
                ]
            ),
            HandshakeLesson(
                lesson_id="handshake-msg2",
                title="消息2：客户端发送SNonce + MIC",
                description="客户端生成SNonce，计算PTK并响应",
                content="""
                    <h3>消息2 (EAPOL-Key Message 2)</h3>
                    <p><strong>方向：客户端 → AP</strong></p>
                    
                    <h4>发送内容：</h4>
                    <ul>
                        <li><strong>SNonce</strong>：客户端生成的随机数（32字节）</li>
                        <li><strong>RSN IE</strong>：RSN信息元素</li>
                        <li><strong>Key Information</strong>：密钥信息</li>
                        <li><strong>MIC</strong>：消息完整性校验码</li>
                    </ul>
                    
                    <h4>客户端此时做了什么？</h4>
                    <ol>
                        <li>生成自己的随机数SNonce</li>
                        <li>用PMK + ANonce + SNonce + MAC地址计算PTK</li>
                        <li>用PTK计算消息的MIC</li>
                        <li>把SNonce + MIC发给AP</li>
                    </ol>
                    
                    <h4>为什么重要？</h4>
                    <p>MIC证明客户端确实有正确的PMK（密码）。AP验证MIC就能确认客户端身份。</p>
                """,
                key_points=[
                    "客户端用PMK+随机数+MAC计算PTK",
                    "MIC证明客户端知道正确密码",
                    "这是验证密码的关键一步",
                ]
            ),
            HandshakeLesson(
                lesson_id="handshake-msg3",
                title="消息3：AP发送GTK + MIC",
                description="AP验证后发送组临时密钥",
                content="""
                    <h3>消息3 (EAPOL-Key Message 3)</h3>
                    <p><strong>方向：AP → 客户端</strong></p>
                    
                    <h4>发送内容：</h4>
                    <ul>
                        <li><strong>GTK</strong>：组临时密钥（加密的）</li>
                        <li><strong>Key Information</strong>：包含Install标志</li>
                        <li><strong>Sequence Number</strong>：序列号</li>
                        <li><strong>MIC</strong>：消息完整性校验</li>
                    </ul>
                    
                    <h4>AP此时做了什么？</h4>
                    <ol>
                        <li>验证消息2的MIC（确认客户端有正确密码）</li>
                        <li>自己也计算出PTK</li>
                        <li>用PTK加密GTK</li>
                        <li>发送消息3，告诉客户端可以安装密钥了</li>
                    </ol>
                    
                    <h4>GTK是什么？</h4>
                    <p>GTK（Group Temporal Key）是用于加密广播/组播数据包的密钥。所有连接的客户端共享同一个GTK。</p>
                """,
                key_points=[
                    "AP验证客户端后发送GTK",
                    "GTK用于广播/组播加密",
                    "Install标志告诉客户端可以安装密钥了",
                ]
            ),
            HandshakeLesson(
                lesson_id="handshake-msg4",
                title="消息4：客户端确认",
                description="客户端确认并完成握手",
                content="""
                    <h3>消息4 (EAPOL-Key Message 4)</h3>
                    <p><strong>方向：客户端 → AP</strong></p>
                    
                    <h4>发送内容：</h4>
                    <ul>
                        <li><strong>Key Information</strong>：确认信息</li>
                        <li><strong>MIC</strong>：消息完整性校验</li>
                    </ul>
                    
                    <h4>客户端此时做了什么？</h4>
                    <ol>
                        <li>验证消息3的MIC</li>
                        <li>解密得到GTK</li>
                        <li>安装PTK和GTK</li>
                        <li>发送确认消息4</li>
                    </ol>
                    
                    <h4>握手完成！</h4>
                    <p>四次握手完成后：</p>
                    <ul>
                        <li>✅ 双方确认对方拥有正确的密码</li>
                        <li>✅ 双方都生成了相同的PTK</li>
                        <li>✅ 客户端获得了GTK</li>
                        <li>✅ 可以开始加密通信了</li>
                    </ul>
                """,
                key_points=[
                    "消息4是客户端的确认",
                    "握手完成后开始加密数据传输",
                    "四个消息缺一不可，各有作用",
                ]
            ),
            HandshakeLesson(
                lesson_id="key-derivation",
                title="密钥派生过程",
                description="PMK、PTK、GTK是如何计算的",
                content="""
                    <h3>WPA密钥层次结构</h3>
                    
                    <h4>第一层：PMK (Pairwise Master Key)</h4>
                    <p>主密钥，由密码和SSID派生。</p>
                    <p>PMK = PBKDF2(密码, SSID, 4096次迭代, 256位)</p>
                    
                    <h4>第二层：PTK (Pairwise Temporal Key)</h4>
                    <p>成对临时密钥，用于单播数据包加密。</p>
                    <p>PTK = PRF(PMK, "Pairwise key expansion", Min(AP_MAC, Client_MAC) || Max(AP_MAC, Client_MAC) || Min(ANonce, SNonce) || Max(ANonce, SNonce))</p>
                    
                    <p>PTK分成三部分：</p>
                    <ul>
                        <li><strong>KCK</strong>：密钥确认密钥（计算MIC）</li>
                        <li><strong>KEK</strong>：密钥加密密钥（加密GTK）</li>
                        <li><strong>TK</strong>：临时密钥（实际数据加密）</li>
                    </ul>
                    
                    <h4>第三层：GTK (Group Temporal Key)</h4>
                    <p>组临时密钥，用于广播/组播数据包加密。</p>
                    <p>由AP生成，通过消息3加密发送给客户端。</p>
                    
                    <h4>为什么要这么多层？</h4>
                    <ul>
                        <li>PMK长期不变，减少使用次数更安全</li>
                        <li>PTK每次连接不同，前向保密</li>
                        <li>GTK独立管理，方便更换组密钥</li>
                    </ul>
                """,
                key_points=[
                    "密码 → PMK → PTK → TK 三层派生",
                    "PBKDF2用于从密码生成PMK（4096次迭代）",
                    "PTK分成KCK+KEK+TK三部分",
                    "每次握手生成不同的随机数 → 不同的PTK",
                ]
            ),
        ]

    def generate_random_nonce(self) -> str:
        """生成随机nonce（hex格式）"""
        import os
        return os.urandom(32).hex()

    def compute_pmk(self, password: str, ssid: str) -> str:
        """计算PMK（简化演示）"""
        # 实际WPA2使用PBKDF2-HMAC-SHA1 4096次迭代
        pmk = hashlib.pbkdf2_hmac('sha1', password.encode(), ssid.encode(), 4096, 32)
        return pmk.hex()

    def compute_ptk(self, pmk_hex: str, anonce: str, snonce: str,
                    ap_mac: str, client_mac: str) -> str:
        """计算PTK（简化演示版本，仅用于教学）"""
        pmk = bytes.fromhex(pmk_hex)

        def mac_to_bytes(mac_str: str) -> bytes:
            return bytes.fromhex(mac_str.replace(':', ''))

        ap_b = mac_to_bytes(ap_mac)
        cli_b = mac_to_bytes(client_mac)
        a_n = bytes.fromhex(anonce)
        s_n = bytes.fromhex(snonce)

        # 排序
        mac_min = min(ap_b, cli_b)
        mac_max = max(ap_b, cli_b)
        nonce_min = min(a_n, s_n)
        nonce_max = max(a_n, s_n)

        # PTK = PRF(PMK, "Pairwise key expansion",
        #           Min(AA,SPA) || Max(AA,SPA) ||
        #           Min(ANonce,SNonce) || Max(ANonce,SNonce))
        data = b"Pairwise key expansion" + b"\x00" + mac_min + mac_max + nonce_min + nonce_max

        # 简化版PRF（实际是SHA1-based）
        # 真实实现更复杂，这里简化演示
        ptk = hmac.new(pmk, data, hashlib.sha1).digest()
        # 扩展到48字节（KCK+KEK+TK = 16+16+16）
        full_ptk = b""
        for i in range(3):
            full_ptk += hmac.new(pmk, data + bytes([i]), hashlib.sha1).digest()

        return full_ptk[:48].hex()

    def start_simulation(self, ssid: str = "TestNetwork",
                         password: str = "password123",
                         ap_mac: str = "aa:bb:cc:dd:ee:ff",
                         client_mac: str = "11:22:33:44:55:66"):
        """开始新的模拟"""
        self.step = 0
        self.completed = False
        self.packets = []
        self.derivation_steps = []
        self._ssid = ssid
        self._password = password
        self._ap_mac = ap_mac
        self._client_mac = client_mac
        self._anonce = ""
        self._snonce = ""
        self._pmk = ""
        self._ptk = ""
        self._gtk = ""

    def get_step_info(self, step_num: int) -> Dict:
        """获取指定步骤的详细信息"""
        if step_num < 1 or step_num > 4:
            return {"error": "步骤范围1-4"}

        lessons = {
            1: self.lessons[1],  # msg1
            2: self.lessons[2],  # msg2
            3: self.lessons[3],  # msg3
            4: self.lessons[4],  # msg4
        }
        lesson = lessons[step_num]

        info = {
            "step": step_num,
            "title": lesson.title,
            "description": lesson.description,
            "content": lesson.content,
            "key_points": lesson.key_points,
            "warning": lesson.warning,
        }

        # 如果有对应数据包，也加上
        if step_num <= len(self.packets):
            packet = self.packets[step_num - 1]
            info["packet"] = {
                "number": packet.packet_number,
                "direction": "AP -> Client" if packet.from_ap else "Client -> AP",
                "key_info": packet.eapol_key_info,
                "nonce": packet.nonce,
                "mic": packet.mic,
                "key_length": packet.key_length,
            }

        return info

    def do_step(self) -> Dict:
        """执行下一步，返回详细信息"""
        if self.completed:
            return {"completed": True, "step": self.step}

        self.step += 1

        if self.step == 1:
            return self._do_step1()
        elif self.step == 2:
            return self._do_step2()
        elif self.step == 3:
            return self._do_step3()
        elif self.step == 4:
            return self._do_step4()
        else:
            self.completed = True
            return {"completed": True, "step": self.step}

    def _do_step1(self) -> Dict:
        """步骤1：AP发送ANonce"""
        self._anonce = self.generate_random_nonce()

        packet = HandshakePacket(
            packet_number=1,
            from_ap=True,
            eapol_key_info="0x008a",
            key_information={"key_type": True, "install": False, "ack": True, "mic": False},
            key_length=16,
            replay_counter=1,
            nonce=self._anonce,
            iv="00000000000000000000000000000000",
            rsc="0000000000000000",
            mic="00000000000000000000000000000000",
            key_data_length=0,
            key_data=""
        )
        self.packets.append(packet)

        # 计算PMK
        self._pmk = self.compute_pmk(self._password, self._ssid)
        self.derivation_steps.append(KeyDerivationStep(
            step_name="PMK生成",
            description="由密码和SSID通过PBKDF2生成主密钥",
            input_data=f"密码: {'*' * len(self._password)}, SSID: {self._ssid}",
            output_data=f"PMK: {self._pmk[:16]}...",
            algorithm="PBKDF2-HMAC-SHA1 (4096 iterations)"
        ))

        lesson = self.lessons[1]
        return {
            "step": 1,
            "completed": False,
            "title": lesson.title,
            "content": lesson.content,
            "key_points": lesson.key_points,
            "warning": lesson.warning,
            "packet": {
                "direction": "AP → 客户端",
                "name": "EAPOL-Key Message 1",
                "nonce": self._anonce,
                "description": "AP生成ANonce并发送给客户端"
            },
            "derivation": self.derivation_steps[-1].__dict__ if self.derivation_steps else None
        }

    def _do_step2(self) -> Dict:
        """步骤2：客户端响应SNonce + MIC"""
        self._snonce = self.generate_random_nonce()

        # 客户端计算PTK
        self._ptk = self.compute_ptk(
            self._pmk, self._anonce, self._snonce,
            self._ap_mac, self._client_mac
        )
        self.derivation_steps.append(KeyDerivationStep(
            step_name="PTK派生",
            description="客户端用PMK、ANonce、SNonce和MAC地址计算PTK",
            input_data=f"PMK + ANonce + SNonce + AP_MAC + Client_MAC",
            output_data=f"PTK: {self._ptk[:32]}... (48字节)",
            algorithm="PRF-SHA1 (伪随机函数)"
        ))

        # 提取KCK用于计算MIC
        kck = bytes.fromhex(self._ptk)[:16]
        mic = hmac.new(kck, b"EAPOL-Msg2", hashlib.sha1).hexdigest()[:32]

        packet = HandshakePacket(
            packet_number=2,
            from_ap=False,
            eapol_key_info="0x010a",
            key_information={"key_type": True, "install": False, "ack": False, "mic": True},
            key_length=16,
            replay_counter=1,
            nonce=self._snonce,
            iv="00000000000000000000000000000000",
            rsc="0000000000000000",
            mic=mic,
            key_data_length=0,
            key_data=""
        )
        self.packets.append(packet)

        lesson = self.lessons[2]
        return {
            "step": 2,
            "completed": False,
            "title": lesson.title,
            "content": lesson.content,
            "key_points": lesson.key_points,
            "warning": lesson.warning,
            "packet": {
                "direction": "客户端 → AP",
                "name": "EAPOL-Key Message 2",
                "nonce": self._snonce,
                "mic": mic,
                "description": "客户端发送SNonce和MIC（证明自己知道密码）"
            },
            "derivation": self.derivation_steps[-1].__dict__ if self.derivation_steps else None
        }

    def _do_step3(self) -> Dict:
        """步骤3：AP发送GTK"""
        # AP验证MIC并计算PTK（结果应该和客户端的一样）
        ap_ptk = self.compute_ptk(
            self._pmk, self._anonce, self._snonce,
            self._ap_mac, self._client_mac
        )
        assert ap_ptk == self._ptk, "PTK不匹配（模拟演示中应该匹配）"

        # 生成GTK
        self._gtk = self.generate_random_nonce()[:32]  # 16字节GTK

        self.derivation_steps.append(KeyDerivationStep(
            step_name="GTK生成",
            description="AP生成组临时密钥，用于广播/组播加密",
            input_data="AP随机生成",
            output_data=f"GTK: {self._gtk[:16]}...",
            algorithm="随机生成"
        ))

        # 用KEK加密GTK（简化：用KEK做HMAC模拟）
        kek = bytes.fromhex(self._ptk)[16:32]
        encrypted_gtk = hmac.new(kek, bytes.fromhex(self._gtk), hashlib.sha256).hexdigest()

        # 计算MIC
        kck = bytes.fromhex(self._ptk)[:16]
        mic = hmac.new(kck, b"EAPOL-Msg3", hashlib.sha1).hexdigest()[:32]

        packet = HandshakePacket(
            packet_number=3,
            from_ap=True,
            eapol_key_info="0x01c9",
            key_information={"key_type": True, "install": True, "ack": True, "mic": True, "secure": True},
            key_length=16,
            replay_counter=2,
            nonce=self._anonce,
            iv="00000000000000000000000000000000",
            rsc="0000000000000000",
            mic=mic,
            key_data_length=32,
            key_data=encrypted_gtk
        )
        self.packets.append(packet)

        lesson = self.lessons[3]
        return {
            "step": 3,
            "completed": False,
            "title": lesson.title,
            "content": lesson.content,
            "key_points": lesson.key_points,
            "warning": lesson.warning,
            "packet": {
                "direction": "AP → 客户端",
                "name": "EAPOL-Key Message 3",
                "gtk_encrypted": encrypted_gtk,
                "mic": mic,
                "install": True,
                "description": "AP发送加密的GTK，告诉客户端可以安装密钥了"
            },
            "derivation": self.derivation_steps[-1].__dict__ if self.derivation_steps else None
        }

    def _do_step4(self) -> Dict:
        """步骤4：客户端确认"""
        # 客户端验证MIC并解密GTK（简化）

        # 计算确认MIC
        kck = bytes.fromhex(self._ptk)[:16]
        mic = hmac.new(kck, b"EAPOL-Msg4", hashlib.sha1).hexdigest()[:32]

        packet = HandshakePacket(
            packet_number=4,
            from_ap=False,
            eapol_key_info="0x0309",
            key_information={"key_type": True, "install": False, "ack": False, "mic": True, "secure": True},
            key_length=16,
            replay_counter=2,
            nonce="0000000000000000000000000000000000000000000000000000000000000000",
            iv="00000000000000000000000000000000",
            rsc="0000000000000000",
            mic=mic,
            key_data_length=0,
            key_data=""
        )
        self.packets.append(packet)

        self.completed = True

        lesson = self.lessons[4]
        return {
            "step": 4,
            "completed": True,
            "title": lesson.title,
            "content": lesson.content,
            "key_points": lesson.key_points,
            "warning": lesson.warning,
            "packet": {
                "direction": "客户端 → AP",
                "name": "EAPOL-Key Message 4",
                "mic": mic,
                "description": "客户端确认，握手完成！"
            },
            "final_state": {
                "pmk": self._pmk,
                "ptk": self._ptk,
                "gtk": self._gtk,
                "keys_installed": True,
                "handshake_complete": True
            }
        }

    def get_all_lessons(self) -> List[Dict]:
        """获取所有教学课程摘要"""
        return [
            {
                "id": lesson.lesson_id,
                "title": lesson.title,
                "description": lesson.description,
                "step": i if i < len(self.lessons) - 1 else None
            }
            for i, lesson in enumerate(self.lessons)
        ]

    def get_lesson(self, lesson_id: str) -> Optional[Dict]:
        """获取指定课程"""
        for lesson in self.lessons:
            if lesson.lesson_id == lesson_id:
                return {
                    "id": lesson.lesson_id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "content": lesson.content,
                    "key_points": lesson.key_points,
                    "warning": lesson.warning
                }
        return None

    def get_security_notes(self) -> List[str]:
        """获取安全注意事项"""
        return [
            "本模拟器仅用于学习WPA握手协议原理",
            "握手机制本身是安全的，风险主要来自弱密码",
            "使用强密码（≥12位，混合字符）可以有效抵御字典攻击",
            "WPA3的SAE握手进一步增强了安全性",
            "禁止对任何未授权的网络进行攻击测试",
            "请在自己的网络上进行学习和实验",
        ]


# 创建全局实例
_handshake_simulator = None

def get_handshake_simulator() -> WPAHandshakeSimulator:
    """获取握手模拟器单例"""
    global _handshake_simulator
    if _handshake_simulator is None:
        _handshake_simulator = WPAHandshakeSimulator()
    return _handshake_simulator

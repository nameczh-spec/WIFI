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

    def get_pbkdf2_detail(self, password: str, ssid: str) -> Dict:
        """PBKDF2逐步骤计算演示"""
        iterations = 4096
        pmk = hashlib.pbkdf2_hmac('sha1', password.encode(), ssid.encode(), iterations, 32)
        
        steps = []
        
        steps.append({
            "step_num": 1,
            "title": "准备输入",
            "description": "PBKDF2需要四个输入参数：密码、盐（SSID）、迭代次数、输出长度",
            "input_preview": f"密码: {'•' * len(password)} ({len(password)}字符)\nSSID: {ssid}\n迭代次数: {iterations}\n输出长度: 32字节 (256位)",
            "output_preview": "等待计算...",
            "algorithm": "PBKDF2-HMAC-SHA1",
        })
        
        steps.append({
            "step_num": 2,
            "title": "第1次迭代 (U1)",
            "description": "第一次迭代：对密码 + 盐 + 块索引 计算HMAC-SHA1",
            "input_preview": f"HMAC-SHA1(密码, SSID || 0x00000001)",
            "output_preview": "U1 = HMAC-SHA1(Password, Salt || 1)\n(20字节SHA1输出)",
            "algorithm": "HMAC-SHA1",
            "note": "这是第1次HMAC计算，结果作为U1",
        })
        
        steps.append({
            "step_num": 3,
            "title": "迭代累积 (U2 ~ U4096)",
            "description": f"后续每次迭代：用上一次的结果作为输入再次计算HMAC，然后与累积结果异或",
            "input_preview": f"U2 = HMAC-SHA1(密码, U1)\nU3 = HMAC-SHA1(密码, U2)\n...\n重复 {iterations} 次",
            "output_preview": f"DK = U1 ⊕ U2 ⊕ U3 ⊕ ... ⊕ U{iterations}",
            "algorithm": "HMAC-SHA1 × 4096次 + XOR累积",
            "note": f"这是最耗时的步骤，{iterations}次迭代使得暴力破解的成本大幅增加",
        })
        
        steps.append({
            "step_num": 4,
            "title": "生成最终PMK",
            "description": "经过4096次迭代后，得到最终的256位PMK（成对主密钥）",
            "input_preview": f"密码 + SSID + {iterations}次HMAC迭代",
            "output_preview": f"PMK: {pmk.hex()[:32]}... (32字节/256位)",
            "algorithm": "PBKDF2-HMAC-SHA1 完成",
        })
        
        return {
            "success": True,
            "steps": steps,
            "pmk": pmk.hex(),
            "iterations": iterations,
            "password_length": len(password),
            "ssid": ssid,
        }

    def get_prf_detail(self, pmk_hex: str, ap_mac: str, client_mac: str,
                       anonce: str, snonce: str) -> Dict:
        """PRF-X函数详细演示"""
        pmk = bytes.fromhex(pmk_hex)
        
        def mac_to_bytes(mac_str: str) -> bytes:
            return bytes.fromhex(mac_str.replace(':', ''))
        
        ap_b = mac_to_bytes(ap_mac)
        cli_b = mac_to_bytes(client_mac)
        a_n = bytes.fromhex(anonce)
        s_n = bytes.fromhex(snonce)
        
        mac_min = min(ap_b, cli_b)
        mac_max = max(ap_b, cli_b)
        nonce_min = min(a_n, s_n)
        nonce_max = max(a_n, s_n)
        
        label = b"Pairwise key expansion"
        data = label + b"\x00" + mac_min + mac_max + nonce_min + nonce_max
        
        full_ptk = b""
        for i in range(4):
            round_data = data + bytes([i])
            round_result = hmac.new(pmk, round_data, hashlib.sha1).digest()
            full_ptk += round_result
        
        ptk = full_ptk[:48]
        
        steps = [
            {
                "step_num": 1,
                "title": "准备PRF输入",
                "description": "PRF（伪随机函数）需要PMK、标签字符串和输入数据",
                "input_preview": f"PMK: {pmk_hex[:16]}...\n标签: 'Pairwise key expansion'\n数据: Min(MAC)||Max(MAC)||Min(Nonce)||Max(Nonce)",
                "output_preview": "等待计算...",
                "algorithm": "PRF-SHA1",
            },
            {
                "step_num": 2,
                "title": "排序地址和Nonce",
                "description": "为了确保AP和客户端计算出相同的PTK，需要对MAC地址和Nonce进行排序",
                "input_preview": f"AP_MAC: {ap_mac}\nClient_MAC: {client_mac}\nANonce: {anonce[:16]}...\nSNonce: {snonce[:16]}...",
                "output_preview": f"Min(MAC): {mac_min.hex()}\nMax(MAC): {mac_max.hex()}\nMin(Nonce): {nonce_min.hex()[:16]}...\nMax(Nonce): {nonce_max.hex()[:16]}...",
                "note": "排序保证双方计算顺序一致，结果相同",
            },
            {
                "step_num": 3,
                "title": "多轮HMAC扩展",
                "description": "通过多轮HMAC-SHA1将PMK扩展到需要的长度",
                "input_preview": f"PTK-0 = HMAC-SHA1(PMK, 数据 || 0)\nPTK-1 = HMAC-SHA1(PMK, 数据 || 1)\nPTK-2 = HMAC-SHA1(PMK, 数据 || 2)\nPTK-3 = HMAC-SHA1(PMK, 数据 || 3)",
                "output_preview": f"PTK = PTK-0 || PTK-1 || PTK-2 || PTK-3 (取前48字节)",
                "algorithm": "HMAC-SHA1 × 4轮",
            },
            {
                "step_num": 4,
                "title": "生成最终PTK",
                "description": "拼接并截取，得到48字节的PTK",
                "input_preview": "4轮HMAC输出拼接",
                "output_preview": f"PTK: {ptk.hex()[:48]}... (48字节/384位)",
                "algorithm": "PRF-SHA1 完成",
            },
        ]
        
        return {
            "success": True,
            "ptk": ptk.hex(),
            "steps": steps,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce": anonce,
            "snonce": snonce,
            "label": label.decode(),
        }

    def decompose_ptk(self, ptk_hex: str) -> Dict:
        """将PTK分解为各个子密钥"""
        ptk = bytes.fromhex(ptk_hex)
        
        kck = ptk[0:16]
        kek = ptk[16:32]
        tk = ptk[32:48]
        
        mic_tx = ptk[0:8] if len(ptk) >= 8 else b""
        mic_rx = ptk[8:16] if len(ptk) >= 16 else b""
        
        return {
            "success": True,
            "total_length": len(ptk),
            "kck": {
                "name": "KCK (Key Confirmation Key)",
                "offset": "0-15字节",
                "length": "16字节 (128位)",
                "purpose": "密钥确认密钥，用于计算MIC（消息完整性校验）",
                "hex": kck.hex(),
            },
            "kek": {
                "name": "KEK (Key Encryption Key)",
                "offset": "16-31字节",
                "length": "16字节 (128位)",
                "purpose": "密钥加密密钥，用于加密传输GTK",
                "hex": kek.hex(),
            },
            "tk": {
                "name": "TK (Temporal Key)",
                "offset": "32-47字节",
                "length": "16字节 (128位)",
                "purpose": "临时密钥，用于实际数据加密（CCMP/TKIP）",
                "hex": tk.hex(),
            },
            "mic_tx": {
                "name": "MIC Tx (Michael Tx)",
                "offset": "PTK前半部分派生",
                "length": "8字节 (64位)",
                "purpose": "发送方向的Michael算法完整性校验密钥（TKIP使用）",
                "hex": mic_tx.hex(),
            },
            "mic_rx": {
                "name": "MIC Rx (Michael Rx)",
                "offset": "PTK前半部分派生",
                "length": "8字节 (64位)",
                "purpose": "接收方向的Michael算法完整性校验密钥（TKIP使用）",
                "hex": mic_rx.hex(),
            },
        }

    def get_derivation_chain(self) -> Dict:
        """密钥推导链可视化数据"""
        nodes = [
            {"id": "password", "label": "用户密码", "level": 0, "type": "input"},
            {"id": "ssid", "label": "SSID (盐)", "level": 0, "type": "input"},
            {"id": "pmk", "label": "PMK\n成对主密钥", "level": 1, "type": "key"},
            {"id": "ptk", "label": "PTK\n成对临时密钥", "level": 2, "type": "key"},
            {"id": "kck", "label": "KCK\n密钥确认密钥", "level": 3, "type": "subkey"},
            {"id": "kek", "label": "KEK\n密钥加密密钥", "level": 3, "type": "subkey"},
            {"id": "tk", "label": "TK\n临时密钥", "level": 3, "type": "subkey"},
            {"id": "gtk", "label": "GTK\n组临时密钥", "level": 2, "type": "key"},
            {"id": "data_encryption", "label": "数据加密\n(CCMP/TKIP)", "level": 4, "type": "usage"},
            {"id": "mic", "label": "MIC验证\n(消息完整性)", "level": 4, "type": "usage"},
            {"id": "gtk_encryption", "label": "GTK加密传输", "level": 4, "type": "usage"},
        ]
        
        edges = [
            {"from": "password", "to": "pmk", "label": "PBKDF2\n4096次迭代", "algorithm": "HMAC-SHA1"},
            {"from": "ssid", "to": "pmk", "label": "作为盐", "algorithm": ""},
            {"from": "pmk", "to": "ptk", "label": "PRF + ANonce + SNonce + MAC", "algorithm": "HMAC-SHA1"},
            {"from": "ptk", "to": "kck", "label": "分解", "algorithm": "0-15字节"},
            {"from": "ptk", "to": "kek", "label": "分解", "algorithm": "16-31字节"},
            {"from": "ptk", "to": "tk", "label": "分解", "algorithm": "32-47字节"},
            {"from": "kck", "to": "mic", "label": "计算MIC", "algorithm": "HMAC-SHA1"},
            {"from": "kek", "to": "gtk_encryption", "label": "加密GTK", "algorithm": "AES-Keywrap"},
            {"from": "tk", "to": "data_encryption", "label": "加密数据", "algorithm": "AES-CCM"},
            {"from": "pmk", "to": "gtk", "label": "AP生成", "algorithm": "随机"},
        ]
        
        return {
            "success": True,
            "nodes": nodes,
            "edges": edges,
            "levels": 5,
            "description": "WPA2密钥层次结构：密码 → PMK → PTK → 子密钥 → 实际使用",
        }

    def get_pbkdf2_animation_data(self, password: str, ssid: str,
                                  num_iterations: int = 10) -> Dict:
        """PBKDF2迭代动画数据（可视化用）"""
        iterations_data = []
        password_bytes = password.encode()
        salt = ssid.encode()
        
        prev_hash = b""
        accumulator = b"\x00" * 20
        
        for i in range(1, num_iterations + 1):
            if i == 1:
                u_input = salt + b"\x00\x00\x00\x01"
                current_hash = hmac.new(password_bytes, u_input, hashlib.sha1).digest()
                prev_hash = current_hash
            else:
                current_hash = hmac.new(password_bytes, prev_hash, hashlib.sha1).digest()
                prev_hash = current_hash
            
            accumulator = bytes(a ^ b for a, b in zip(accumulator, current_hash))
            
            iterations_data.append({
                "iteration": i,
                "input_hash": prev_hash.hex() if i > 1 else (salt + b"\x00\x00\x00\x01").hex()[:40],
                "output_hash": current_hash.hex(),
                "accumulator": accumulator.hex(),
                "operation": "U1 = HMAC(P, S || 1)" if i == 1 else f"U{i} = HMAC(P, U{i-1})",
                "accumulate_op": f"DK ⊕= U{i}",
            })
        
        return {
            "success": True,
            "iterations": iterations_data,
            "total_iterations": 4096,
            "showing_iterations": num_iterations,
            "note": f"展示前{num_iterations}次迭代，实际WPA2使用4096次迭代",
        }

    def get_key_security_explanations(self) -> Dict:
        """密钥安全原理解释"""
        return {
            "pmk_security": {
                "title": "PMK的安全性",
                "principle": """
                    <h4>PMK是如何保证安全的？</h4>
                    <p>PMK（成对主密钥）由密码通过PBKDF2算法派生。PBKDF2的核心设计是<strong>慢</strong>——故意让计算变得昂贵。</p>
                    
                    <h4>关键安全机制</h4>
                    <ul>
                        <li><strong>4096次迭代</strong>：每次密码尝试都需要4096次HMAC-SHA1计算</li>
                        <li><strong>盐值（SSID）</strong>：相同密码在不同网络产生不同PMK</li>
                        <li><strong>单向函数</strong>：无法从PMK反推密码</li>
                    </ul>
                    
                    <h4>为什么用4096次？</h4>
                    <p>迭代次数是安全性和用户体验的权衡：</p>
                    <ul>
                        <li>次数太少：容易被暴力破解</li>
                        <li>次数太多：连接太慢，用户体验差</li>
                        <li>4096是2004年WPA2标准制定时的合理选择</li>
                    </ul>
                """,
                "why_secure": """
                    <h4>为什么这是安全的？</h4>
                    <ol>
                        <li><strong>计算成本高</strong>：尝试一个密码需要4096次HMAC计算</li>
                        <li><strong>GPU也有极限</strong>：即使GPU每秒尝试10万次，8位纯字母密码也需要约3年</li>
                        <li><strong>强密码无解</strong>：12位混合密码的组合空间是94^12，远超任何计算能力</li>
                    </ol>
                    
                    <p><strong>结论：PMK的设计是安全的，弱点在于用户的密码强度。</strong></p>
                """,
            },
            "ptk_security": {
                "title": "PTK的安全性",
                "principle": """
                    <h4>PTK的安全特性</h4>
                    <p>PTK（成对临时密钥）的设计目标是<strong>前向保密性</strong>。</p>
                    
                    <h4>前向保密性（Forward Secrecy）</h4>
                    <p>即使某次会话的PTK泄露，也不会影响其他会话的安全，也不会泄露PMK。</p>
                    
                    <h4>实现原理</h4>
                    <ul>
                        <li><strong>每次握手都不同</strong>：ANonce和SNonce都是随机的</li>
                        <li><strong>PRF是单向的</strong>：无法从PTK反推PMK</li>
                        <li><strong>会话结束即失效</strong>：断开连接后PTK就没用了</li>
                    </ul>
                    
                    <h4>为什么每次都要重新生成？</h4>
                    <ol>
                        <li>限制密钥使用时间：减少被破解的时间窗口</li>
                        <li>隔离不同会话：一个会话被破解不影响其他会话</li>
                        <li>防止累积攻击：截获的数据包越多，不会越容易破解</li>
                    </ol>
                """,
                "why_secure": """
                    <h4>安全保障</h4>
                    <ul>
                        <li><strong>随机Nonce</strong>：ANonce和SNonce都是32字节的真随机数</li>
                        <li><strong>HMAC-SHA1</strong>：经过严格密码学分析的伪随机函数</li>
                        <li><strong>384位输出</strong>：PTK长达48字节，强度充足</li>
                    </ul>
                    
                    <p><strong>结论：PTK的派生机制是安全的，只要PMK安全，PTK就安全。</strong></p>
                """,
            },
            "forward_secrecy": {
                "title": "前向保密性详解",
                "principle": """
                    <h4>什么是前向保密性？</h4>
                    <p>前向保密性（Forward Secrecy / Perfect Forward Secrecy）是指：</p>
                    <blockquote>即使长期密钥（如PMK或密码）泄露，之前的会话密钥（如PTK）也无法被还原。</blockquote>
                    
                    <h4>WPA2中的前向保密性</h4>
                    <p>WPA2具有部分前向保密性：</p>
                    <ul>
                        <li>✅ 每次握手生成不同的PTK</li>
                        <li>✅ 无法从PTK反推PMK</li>
                        <li>❌ 但如果知道密码，可以重新计算任何会话的PTK（只要知道Nonce）</li>
                    </ul>
                    
                    <h4>WPA3的改进</h4>
                    <p>WPA3使用SAE（Simultaneous Authentication of Equals）协议，提供了真正的前向保密性：</p>
                    <ul>
                        <li>✅ 即使知道密码，也无法还原之前的会话密钥</li>
                        <li>✅ 抵抗离线字典攻击</li>
                        <li>✅ Dragonfly握手协议</li>
                    </ul>
                """,
                "why_secure": """
                    <h4>为什么前向保密性很重要？</h4>
                    <ol>
                        <li><strong>数据保护期更长</strong>：即使密码后来泄露，之前的数据仍然安全</li>
                        <li><strong>降低攻击影响范围</strong>：一次密钥泄露只影响当前会话</li>
                        <li><strong>符合隐私保护原则</strong>：历史通信应该保持私密</li>
                    </ol>
                    
                    <p><strong>最佳实践：升级到WPA3可以获得更强的前向保密性。</strong></p>
                """,
            },
        }

    def get_derivation_info_basic(self, pmk_hex: str, ap_mac: str, client_mac: str,
                                   anonce: str, snonce: str,
                                   detail_level: str = "basic") -> Dict:
        """渐进式密钥推导信息展示"""
        basic = {
            "success": True,
            "pmk_preview": pmk_hex[:16] + "..." + pmk_hex[-8:],
            "ptk_length": "48字节 (384位)",
            "algorithm": "PBKDF2 → PRF-SHA1",
        }
        
        if detail_level == "basic":
            return basic
        
        ptk_result = self.get_prf_detail(pmk_hex, ap_mac, client_mac, anonce, snonce)
        detailed = {
            **basic,
            "ap_mac": ap_mac,
            "client_mac": client_mac,
            "anonce_preview": anonce[:16] + "...",
            "snonce_preview": snonce[:16] + "...",
            "ptk_preview": ptk_result["ptk"][:32] + "...",
            "key_components": ["KCK (16B)", "KEK (16B)", "TK (16B)"],
        }
        
        if detail_level == "detailed":
            return detailed
        
        decomposed = self.decompose_ptk(ptk_result["ptk"])
        full = {
            **detailed,
            "pbkdf2_steps": self.get_pbkdf2_detail("********", "TestSSID")["steps"],
            "prf_steps": ptk_result["steps"],
            "decomposed_keys": decomposed,
            "derivation_chain": self.get_derivation_chain(),
            "security_explanations": self.get_key_security_explanations(),
        }
        
        return full


# 创建全局实例
_handshake_simulator = None

def get_handshake_simulator() -> WPAHandshakeSimulator:
    """获取握手模拟器单例"""
    global _handshake_simulator
    if _handshake_simulator is None:
        _handshake_simulator = WPAHandshakeSimulator()
    return _handshake_simulator

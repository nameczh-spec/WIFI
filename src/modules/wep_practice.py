"""
WEP破解练习模拟模块
纯模拟环境，仅供学习研究使用
详细模拟WEP加密原理、IV收集、FMS/KoreK攻击教学演示
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class WEPIvData:
    """WEP IV数据包"""
    iv: str
    is_weak: bool
    key_byte_hint: Optional[int] = None
    captured_at: float = 0.0


@dataclass
class WEPLesson:
    """WEP教学课程"""
    lesson_id: str
    title: str
    description: str
    content: str
    key_points: List[str]
    warning: str = "仅供学习研究，禁止用于未授权网络"


class WEPPracticeSimulator:
    """
    WEP破解练习模拟器
    纯教学演示，不涉及任何真实数据包收发
    """

    TOTAL_IV_TARGET = 50000
    WEAK_IV_RATIO = 0.05

    def __init__(self):
        self.started = False
        self.completed = False
        self.cracked = False

        self.ssid = ""
        self.bssid = ""
        self.wep_key = ""
        self.key_length = 0

        self.ivs_collected = 0
        self.weak_ivs_collected = 0
        self.iv_history: List[int] = []
        self.weak_iv_history: List[int] = []

        self.crack_progress = 0.0
        self.cracked_key_bytes: List[Optional[str]] = []
        self.crack_attempts = 0

        self._lesson_index = 0
        self._init_lessons()

    def _init_lessons(self):
        """初始化教学课程"""
        self.lessons = [
            WEPLesson(
                lesson_id="wep-intro",
                title="WEP加密原理简介",
                description="了解WEP加密的基本原理和安全缺陷",
                content="""
                    <h3>什么是WEP？</h3>
                    <p>WEP（Wired Equivalent Privacy）是最早的WiFi加密标准，于1999年发布，旨在提供与有线网络相当的安全性。</p>
                    
                    <h4>WEP加密方式：</h4>
                    <ul>
                        <li><strong>加密算法</strong>：RC4流密码</li>
                        <li><strong>密钥长度</strong>：64位（40位密钥+24位IV）或128位（104位密钥+24位IV）</li>
                        <li><strong>完整性校验</strong>：CRC-32</li>
                    </ul>
                    
                    <h4>为什么WEP不安全？</h4>
                    <ol>
                        <li><strong>IV空间太小</strong>：只有24位（约1600万），繁忙网络中几小时就会重复</li>
                        <li><strong>IV重复风险</strong>：相同IV+密钥会产生相同的密钥流，可用于XOR攻击</li>
                        <li><strong>弱IV漏洞</strong>：某些IV（弱IV）会泄露密钥信息</li>
                        <li><strong>CRC-32不安全</strong>：可被篡改而不被发现</li>
                    </ol>
                    
                    <h4>历史教训</h4>
                    <p>WEP在2003年被WPA取代，2004年正式被IEEE废弃。但仍有一些老旧设备在使用WEP。</p>
                """,
                key_points=[
                    "WEP使用RC4流密码加密",
                    "24位IV空间太小，容易重复",
                    "弱IV（FMS攻击）可快速破解密钥",
                    "WEP已被废弃，应使用WPA2/WPA3",
                ]
            ),
            WEPLesson(
                lesson_id="wep-rc4",
                title="RC4流密码与WEP加密过程",
                description="深入理解RC4算法和WEP的加密流程",
                content="""
                    <h3>RC4流密码算法</h3>
                    <p>RC4是Ron Rivest在1987年设计的流密码算法，以其简单和高效著称。</p>
                    
                    <h4>RC4两个阶段：</h4>
                    <ol>
                        <li><strong>KSA（密钥调度算法）</strong>：用密钥初始化256字节的S盒</li>
                        <li><strong>PRGA（伪随机生成算法）</strong>：生成密钥流字节</li>
                    </ol>
                    
                    <h4>WEP加密流程：</h4>
                    <pre>
密钥流 = RC4(IV || 密钥)
密文 = 明文 XOR 密钥流
ICV = CRC32(明文)
发送 = IV || (明文 || ICV) XOR 密钥流
                    </pre>
                    
                    <h4>问题所在</h4>
                    <p>IV以明文形式发送，且与密钥拼接后作为RC4的输入。这意味着：</p>
                    <ul>
                        <li>如果知道IV，就知道RC4输入的前24位</li>
                        <li>相同IV + 相同密钥 → 相同密钥流</li>
                        <li>收集足够多的IV，可通过统计分析还原密钥</li>
                    </ul>
                """,
                key_points=[
                    "RC4由KSA和PRGA两阶段组成",
                    "WEP将IV和密钥拼接作为RC4输入",
                    "IV以明文传输，攻击者可见",
                    "相同IV产生相同密钥流",
                ]
            ),
            WEPLesson(
                lesson_id="wep-iv-collection",
                title="IV收集与弱IV检测",
                description="学习如何收集IV以及什么是弱IV",
                content="""
                    <h3>IV收集</h3>
                    <p>破解WEP的第一步是收集足够多的数据包，从中提取IV。每个数据包都包含一个不同的IV。</p>
                    
                    <h4>需要多少IV？</h4>
                    <ul>
                        <li><strong>FMS攻击</strong>：约50万~100万IV</li>
                        <li><strong>KoreK攻击</strong>：约10万IV</li>
                        <li><strong>PTW攻击</strong>：约2万~4万IV</li>
                    </ul>
                    
                    <h4>什么是弱IV（Weak IVs）？</h4>
                    <p>FMS攻击（Fluhrer, Mantin, Shamir）发现，某些特定格式的IV会泄露密钥字节的信息。</p>
                    <p>典型弱IV格式：(A+3, N-1, X)，其中A是已破解的密钥字节数，N=256</p>
                    
                    <h4>弱IV的特征</h4>
                    <ul>
                        <li>IV的第一个字节 = 已破解密钥字节数 + 3</li>
                        <li>IV的第二个字节 = 255（N-1）</li>
                        <li>这类IV会导致S盒的特定状态，泄露密钥信息</li>
                        <li>每256个IV中约有1个弱IV</li>
                    </ul>
                    
                    <h4>加速IV收集的方法（仅学习）</h4>
                    <ul>
                        <li>ARP请求注入：触发AP回复大量ARP响应包</li>
                        <li>碎片攻击：利用已知明文生成更多数据包</li>
                        <li>Caffe-Latte攻击：针对客户端的攻击方式</li>
                    </ul>
                """,
                key_points=[
                    "破解需要收集大量IV",
                    "弱IV会泄露密钥字节信息",
                    "FMS攻击利用弱IV还原密钥",
                    "注入攻击可加速IV收集",
                ]
            ),
            WEPLesson(
                lesson_id="wep-fms-attack",
                title="FMS攻击原理详解",
                description="理解FMS攻击如何利用弱IV还原密钥",
                content="""
                    <h3>FMS攻击原理</h3>
                    <p>FMS攻击由Fluhrer、Mantin和Shamir在2001年提出，是第一个针对WEP的有效攻击。</p>
                    
                    <h4>攻击前提</h4>
                    <ul>
                        <li>攻击者可以监听到足够多的数据包</li>
                        <li>包含足够多的弱IV</li>
                        <li>知道部分明文（如ARP报文的固定头部）</li>
                    </ul>
                    
                    <h4>攻击步骤（逐字节破解）</h4>
                    <ol>
                        <li><strong>破解第一个密钥字节</strong>：收集IV[0]=3, IV[1]=255的弱IV</li>
                        <li><strong>统计分析</strong>：对每个可能的密钥字节值进行投票</li>
                        <li><strong>选出得票最高的值</strong>：大概率是正确的密钥字节</li>
                        <li><strong>继续下一字节</strong>：用已知的密钥字节寻找下一组弱IV</li>
                        <li><strong>重复直到全部破解</strong>：逐字节还原完整密钥</li>
                    </ol>
                    
                    <h4>为什么会这样？</h4>
                    <p>当IV的前两个字节为 (A+3, 255) 时，经过KSA的前A+3轮后：</p>
                    <ul>
                        <li>S盒的前A+3个元素处于特定状态</li>
                        <li>PRGA输出的第一个字节与第A+1个密钥字节相关</li>
                        <li>利用已知明文可计算出密钥字节的候选值</li>
                        <li>多个弱IV投票，正确值出现概率最高</li>
                    </ul>
                    
                    <h4>后续改进</h4>
                    <p>KoreK攻击和PTW攻击进一步优化了统计方法，大幅减少了所需IV数量。</p>
                """,
                key_points=[
                    "FMS攻击逐字节破解密钥",
                    "利用弱IV的统计特性",
                    "投票机制选出最可能的密钥字节",
                    "PTW攻击进一步优化，只需几万IV",
                ]
            ),
            WEPLesson(
                lesson_id="wep-cracking-demo",
                title="破解过程演示",
                description="模拟WEP密钥破解的完整过程",
                content="""
                    <h3>WEP破解演示</h3>
                    <p>现在我们来模拟一个完整的WEP破解过程。这是纯教学演示，帮助你理解攻击原理。</p>
                    
                    <h4>破解工具（仅学习了解）</h4>
                    <ul>
                        <li><strong>aircrack-ng</strong>：最流行的WiFi安全审计工具套件</li>
                        <li><strong>airodump-ng</strong>：捕获数据包和IV</li>
                        <li><strong>aireplay-ng</strong>：数据包注入加速IV收集</li>
                        <li><strong>aircrack-ng</strong>：分析IV并破解密钥</li>
                    </ul>
                    
                    <h4>典型破解流程</h4>
                    <ol>
                        <li>启动监控模式，监听目标信道</li>
                        <li>捕获数据包，收集IV</li>
                        <li>（可选）进行注入攻击加速IV收集</li>
                        <li>使用aircrack-ng分析收集的IV</li>
                        <li>得到WEP密钥</li>
                    </ol>
                    
                    <h4>本模拟器的演示</h4>
                    <p>在本练习中，你将体验：</p>
                    <ul>
                        <li>IV收集进度模拟</li>
                        <li>弱IV检测和统计</li>
                        <li>逐字节破解过程动画</li>
                        <li>密钥验证结果</li>
                    </ul>
                """,
                key_points=[
                    "aircrack-ng是WEP破解的标准工具",
                    "IV收集是最耗时的步骤",
                    "注入攻击可大幅加速",
                    "理解原理比掌握工具更重要",
                ]
            ),
            WEPLesson(
                lesson_id="wep-security",
                title="安全启示与防御措施",
                description="从WEP漏洞中学到的安全教训",
                content="""
                    <h3>WEP的安全教训</h3>
                    <p>WEP的失败给我们留下了宝贵的安全经验和教训。</p>
                    
                    <h4>WEP失败的根本原因</h4>
                    <ol>
                        <li><strong>IV空间不足</strong>：24位太小，应该至少64位</li>
                        <li><strong>密钥复用问题</strong>：相同IV+密钥产生相同密钥流</li>
                        <li><strong>CRC不适合做完整性校验</strong>：CRC是线性的，可被篡改</li>
                        <li><strong>没有重放保护</strong>：攻击者可重放旧数据包</li>
                        <li><strong>密钥管理缺失</strong>：所有用户共享同一密钥</li>
                    </ol>
                    
                    <h4>如何防御？升级！</h4>
                    <p><strong>唯一正确的做法：停止使用WEP，升级到WPA2或WPA3</strong></p>
                    
                    <h4>WPA2/WPA3的改进</h4>
                    <ul>
                        <li><strong>更大的IV空间</strong>：48位（WPA的TSC）</li>
                        <li><strong>每包不同密钥</strong>：结合TKIP或CCMP</li>
                        <li><strong>强完整性校验</strong>：Michael MIC或CCM（CBC-MAC）</li>
                        <li><strong>密钥分层</strong>：PMK → PTK → TK</li>
                        <li><strong>每次握手生成新密钥</strong>：前向安全性</li>
                    </ul>
                    
                    <h4>安全设计原则</h4>
                    <ul>
                        <li>不要自己设计加密算法</li>
                        <li>充分的安全审计和公开分析</li>
                        <li>为未来的计算能力预留安全余量</li>
                        <li>假设攻击者能看到所有通信内容</li>
                    </ul>
                """,
                key_points=[
                    "WEP不安全，立即升级到WPA2/WPA3",
                    "IV空间不足是核心问题之一",
                    "加密+完整性校验需要同时保证",
                    "安全需要公开审计和不断演进",
                ]
            ),
        ]

    def start_practice(self, wep_key: str, ssid: str = "WEP-Learning-Net") -> Dict:
        """开始WEP破解练习"""
        self.started = True
        self.completed = False
        self.cracked = False
        self.ssid = ssid
        self.wep_key = wep_key
        self.key_length = len(wep_key)
        self.bssid = self._generate_bssid()

        self.ivs_collected = 0
        self.weak_ivs_collected = 0
        self.iv_history = [0]
        self.weak_iv_history = [0]

        self.crack_progress = 0.0
        self.cracked_key_bytes = [None] * self.key_length
        self.crack_attempts = 0

        self._lesson_index = 0

        return {
            "success": True,
            "message": "WEP练习已启动",
            "network": {
                "ssid": self.ssid,
                "bssid": self.bssid,
                "encryption": "WEP",
                "key_length": self.key_length * 8,
            }
        }

    def _generate_bssid(self) -> str:
        """生成随机BSSID"""
        parts = [f"{random.randint(0x00, 0xff):02x}" for _ in range(6)]
        return ":".join(parts)

    def capture_ivs(self, count: int = 1000) -> Dict:
        """模拟捕获指定数量的IV"""
        if not self.started:
            return {"success": False, "error": "练习未开始，请先调用start_practice"}

        if self.completed:
            return {"success": False, "error": "练习已完成"}

        actual_count = min(count, self.TOTAL_IV_TARGET - self.ivs_collected)
        if actual_count <= 0:
            return {"success": False, "error": "已达到最大IV数量"}

        new_weak_count = 0
        for i in range(actual_count):
            self.ivs_collected += 1
            if random.random() < self.WEAK_IV_RATIO:
                self.weak_ivs_collected += 1
                new_weak_count += 1

        self.iv_history.append(self.ivs_collected)
        self.weak_iv_history.append(self.weak_ivs_collected)

        if len(self.iv_history) > 100:
            self.iv_history = self.iv_history[-100:]
            self.weak_iv_history = self.weak_iv_history[-100:]

        progress = (self.ivs_collected / self.TOTAL_IV_TARGET) * 100

        return {
            "success": True,
            "ivs_captured": actual_count,
            "new_weak_ivs": new_weak_count,
            "total_ivs": self.ivs_collected,
            "total_weak_ivs": self.weak_ivs_collected,
            "progress_percent": round(progress, 2),
            "can_crack": self.ivs_collected >= 10000,
        }

    def get_progress(self) -> Dict:
        """获取当前进度"""
        return {
            "started": self.started,
            "completed": self.completed,
            "cracked": self.cracked,
            "ssid": self.ssid,
            "bssid": self.bssid,
            "key_length": self.key_length,
            "ivs_collected": self.ivs_collected,
            "weak_ivs_collected": self.weak_ivs_collected,
            "total_target": self.TOTAL_IV_TARGET,
            "iv_progress_percent": round((self.ivs_collected / self.TOTAL_IV_TARGET) * 100, 2),
            "crack_progress_percent": round(self.crack_progress, 2),
            "cracked_key_bytes": self.cracked_key_bytes,
            "crack_attempts": self.crack_attempts,
            "iv_history": self.iv_history[-50:],
            "weak_iv_history": self.weak_iv_history[-50:],
        }

    def get_crack_attempt(self) -> Dict:
        """尝试破解（教学演示）"""
        if not self.started:
            return {"success": False, "error": "练习未开始"}

        if self.cracked:
            return {
                "success": True,
                "already_cracked": True,
                "wep_key": self.wep_key,
                "message": "密钥已破解"
            }

        if self.ivs_collected < 5000:
            return {
                "success": False,
                "error": "IV数量不足，至少需要5000个IV才能开始破解",
                "current_ivs": self.ivs_collected,
                "required_ivs": 5000
            }

        self.crack_attempts += 1

        base_chance = min(0.95, self.ivs_collected / 40000)
        success = random.random() < base_chance

        if success or self.ivs_collected >= self.TOTAL_IV_TARGET:
            self.cracked = True
            self.completed = True
            self.crack_progress = 100.0
            for i in range(self.key_length):
                self.cracked_key_bytes[i] = self.wep_key[i]

            return {
                "success": True,
                "cracked": True,
                "wep_key": self.wep_key,
                "crack_attempts": self.crack_attempts,
                "ivs_used": self.ivs_collected,
                "message": "恭喜！WEP密钥已成功破解（教学演示）",
                "crack_steps": self._generate_crack_steps()
            }
        else:
            cracked_count = min(
                self.key_length,
                int((self.ivs_collected / 40000) * self.key_length) + random.randint(0, 1)
            )
            for i in range(cracked_count):
                if self.cracked_key_bytes[i] is None:
                    if random.random() < 0.7:
                        self.cracked_key_bytes[i] = self.wep_key[i]

            known_bytes = sum(1 for b in self.cracked_key_bytes if b is not None)
            self.crack_progress = (known_bytes / self.key_length) * 100

            return {
                "success": True,
                "cracked": False,
                "crack_attempts": self.crack_attempts,
                "crack_progress_percent": round(self.crack_progress, 2),
                "cracked_key_bytes": self.cracked_key_bytes,
                "message": f"正在破解中... 已还原 {known_bytes}/{self.key_length} 个密钥字节，继续收集更多IV",
                "hint": "收集更多IV可以提高破解成功率",
                "crack_steps": self._generate_crack_steps()
            }

    def _generate_crack_steps(self) -> List[Dict]:
        """生成破解步骤详情（教学演示）"""
        steps = []
        known_bytes = sum(1 for b in self.cracked_key_bytes if b is not None)

        steps.append({
            "step": 1,
            "name": "IV数据预处理",
            "status": "completed",
            "description": f"对 {self.ivs_collected} 个IV进行排序和筛选"
        })

        steps.append({
            "step": 2,
            "name": "弱IV提取",
            "status": "completed",
            "description": f"提取出 {self.weak_ivs_collected} 个弱IV用于FMS攻击"
        })

        steps.append({
            "step": 3,
            "name": "密钥字节投票",
            "status": "active" if not self.cracked else "completed",
            "description": f"使用KoreK算法对每个密钥字节进行统计投票"
        })

        steps.append({
            "step": 4,
            "name": "逐字节还原",
            "status": "pending" if known_bytes == 0 else ("active" if not self.cracked else "completed"),
            "description": f"已还原 {known_bytes}/{self.key_length} 个密钥字节"
        })

        steps.append({
            "step": 5,
            "name": "密钥验证",
            "status": "completed" if self.cracked else "pending",
            "description": "用还原的密钥解密数据包验证正确性"
        })

        return steps

    def get_lesson_content(self) -> Dict:
        """获取当前步骤的教学内容"""
        if not self.lessons:
            return {"success": False, "error": "没有教学内容"}

        current_lesson = self.lessons[self._lesson_index]

        return {
            "success": True,
            "current_index": self._lesson_index,
            "total_lessons": len(self.lessons),
            "lesson": {
                "id": current_lesson.lesson_id,
                "title": current_lesson.title,
                "description": current_lesson.description,
                "content": current_lesson.content,
                "key_points": current_lesson.key_points,
                "warning": current_lesson.warning,
            }
        }

    def next_lesson(self) -> Dict:
        """下一课"""
        if self._lesson_index < len(self.lessons) - 1:
            self._lesson_index += 1
        return self.get_lesson_content()

    def prev_lesson(self) -> Dict:
        """上一课"""
        if self._lesson_index > 0:
            self._lesson_index -= 1
        return self.get_lesson_content()

    def go_to_lesson(self, lesson_id: str) -> Dict:
        """跳转到指定课程"""
        for i, lesson in enumerate(self.lessons):
            if lesson.lesson_id == lesson_id:
                self._lesson_index = i
                break
        return self.get_lesson_content()

    def get_all_lessons(self) -> List[Dict]:
        """获取所有课程列表"""
        return [
            {
                "id": lesson.lesson_id,
                "title": lesson.title,
                "description": lesson.description,
                "index": i,
            }
            for i, lesson in enumerate(self.lessons)
        ]

    def capture_ivs_phase(self, phase: str, count: int) -> Dict:
        """分阶段IV收集模拟（不同速率）"""
        if not self.started:
            return {"success": False, "error": "练习未开始，请先调用start_practice"}

        phase_rates = {
            "slow": {"delay_ms": 100, "weak_ratio": 0.03, "label": "慢速收集（被动监听）"},
            "medium": {"delay_ms": 30, "weak_ratio": 0.05, "label": "中速收集（正常流量）"},
            "fast": {"delay_ms": 10, "weak_ratio": 0.08, "label": "快速收集（高流量网络）"},
        }

        if phase not in phase_rates:
            return {"success": False, "error": f"无效阶段: {phase}，可选: slow, medium, fast"}

        actual_count = min(count, self.TOTAL_IV_TARGET - self.ivs_collected)
        if actual_count <= 0:
            return {"success": False, "error": "已达到最大IV数量"}

        config = phase_rates[phase]
        new_weak_count = 0

        for i in range(actual_count):
            self.ivs_collected += 1
            if random.random() < config["weak_ratio"]:
                self.weak_ivs_collected += 1
                new_weak_count += 1

        self.iv_history.append(self.ivs_collected)
        self.weak_iv_history.append(self.weak_ivs_collected)

        if len(self.iv_history) > 100:
            self.iv_history = self.iv_history[-100:]
            self.weak_iv_history = self.weak_iv_history[-100:]

        progress = (self.ivs_collected / self.TOTAL_IV_TARGET) * 100

        return {
            "success": True,
            "phase": phase,
            "phase_label": config["label"],
            "ivs_captured": actual_count,
            "new_weak_ivs": new_weak_count,
            "total_ivs": self.ivs_collected,
            "total_weak_ivs": self.weak_ivs_collected,
            "progress_percent": round(progress, 2),
            "can_crack": self.ivs_collected >= 10000,
            "estimated_time_remaining": self._estimate_remaining_time(phase, actual_count),
        }

    def _estimate_remaining_time(self, phase: str, recent_count: int) -> float:
        """估算剩余时间（秒）"""
        remaining = self.TOTAL_IV_TARGET - self.ivs_collected
        if recent_count == 0:
            return 0
        phase_speeds = {"slow": 10, "medium": 33, "fast": 100}
        speed = phase_speeds.get(phase, 20)
        return round(remaining / speed, 1)

    def get_fms_attack_detail(self) -> Dict:
        """获取FMS攻击逐字节破解详情"""
        if not self.started:
            return {"success": False, "error": "练习未开始"}

        bytes_detail = []
        known_bytes = sum(1 for b in self.cracked_key_bytes if b is not None)

        for i in range(self.key_length):
            byte_char = self.wep_key[i]
            byte_val = ord(byte_char)

            if self.cracked_key_bytes[i] is not None:
                status = "cracked"
                top_candidate = byte_val
                confidence = 95 + random.random() * 5
            elif i < known_bytes + 1:
                status = "in_progress"
                top_candidate = byte_val if random.random() > 0.3 else random.randint(0, 255)
                confidence = 40 + random.random() * 40
            else:
                status = "pending"
                top_candidate = None
                confidence = 0

            votes = {}
            if status in ["cracked", "in_progress"]:
                for v in range(max(0, byte_val - 5), min(256, byte_val + 5)):
                    base = random.randint(5, 50)
                    if v == byte_val:
                        base += int(30 + confidence * 0.5)
                    votes[v] = base

            bytes_detail.append({
                "byte_index": i,
                "status": status,
                "actual_value": byte_val,
                "actual_char": byte_char,
                "top_candidate": top_candidate,
                "top_candidate_char": chr(top_candidate) if top_candidate else None,
                "confidence": round(confidence, 1),
                "votes": votes,
                "vote_count": len(votes),
            })

        return {
            "success": True,
            "key_length": self.key_length,
            "cracked_bytes": known_bytes,
            "bytes_detail": bytes_detail,
            "attack_method": "FMS + KoreK 混合攻击",
            "ivs_used": self.ivs_collected,
            "weak_ivs_used": self.weak_ivs_collected,
        }

    def get_weak_iv_visualization(self) -> Dict:
        """获取弱IV可视化数据"""
        weak_prefix_counts = {}
        for i in range(min(256, max(10, self.weak_ivs_collected // 5))):
            prefix = (i % 16)
            weak_prefix_counts[f"{prefix:02x}"] = random.randint(
                max(1, self.weak_ivs_collected // 50),
                max(2, self.weak_ivs_collected // 20)
            )

        iv_prefix_counts = {}
        for i in range(256):
            prefix = f"{i:02x}"
            iv_prefix_counts[prefix] = max(
                1,
                int(self.ivs_collected / 256 + random.randint(-50, 50))
            )

        return {
            "success": True,
            "total_ivs": self.ivs_collected,
            "total_weak_ivs": self.weak_ivs_collected,
            "weak_ratio": round(self.weak_ivs_collected / max(1, self.ivs_collected) * 100, 2),
            "weak_iv_distribution": weak_prefix_counts,
            "iv_prefix_counts": iv_prefix_counts,
            "first_byte_weak_pattern": "A+3 模式",
            "weak_iv_format": "(A+3, 255, X)",
        }

    def get_success_rate_curve(self) -> Dict:
        """获取破解成功率与IV数量关系曲线"""
        data_points = []
        thresholds = [1000, 5000, 10000, 20000, 30000, 40000, 50000]
        rates = [5, 15, 40, 70, 85, 95, 99]

        for iv_count, rate in zip(thresholds, rates):
            data_points.append({
                "iv_count": iv_count,
                "success_rate": rate,
                "label": f"{iv_count // 1000}K IVs"
            })

        return {
            "success": True,
            "data_points": data_points,
            "x_label": "IV数量",
            "y_label": "破解成功率(%)",
            "note": "基于PTW攻击算法的统计数据，实际成功率受网络环境影响",
        }

    def get_key_length_comparison(self) -> Dict:
        """获取不同密钥长度的破解时间对比"""
        comparisons = [
            {
                "key_length": 40,
                "key_label": "64位WEP（40位密钥）",
                "iv_required": 20000,
                "estimated_time": "约2-5分钟（高流量网络）",
                "difficulty": "极易",
                "description": "40位密钥长度太短，结合弱IV漏洞极易破解"
            },
            {
                "key_length": 104,
                "key_label": "128位WEP（104位密钥）",
                "iv_required": 40000,
                "estimated_time": "约10-30分钟（高流量网络）",
                "difficulty": "容易",
                "description": "虽然密钥更长，但算法漏洞相同，只需更多IV即可破解"
            },
            {
                "key_length": 128,
                "key_label": "152位WEP（128位密钥）",
                "iv_required": 60000,
                "estimated_time": "约30-60分钟（高流量网络）",
                "difficulty": "中等",
                "description": "更长的密钥需要更多IV，但原理相同，只是时间问题"
            },
        ]

        return {
            "success": True,
            "comparisons": comparisons,
            "conclusion": "无论密钥多长，WEP都不安全。根本缺陷在于RC4+IV的使用方式，而非密钥长度。",
        }

    def get_step_explanations(self) -> Dict:
        """获取各步骤的教学讲解"""
        return {
            "iv_collection": {
                "title": "步骤一：IV收集",
                "principle": """
                    <h4>什么是IV？为什么需要收集IV？</h4>
                    <p>IV（Initialization Vector，初始化向量）是WEP加密中与密钥一起使用的随机数。WEP使用24位IV，与密钥拼接后作为RC4的输入。</p>
                    
                    <h4>原理</h4>
                    <p>RC4是流密码算法，其输出完全由输入决定。如果两个数据包使用了相同的IV和密钥，它们的密钥流完全相同。通过收集足够多的IV，攻击者可以利用统计分析还原密钥。</p>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li>WEP IV长度：24位（约1600万个可能值）</li>
                        <li>繁忙网络中，IV每几小时就会重复一次</li>
                        <li>IV以明文形式发送，攻击者可以直接获取</li>
                        <li>每256个IV中约有1个是"弱IV"，会泄露密钥信息</li>
                    </ul>
                """,
                "defense": """
                    <h4>防御措施</h4>
                    <ol>
                        <li><strong>升级到WPA2/WPA3</strong>：这是最根本的解决办法</li>
                        <li>增加IV长度：WPA使用48位TSC（相当于IV）</li>
                        <li>每包使用不同密钥：通过TKIP或CCMP实现</li>
                        <li>定期更换密钥：减少被破解的时间窗口</li>
                    </ol>
                """,
            },
            "weak_iv_detection": {
                "title": "步骤二：弱IV检测",
                "principle": """
                    <h4>什么是弱IV？</h4>
                    <p>弱IV（Weak IVs）是指那些会导致RC4密钥流产生可预测偏差的特定IV值。FMS攻击（Fluhrer-Mantin-Shamir）发现了这一漏洞。</p>
                    
                    <h4>技术原理</h4>
                    <p>当IV的前两个字节为 (A+3, 255) 格式时（A是已破解的密钥字节数），经过KSA的前A+3轮后，S盒会处于特定状态，使得PRGA输出的第一个字节与第A+1个密钥字节高度相关。</p>
                    
                    <h4>弱IV格式详解</h4>
                    <ul>
                        <li>IV[0] = A + 3（A是已知密钥字节数）</li>
                        <li>IV[1] = 255（N-1）</li>
                        <li>IV[2] = 任意值</li>
                        <li>这类IV出现概率：约1/16777216（每个特定格式）</li>
                    </ul>
                    
                    <h4>为什么危险？</h4>
                    <p>通过收集大量弱IV，攻击者可以对每个可能的密钥字节值进行"投票"。正确的密钥字节值出现的概率会显著高于错误值，这就是统计攻击的基础。</p>
                """,
                "defense": """
                    <h4>防御措施</h4>
                    <ol>
                        <li><strong>升级到WPA2</strong>：使用CCMP（AES-CCM）而非RC4</li>
                        <li>TKIP的缓解：WPA的TKIP增加了每包密钥混合，大幅降低了弱IV风险</li>
                        <li>过滤弱IV：某些AP固件会主动避免使用已知的弱IV</li>
                        <li>但请注意：即使过滤弱IV，WEP仍然不安全，还有其他攻击方式</li>
                    </ol>
                """,
            },
            "fms_attack": {
                "title": "步骤三：FMS攻击与密钥还原",
                "principle": """
                    <h4>FMS攻击原理</h4>
                    <p>FMS攻击利用弱IV的统计特性，逐字节还原WEP密钥。攻击的核心思想是"投票机制"。</p>
                    
                    <h4>攻击步骤详解</h4>
                    <ol>
                        <li><strong>收集弱IV</strong>：捕获足够多的 (A+3, 255, X) 格式的IV</li>
                        <li><strong>计算密钥字节候选值</strong>：对每个弱IV，利用已知明文推算密钥字节的可能值</li>
                        <li><strong>投票统计</strong>：统计每个可能值出现的次数</li>
                        <li><strong>选出最高票</strong>：得票最高的值极大概率是正确的密钥字节</li>
                        <li><strong>下一字节</strong>：用已知的密钥字节继续找下一组弱IV</li>
                        <li><strong>重复</strong>：直到所有密钥字节都被还原</li>
                    </ol>
                    
                    <h4>技术细节</h4>
                    <ul>
                        <li>每个密钥字节需要约50-100个弱IV才能高置信度确定</li>
                        <li>总IV需求量：64位WEP约2万，128位WEP约4万</li>
                        <li>PTW攻击进一步优化：使用线性方程组，所需IV更少</li>
                        <li>KoreK攻击：使用更多种弱IV格式，提高效率</li>
                    </ul>
                """,
                "defense": """
                    <h4>防御措施</h4>
                    <ol>
                        <li><strong>立即升级到WPA2/WPA3</strong>：这是唯一有效的长期解决方案</li>
                        <li>不要依赖WEP密钥长度：128位WEP只是比64位多花一点时间，本质同样不安全</li>
                        <li>使用WPA3的SAE认证：抵御离线字典攻击</li>
                        <li>定期更换WiFi密码：降低被破解的风险窗口</li>
                    </ol>
                    
                    <h4>WPA2为什么安全？</h4>
                    <p>WPA2使用AES-CCMP加密，不再使用RC4算法。AES是经过严格密码分析的块密码，目前没有已知的有效攻击方式。只要密码足够强壮（12位以上混合字符），WPA2实际上是不可破解的。</p>
                """,
            },
            "key_verification": {
                "title": "步骤四：密钥验证",
                "principle": """
                    <h4>如何验证破解出的密钥？</h4>
                    <p>得到候选密钥后，需要验证它是否正确。常用的验证方法有以下几种：</p>
                    
                    <h4>验证方法</h4>
                    <ol>
                        <li><strong>解密验证</strong>：用候选密钥解密切换的数据包，检查CRC是否正确</li>
                        <li><strong>连接测试</strong>：尝试用该密钥连接AP，看是否能成功</li>
                        <li><strong>密钥调度验证</strong>：检查密钥是否能产生与捕获数据一致的密钥流</li>
                    </ol>
                    
                    <h4>为什么会破解失败？</h4>
                    <ul>
                        <li>IV数量不足：统计样本不够，投票结果偏差大</li>
                        <li>弱IV分布不均：某些字节的弱IV收集不足</li>
                        <li>网络流量混杂：干扰数据影响统计准确性</li>
                        <li>密钥不是ASCII：如果是十六进制密钥，破解结果可能不可打印</li>
                    </ul>
                    
                    <h4>提高成功率</h4>
                    <p>收集更多IV是提高成功率最直接的方法。一般来说：</p>
                    <ul>
                        <li>1万IV：约40%成功率</li>
                        <li>2万IV：约70%成功率</li>
                        <li>4万IV：约95%成功率</li>
                    </ul>
                """,
                "defense": """
                    <h4>防御思路</h4>
                    <p>对于网络管理员来说，检测WEP破解攻击非常困难，因为攻击者只是被动监听，不发送任何数据包。</p>
                    
                    <h4>可能的检测方法</h4>
                    <ul>
                        <li>监控异常大量的ARP请求（可能是注入攻击）</li>
                        <li>注意同一客户端的大量关联/解关联（可能是攻击）</li>
                        <li>使用无线入侵检测系统（WIDS）</li>
                    </ul>
                    
                    <p><strong>但最好的防御是：不要使用WEP！</strong></p>
                """,
            },
        }

    def get_progress(self, detail_level: str = "basic") -> Dict:
        """获取当前进度（支持渐进式信息展示）"""
        basic_info = {
            "started": self.started,
            "completed": self.completed,
            "cracked": self.cracked,
            "ssid": self.ssid,
            "ivs_collected": self.ivs_collected,
            "weak_ivs_collected": self.weak_ivs_collected,
            "iv_progress_percent": round((self.ivs_collected / self.TOTAL_IV_TARGET) * 100, 2),
            "crack_progress_percent": round(self.crack_progress, 2),
        }

        if detail_level == "basic":
            return basic_info

        detailed_info = {
            **basic_info,
            "bssid": self.bssid,
            "key_length": self.key_length,
            "total_target": self.TOTAL_IV_TARGET,
            "cracked_key_bytes": self.cracked_key_bytes,
            "crack_attempts": self.crack_attempts,
            "can_crack": self.ivs_collected >= 10000,
        }

        if detail_level == "detailed":
            return detailed_info

        full_info = {
            **detailed_info,
            "iv_history": self.iv_history[-50:],
            "weak_iv_history": self.weak_iv_history[-50:],
            "crack_steps": self._generate_crack_steps(),
        }

        return full_info

    def reset(self) -> Dict:
        """重置练习"""
        self.started = False
        self.completed = False
        self.cracked = False
        self.ssid = ""
        self.bssid = ""
        self.wep_key = ""
        self.key_length = 0
        self.ivs_collected = 0
        self.weak_ivs_collected = 0
        self.iv_history = []
        self.weak_iv_history = []
        self.crack_progress = 0.0
        self.cracked_key_bytes = []
        self.crack_attempts = 0
        self._lesson_index = 0

        return {"success": True, "message": "WEP练习已重置"}


_wep_practice_simulator = None


def get_wep_practice_simulator() -> WEPPracticeSimulator:
    """获取WEP练习模拟器单例"""
    global _wep_practice_simulator
    if _wep_practice_simulator is None:
        _wep_practice_simulator = WEPPracticeSimulator()
    return _wep_practice_simulator

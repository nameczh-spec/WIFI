"""
教学模式系统
提供全面的WiFi安全学习内容，包括加密原理、握手过程、漏洞分析等
所有内容仅供学习研究使用
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class LearningCategory(Enum):
    """学习类别"""
    ENCRYPTION_BASICS = "encryption_basics"  # 加密基础
    WEP = "wep"  # WEP加密
    WPA = "wpa"  # WPA/WPA2加密
    WPA3 = "wpa3"  # WPA3加密
    HANDSHAKE = "handshake"  # 握手过程
    VULNERABILITIES = "vulnerabilities"  # 漏洞分析
    SECURITY_PRACTICES = "security_practices"  # 安全实践


class DifficultyLevel(Enum):
    """难度级别"""
    BEGINNER = "beginner"  # 入门
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级


@dataclass
class LearningStep:
    """学习步骤"""
    step_id: str
    title: str
    content: str  # 支持HTML格式
    code_example: Optional[str] = None
    illustration: Optional[str] = None  # 示意图描述
    key_points: List[str] = field(default_factory=list)
    warning: Optional[str] = None  # 安全提示


@dataclass
class LearningModule:
    """学习模块"""
    module_id: str
    category: LearningCategory
    title: str
    description: str
    difficulty: DifficultyLevel
    estimated_time: int  # 分钟
    steps: List[LearningStep] = field(default_factory=list)
    quiz: List[Dict] = field(default_factory=list)
    is_practical: bool = False  # 是否包含实践练习
    prerequisites: List[str] = field(default_factory=list)  # 前置模块


class TeachingSystem:
    """
    教学系统
    管理所有学习内容和学习进度
    """

    def __init__(self):
        self.modules: Dict[str, LearningModule] = {}
        self.progress: Dict[str, int] = {}  # module_id -> 当前步骤索引
        self._init_modules()

    def _init_modules(self):
        """初始化所有学习模块"""
        self._add_module(self._create_encryption_basics_module())
        self._add_module(self._create_wep_module())
        self._add_module(self._create_wpa_module())
        self._add_module(self._create_wpa3_module())
        self._add_module(self._create_vulnerabilities_module())
        self._add_module(self._create_security_practices_module())

    def _add_module(self, module: LearningModule):
        self.modules[module.module_id] = module

    def get_all_modules(self) -> List[LearningModule]:
        """获取所有学习模块"""
        return list(self.modules.values())

    def get_module_by_category(self, category: LearningCategory) -> List[LearningModule]:
        """按类别获取模块"""
        return [m for m in self.modules.values() if m.category == category]

    def get_module(self, module_id: str) -> Optional[LearningModule]:
        """获取指定模块"""
        return self.modules.get(module_id)

    def get_progress(self, module_id: str) -> int:
        """获取学习进度"""
        return self.progress.get(module_id, 0)

    def set_progress(self, module_id: str, step_index: int):
        """设置学习进度"""
        self.progress[module_id] = step_index

    def _create_encryption_basics_module(self) -> LearningModule:
        """创建加密基础模块"""
        steps = [
            LearningStep(
                step_id="basics-1",
                title="什么是加密？",
                content="""
                    <p>加密是将信息转换为不可读形式的过程，只有授权方才能将其恢复为可读形式。</p>
                    <p>在WiFi通信中，加密确保了数据在无线传输过程中不被第三方窃取或篡改。</p>
                    <h4>加密的基本概念：</h4>
                    <ul>
                        <li><strong>明文 (Plaintext)</strong>：原始的、可读的数据</li>
                        <li><strong>密文 (Ciphertext)</strong>：加密后的数据</li>
                        <li><strong>密钥 (Key)</strong>：用于加密和解密的秘密信息</li>
                        <li><strong>加密算法</strong>：执行加密/解密的数学方法</li>
                    </ul>
                """,
                key_points=[
                    "加密保护数据的机密性",
                    "密钥是加密系统的核心",
                    "没有正确密钥就无法解密",
                ],
                warning="⚠ 本教程仅供学习研究，请勿用于未授权的网络。"
            ),
            LearningStep(
                step_id="basics-2",
                title="对称加密 vs 非对称加密",
                content="""
                    <h3>对称加密</h3>
                    <p>加密和解密使用<strong>相同的密钥</strong>。</p>
                    <p>WiFi主要使用对称加密，因为它速度快、效率高。</p>
                    <p>常见算法：AES、RC4、DES</p>
                    
                    <h3>非对称加密</h3>
                    <p>使用<strong>一对密钥</strong>：公钥和私钥。</p>
                    <p>公钥加密的数据只能用私钥解密，反之亦然。</p>
                    <p>常用于密钥交换和数字签名。</p>
                    <p>常见算法：RSA、ECC</p>
                    
                    <h4>为什么WiFi不用非对称加密传输数据？</h4>
                    <p>非对称加密计算量大、速度慢，不适合高速数据传输。WiFi通常先用非对称加密交换对称密钥，然后用对称加密传输数据。</p>
                """,
                code_example="""
# 简单的对称加密示例（凯撒密码）
def caesar_encrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            shifted = ord(char) + shift
            if char.isupper():
                result += chr((shifted - 65) % 26 + 65)
            else:
                result += chr((shifted - 97) % 26 + 97)
        else:
            result += char
    return result

# 加密
encrypted = caesar_encrypt("Hello WiFi", 3)
print("密文:", encrypted)  # Khoor ZLIl

# 解密
decrypted = caesar_encrypt(encrypted, -3)
print("明文:", decrypted)  # Hello WiFi
                """,
                key_points=[
                    "对称加密：加密解密用同一个密钥，速度快",
                    "非对称加密：公钥私钥配对，用于密钥交换",
                    "WiFi结合使用两者：非对称交换密钥，对称传输数据",
                ]
            ),
            LearningStep(
                step_id="basics-3",
                title="流密码 vs 分组密码",
                content="""
                    <h3>流密码 (Stream Cipher)</h3>
                    <p>逐位/逐字节加密数据流，像水流一样连续处理。</p>
                    <p>特点：速度快、硬件实现简单</p>
                    <p>代表：RC4（用于WEP和早期WPA）</p>
                    
                    <h3>分组密码 (Block Cipher)</h3>
                    <p>将数据分成固定大小的块（如128位），逐块加密。</p>
                    <p>特点：安全性更高，但模式选择很重要</p>
                    <p>代表：AES（用于WPA2/WPA3）</p>
                    
                    <h4>工作模式</h4>
                    <p>分组密码有多种工作模式，决定了如何处理多个数据块：</p>
                    <ul>
                        <li><strong>ECB</strong>：最简单，但不安全</li>
                        <li><strong>CBC</strong>：需要初始化向量(IV)</li>
                        <li><strong>CTR</strong>：计数器模式，像流密码</li>
                        <li><strong>GCM</strong>：认证加密，同时提供机密性和完整性</li>
                    </ul>
                """,
                key_points=[
                    "流密码：逐位加密，速度快（RC4）",
                    "分组密码：逐块加密，更安全（AES）",
                    "AES-GCM是当前推荐的模式（WPA2 CCMP, WPA3）",
                ]
            ),
            LearningStep(
                step_id="basics-4",
                title="哈希函数与消息认证",
                content="""
                    <h3>哈希函数</h3>
                    <p>将任意长度的数据转换为固定长度的"指纹"。</p>
                    <p>特点：单向不可逆、雪崩效应（微小输入变化导致输出巨变）</p>
                    <p>常见算法：MD5（已不安全）、SHA-1（已不安全）、SHA-256</p>
                    
                    <h3>消息认证码 (MAC)</h3>
                    <p>用于验证消息的完整性和来源真实性。</p>
                    <p>HMAC：基于哈希的消息认证码</p>
                    
                    <h3>为什么需要认证？</h3>
                    <p>只有加密不够！攻击者可能：</p>
                    <ul>
                        <li>篡改加密后的数据（破坏完整性）</li>
                        <li>重放旧的数据包（重放攻击）</li>
                        <li>伪造数据包（欺骗身份）</li>
                    </ul>
                    <p>好的安全协议同时提供<strong>机密性 + 完整性 + 认证</strong>。</p>
                """,
                code_example="""
import hashlib

# SHA-256哈希示例
def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

# 原文
text1 = "WiFi Security"
hash1 = sha256_hash(text1)
print(f"原文: {text1}")
print(f"哈希: {hash1}")

# 微小变化
text2 = "WiFi security"  # s小写
hash2 = sha256_hash(text2)
print(f"\\n变化后: {text2}")
print(f"哈希: {hash2}")
print(f"完全不同的哈希值: {hash1 != hash2}")
                """,
                key_points=[
                    "哈希函数：单向、不可逆、雪崩效应",
                    "HMAC：验证消息完整性和来源",
                    "安全需要：机密性 + 完整性 + 认证（CIA三要素）",
                ]
            ),
        ]

        return LearningModule(
            module_id="encryption-basics",
            category=LearningCategory.ENCRYPTION_BASICS,
            title="加密基础入门",
            description="学习加密的基本概念、对称与非对称加密、流密码与分组密码、哈希函数等基础知识",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_time=20,
            steps=steps,
            quiz=[
                {
                    "question": "对称加密和非对称加密的主要区别是什么？",
                    "options": [
                        "对称加密更快",
                        "对称加密使用同一个密钥加密解密，非对称使用密钥对",
                        "非对称加密更老",
                        "对称加密只能加密文本"
                    ],
                    "correct": 1,
                    "explanation": "对称加密使用单个密钥，非对称使用公钥+私钥的密钥对。"
                },
                {
                    "question": "WiFi为什么主要使用对称加密传输数据？",
                    "options": [
                        "更安全",
                        "速度更快，效率更高",
                        "密钥更长",
                        "不需要密钥"
                    ],
                    "correct": 1,
                    "explanation": "对称加密计算量小、速度快，适合高速数据传输。"
                },
            ]
        )

    def _create_wep_module(self) -> LearningModule:
        """创建WEP模块"""
        steps = [
            LearningStep(
                step_id="wep-1",
                title="WEP简介",
                content="""
                    <h3>什么是WEP？</h3>
                    <p>WEP (Wired Equivalent Privacy) 是最早的WiFi加密标准，于1997年发布。</p>
                    <p>设计目标是提供与有线网络相当的安全性。</p>
                    
                    <h3>WEP的基本参数</h3>
                    <ul>
                        <li><strong>加密算法</strong>：RC4流密码</li>
                        <li><strong>密钥长度</strong>：40位（64位WEP）或104位（128位WEP）</li>
                        <li><strong>IV长度</strong>：24位（与密钥拼接使用）</li>
                        <li><strong>完整性校验</strong>：CRC-32（非常弱）</li>
                    </ul>
                    
                    <h3>WEP为什么不安全？</h3>
                    <p>WEP存在严重的设计缺陷，在2001年就被攻破。现在几分钟内就能破解WEP密码。</p>
                    <p>主要问题：IV空间太小、ICV完整性不足、密钥复用等。</p>
                """,
                key_points=[
                    "WEP使用RC4流密码 + 24位IV",
                    "WEP已被证明完全不安全",
                    "几分钟内即可破解WEP密码",
                ],
                warning="⚠ 学习WEP的目的是了解其安全缺陷，避免重蹈覆辙。绝不对未授权网络使用这些知识。"
            ),
            LearningStep(
                step_id="wep-2",
                title="WEP加密过程",
                content="""
                    <h3>WEP加密流程</h3>
                    <ol>
                        <li>生成24位初始化向量 (IV)</li>
                        <li>IV + 预共享密钥 作为RC4的种子密钥</li>
                        <li>RC4生成密钥流</li>
                        <li>明文数据 + ICV (CRC-32校验和) 与密钥流异或</li>
                        <li>IV + 密文 一起发送</li>
                    </ol>
                    
                    <h3>关键问题 #1：IV只有24位</h3>
                    <p>24位IV意味着只有约1680万个不同的IV值。</p>
                    <p>在繁忙的网络中，IV很快就会重复，导致密钥流重复使用。</p>
                    <p>当两个数据包使用相同的IV和密钥时，它们的密钥流相同！</p>
                    
                    <h3>关键问题 #2：CRC-32不提供认证</h3>
                    <p>CRC-32是为了检测传输错误，不是为了安全。</p>
                    <p>攻击者可以在不知道密钥的情况下修改密文，并同时修改ICV使其匹配。</p>
                """,
                code_example="""
# 简化的WEP加密演示
def rc4_keystream(key, length):
    # 简化的RC4密钥流生成（仅演示）
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    
    keystream = []
    i = j = 0
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream.append(S[(S[i] + S[j]) % 256])
    return keystream

def wep_encrypt(plaintext, key, iv):
    # IV + 密钥 作为种子
    full_key = iv + key
    keystream = rc4_keystream(full_key, len(plaintext))
    ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])
    return iv + ciphertext

# 相同IV + 相同密钥 = 相同密钥流！
key = b'secret'
iv = b'\\x00\\x01\\x02'

ct1 = wep_encrypt(b'Hello', key, iv)
ct2 = wep_encrypt(b'World', key, iv)

print("相同IV意味着相同密钥流！")
print("攻击者可以通过两个密文推导出明文的关系")
                """,
                key_points=[
                    "IV+密钥作为RC4种子",
                    "24位IV很快耗尽导致重复",
                    "相同IV+密钥产生相同密钥流",
                    "CRC-32不能防止篡改",
                ]
            ),
            LearningStep(
                step_id="wep-3",
                title="WEP攻击原理",
                content="""
                    <h3>已知的WEP攻击方法</h3>
                    
                    <h4>1. IV收集攻击 (FMS/KoreK攻击)</h4>
                    <p>收集大量不同IV的数据包，通过统计分析推断密钥。</p>
                    <p>经典的FMS攻击需要约100万个数据包。</p>
                    <p>KoreK攻击优化后只需要约10万个数据包。</p>
                    
                    <h4>2. Chop-Chop攻击</h4>
                    <p>逐字节解密数据包，不需要收集大量IV。</p>
                    <p>通过逐字节试探，利用ICV校验验证猜测。</p>
                    
                    <h4>3. 重放攻击</h4>
                    <p>因为WEP没有序列号和重放保护，攻击者可以截获数据包并重新发送。</p>
                    
                    <h4>4. 比特翻转攻击</h4>
                    <p>因为流密码的特性，可以在不知道明文的情况下翻转密文的特定位，同时修改ICV。</p>
                    
                    <h3>为什么WEP这么快就被破解？</h3>
                    <ol>
                        <li>IV太短（24位）→ 密钥流容易重复</li>
                        <li>RC4密钥调度算法有弱点 → 易受统计攻击</li>
                        <li>ICV只是CRC → 不能防止篡改</li>
                        <li>没有重放保护 → 数据包可以重复使用</li>
                        <li>没有密钥更新 → 长期使用同一密钥</li>
                    </ol>
                """,
                key_points=[
                    "FMS/KoreK：收集IV统计攻击",
                    "Chop-Chop：逐字节解密",
                    "主要原因：IV太短 + RC4弱点 + CRC不够安全",
                ],
                warning="⚠ 了解攻击原理是为了更好地防御。禁止对任何未授权网络使用攻击手段。"
            ),
            LearningStep(
                step_id="wep-4",
                title="从WEP的失败中学到什么",
                content="""
                    <h3>WEP给我们的教训</h3>
                    
                    <h4>1. 不要自己发明加密算法</h4>
                    <p>WEP的设计者们试图"优化"标准安全机制，结果引入了致命弱点。</p>
                    <p>始终使用经过广泛审查的标准算法和协议。</p>
                    
                    <h4>2. 密钥空间必须足够大</h4>
                    <p>24位IV在密码学上太小了。</p>
                    <p>现代加密通常使用128位以上的密钥和随机数。</p>
                    
                    <h4>3. 加密 ≠ 安全</h4>
                    <p>只有加密（机密性）是不够的，还需要：</p>
                    <ul>
                        <li><strong>完整性</strong>：数据没有被篡改</li>
                        <li><strong>认证</strong>：确认通信方身份</li>
                        <li><strong>重放保护</strong>：防止旧数据包被重用</li>
                    </ul>
                    
                    <h4>4. 安全协议需要不断升级</h4>
                    <p>没有永远安全的协议。</p>
                    <p>WPA → WPA2 → WPA3，安全标准在不断进化。</p>
                    
                    <h3>实践建议</h3>
                    <p>✅ 如果你的路由器还在用WEP，立即升级！</p>
                    <p>✅ 至少使用WPA2，推荐WPA3</p>
                    <p>✅ 使用长而复杂的WiFi密码</p>
                    <p>✅ 定期更新路由器固件</p>
                """,
                key_points=[
                    "不要自己造密码学轮子",
                    "密钥/IV空间必须足够大",
                    "安全需要CIA（机密性+完整性+可用性+认证）",
                    "从WEP升级到WPA2/WPA3",
                ]
            ),
        ]

        return LearningModule(
            module_id="wep-encryption",
            category=LearningCategory.WEP,
            title="WEP加密与漏洞",
            description="深入了解WEP加密原理、其设计缺陷以及被破解的原因",
            difficulty=DifficultyLevel.INTERMEDIATE,
            estimated_time=25,
            steps=steps,
            is_practical=True,
            prerequisites=["encryption-basics"],
            quiz=[
                {
                    "question": "WEP使用的加密算法是什么？",
                    "options": ["AES", "RC4", "RSA", "DES"],
                    "correct": 1,
                    "explanation": "WEP使用RC4流密码进行加密。"
                },
                {
                    "question": "WEP的IV（初始化向量）长度是多少？",
                    "options": ["128位", "64位", "24位", "48位"],
                    "correct": 2,
                    "explanation": "WEP只有24位IV，这是其主要弱点之一。"
                },
            ]
        )

    def _create_wpa_module(self) -> LearningModule:
        """创建WPA/WPA2模块"""
        steps = [
            LearningStep(
                step_id="wpa-1",
                title="WPA/WPA2简介",
                content="""
                    <h3>WPA - WiFi Protected Access</h3>
                    <p>WPA是WiFi联盟在2003年推出的临时解决方案，用于替代WEP。</p>
                    <p>它可以在原有硬件上通过固件升级实现。</p>
                    
                    <h3>WPA2 - IEEE 802.11i</h3>
                    <p>2004年正式发布的完整标准。</p>
                    <p>使用AES加密替代RC4，安全性大幅提升。</p>
                    
                    <h3>WPA/WPA2的两种模式</h3>
                    <ul>
                        <li><strong>个人模式 (PSK)</strong>：预共享密钥，家庭/小型网络使用</li>
                        <li><strong>企业模式 (802.1X)</strong>：结合RADIUS服务器，企业级使用</li>
                    </ul>
                    
                    <h3>WPA vs WPA2 核心区别</h3>
                    <table>
                        <tr><th>特性</th><th>WPA (TKIP)</th><th>WPA2 (CCMP)</th></tr>
                        <tr><td>加密算法</td><td>RC4 (TKIP包装)</td><td>AES</td></tr>
                        <tr><td>完整性</td><td>Michael MIC</td><td>CCM (CBC-MAC)</td></tr>
                        <tr><td>密钥管理</td><td>48位TSC + 重新生成</td><td>48位PN + AES密钥派生</td></tr>
                    </table>
                """,
                key_points=[
                    "WPA是过渡方案，WPA2是完整标准",
                    "WPA用TKIP(RC4)，WPA2用CCMP(AES)",
                    "PSK个人模式 vs 企业模式(802.1X)",
                ]
            ),
            LearningStep(
                step_id="wpa-2",
                title="四次握手过程",
                content="""
                    <h3>WPA/WPA2的四次握手</h3>
                    <p>四次握手是客户端连接加密WiFi时的密钥协商过程。</p>
                    <p>目的是安全地生成PTK（成对临时密钥）并验证双方都有正确的密码。</p>
                    
                    <h3>密钥层次结构</h3>
                    <ol>
                        <li><strong>PSK/PMK</strong>：预共享密钥 = 密码哈希生成的主密钥</li>
                        <li><strong>PTK</strong>：成对临时密钥（从PMK+随机数派生）</li>
                        <li><strong>GTK</strong>：组临时密钥（广播/组播加密）</li>
                        <li><strong>TK</strong>：临时密钥（用于实际数据加密）</li>
                    </ol>
                    
                    <h3>四次握手步骤</h3>
                    <p><strong>消息1：AP → Client</strong> (ANonce)</p>
                    <p>AP生成随机数ANonce，发送给客户端。</p>
                    
                    <p><strong>消息2：Client → AP</strong> (SNonce + RSN IE + MIC)</p>
                    <p>客户端生成SNonce，计算PTK，发送SNonce和MIC（消息完整性校验）。</p>
                    
                    <p><strong>消息3：AP → Client</strong> (GTK + MIC + Install)</p>
                    <p>AP验证MIC，确认客户端有正确密码。发送GTK给客户端。</p>
                    
                    <p><strong>消息4：Client → AP</strong> (ACK)</p>
                    <p>客户端确认收到GTK，准备安装密钥。握手完成！</p>
                """,
                key_points=[
                    "四次握手用于验证密码并生成会话密钥",
                    "PMK → PTK → TK 密钥层次结构",
                    "握手包不包含密码本身，但可以用来破解",
                ]
            ),
            LearningStep(
                step_id="wpa-3",
                title="TKIP vs CCMP",
                content="""
                    <h3>TKIP - 临时密钥完整性协议</h3>
                    <p>WPA的加密方案，为了兼容旧硬件而设计。</p>
                    
                    <h4>TKIP对WEP的改进：</h4>
                    <ul>
                        <li><strong>48位序列号(TSC)</strong>：替代24位IV，大大增加空间</li>
                        <li><strong>每包密钥混合</strong>：每个数据包使用不同的密钥</li>
                        <li><strong>Michael MIC</strong>：比CRC-32更强的完整性校验</li>
                        <li><strong>密钥更新</strong>：定期重新生成密钥</li>
                    </ul>
                    
                    <p>但TKIP仍然基于RC4，最终也被发现存在漏洞（如Beck-Tews攻击）。</p>
                    
                    <h3>CCMP - 计数器模式密码块链消息完整码协议</h3>
                    <p>WPA2的标准加密方案，基于AES。</p>
                    
                    <h4>CCMP的组成：</h4>
                    <ul>
                        <li><strong>CTR模式</strong>：AES计数器模式提供机密性</li>
                        <li><strong>CBC-MAC</strong>：密码块链消息认证码提供完整性</li>
                        <li><strong>48位PN (Packet Number)</strong>：序列号，防重放</li>
                    </ul>
                    
                    <p>CCMP同时提供机密性、完整性、认证和重放保护。</p>
                """,
                key_points=[
                    "TKIP = RC4 + MIC + 48位TSC（过渡方案）",
                    "CCMP = AES-CTR + CBC-MAC（标准方案）",
                    "CCMP同时提供CIA三要素",
                ]
            ),
            LearningStep(
                step_id="wpa-4",
                title="WPA2的弱点",
                content="""
                    <h3>WPA2并非完美无缺</h3>
                    <p>虽然WPA2比WEP安全得多，但仍存在一些已知问题。</p>
                    
                    <h4>1. KRACK攻击 (2017)</h4>
                    <p>密钥重装攻击，利用WPA2协议的设计缺陷。</p>
                    <p>攻击者可以强制客户端重装相同密钥，从而解密流量。</p>
                    <p>影响：几乎所有WPA2设备都受影响，但需要物理 proximity。</p>
                    <p>防护：更新设备固件，WPA3更安全。</p>
                    
                    <h4>2. PMKID攻击 (2018)</h4>
                    <p>利用漫游功能中的PMKID字段，不需要完整握手就能破解。</p>
                    <p>只需一个数据包即可离线破解PSK。</p>
                    <p>影响：支持802.11r快速漫游的路由器。</p>
                    
                    <h4>3. 弱密码攻击</h4>
                    <p>最常见的攻击方式：字典攻击/暴力破解。</p>
                    <p>如果密码强度不够，拿到握手包后可以离线破解。</p>
                    <p>防护：使用强密码（至少12位，包含大小写、数字、符号）。</p>
                    
                    <h4>4. WPS漏洞</h4>
                    <p>WiFi保护设置的PIN码容易被暴力破解。</p>
                    <p>防护：关闭WPS功能。</p>
                """,
                key_points=[
                    "KRACK：密钥重装攻击（协议缺陷）",
                    "PMKID：从单个数据包获取破解材料",
                    "最大威胁：弱密码（字典攻击）",
                    "建议：强密码 + 关闭WPS + 更新固件",
                ],
                warning="⚠ 了解弱点是为了更好地防护自己的网络。攻击未授权网络是违法的。"
            ),
        ]

        return LearningModule(
            module_id="wpa-encryption",
            category=LearningCategory.WPA,
            title="WPA/WPA2加密原理",
            description="学习WPA和WPA2的加密机制、四次握手、TKIP与CCMP对比，以及已知弱点",
            difficulty=DifficultyLevel.INTERMEDIATE,
            estimated_time=30,
            steps=steps,
            is_practical=True,
            prerequisites=["encryption-basics"],
            quiz=[
                {
                    "question": "WPA2默认使用的加密算法是什么？",
                    "options": ["RC4", "AES", "RSA", "DES"],
                    "correct": 1,
                    "explanation": "WPA2使用AES-CCMP作为标准加密方案。"
                },
                {
                    "question": "WPA四次握手的主要目的是什么？",
                    "options": [
                        "传输用户数据",
                        "验证密码并生成会话密钥",
                        "扫描可用网络",
                        "分配IP地址"
                    ],
                    "correct": 1,
                    "explanation": "四次握手用于验证双方都有正确密码，并协商生成会话密钥。"
                },
            ]
        )

    def _create_wpa3_module(self) -> LearningModule:
        """创建WPA3模块"""
        steps = [
            LearningStep(
                step_id="wpa3-1",
                title="WPA3简介",
                content="""
                    <h3>WPA3 - 第三代WiFi安全标准</h3>
                    <p>WPA3是WiFi联盟在2018年发布的最新WiFi安全标准。</p>
                    <p>针对WPA2的已知弱点进行了全面升级。</p>
                    
                    <h3>WPA3的主要改进</h3>
                    <ul>
                        <li><strong>SAE握手</strong>：抵御离线字典攻击（即使密码弱也安全）</li>
                        <li><strong>192位安全套件</strong>：企业级增强加密</li>
                        <li><strong>前向保密</strong>：即使长期密钥泄露，过去的流量仍然安全</li>
                        <li><strong>简化的IoT安全</strong>：无屏幕设备也能安全配置</li>
                        <li><strong>更强的加密</strong>：AES-GCMP-256等</li>
                    </ul>
                    
                    <h3>WPA3 vs WPA2</h3>
                    <table>
                        <tr><th>特性</th><th>WPA2</th><th>WPA3</th></tr>
                        <tr><td>认证</td><td>四次握手 (PSK)</td><td>SAE (Dragonfly)</td></tr>
                        <tr><td>离线字典攻击</td><td>✓ 可攻击</td><td>✗ 防护</td></tr>
                        <tr><td>前向保密</td><td>✗ 无</td><td>✓ 有</td></tr>
                        <tr><td>最小加密</td><td>128位AES</td><td>128位CMP (个人)</td></tr>
                    </table>
                """,
                key_points=[
                    "WPA3是最新WiFi安全标准",
                    "SAE握手抵御离线字典攻击",
                    "前向保密保护历史数据",
                ]
            ),
            LearningStep(
                step_id="wpa3-2",
                title="SAE认证机制",
                content="""
                    <h3>SAE - 同步认证对等</h3>
                    <p>SAE (Simultaneous Authentication of Equals) 也叫"Dragonfly"握手。</p>
                    <p>基于密码认证的密钥交换协议，使用椭圆曲线密码学。</p>
                    
                    <h3>SAE如何抵御离线字典攻击？</h3>
                    <p>WPA2的问题：拿到握手包后，攻击者可以离线尝试无限次密码。</p>
                    <p>SAE的解决方案：每次握手都需要与AP交互，不能离线破解。</p>
                    <p>即使密码较弱，攻击者也只能在线猜测（会被发现和限制）。</p>
                    
                    <h3>SAE握手过程（简化）</h3>
                    <ol>
                        <li><strong>Commit</strong>：双方交换承诺值（不泄露密码）</li>
                        <li><strong>Confirm</strong>：双方确认密钥计算结果</li>
                    </ol>
                    
                    <p>整个过程中，不会泄露任何可以用来离线破解的信息。</p>
                    <p>同时还提供<strong>前向保密</strong>：每次会话密钥不同，即使密码泄露，之前的会话数据也无法解密。</p>
                """,
                key_points=[
                    "SAE = Dragonfly握手，基于椭圆曲线",
                    "抵御离线字典攻击（必须在线猜测）",
                    "前向保密：保护历史流量",
                ]
            ),
        ]

        return LearningModule(
            module_id="wpa3-encryption",
            category=LearningCategory.WPA3,
            title="WPA3加密原理",
            description="了解最新的WiFi安全标准WPA3，包括SAE认证和安全增强",
            difficulty=DifficultyLevel.ADVANCED,
            estimated_time=15,
            steps=steps,
            prerequisites=["wpa-encryption"],
            quiz=[
                {
                    "question": "WPA3相比WPA2最主要的安全改进是什么？",
                    "options": [
                        "更快的速度",
                        "SAE握手抵御离线字典攻击",
                        "更长的密码",
                        "更多的信道"
                    ],
                    "correct": 1,
                    "explanation": "SAE认证是WPA3的核心改进，有效抵御离线字典攻击。"
                },
            ]
        )

    def _create_vulnerabilities_module(self) -> LearningModule:
        """创建漏洞分析模块"""
        steps = [
            LearningStep(
                step_id="vuln-1",
                title="常见WiFi安全漏洞概览",
                content="""
                    <h3>WiFi安全威胁分类</h3>
                    
                    <h4>1. 加密协议漏洞</h4>
                    <ul>
                        <li>WEP：完全破解</li>
                        <li>WPA TKIP：已知弱点</li>
                        <li>WPA2：KRACK、PMKID等</li>
                    </ul>
                    
                    <h4>2. 配置漏洞</h4>
                    <ul>
                        <li>弱密码/默认密码</li>
                        <li>WPS PIN码漏洞</li>
                        <li>未启用加密（开放网络）</li>
                        <li>旧固件存在已知CVE</li>
                    </ul>
                    
                    <h4>3. 管理漏洞</h4>
                    <ul>
                        <li>管理界面弱密码</li>
                        <li>远程管理开启</li>
                        <li>UPnP不安全</li>
                    </ul>
                    
                    <h4>4. 社会工程攻击</h4>
                    <ul>
                        <li>邪恶双胞胎（伪造AP）</li>
                        <li>钓鱼页面</li>
                        <li>欺骗连接</li>
                    </ul>
                """,
                key_points=[
                    "漏洞来自多个层面：协议、配置、管理、社工",
                    "最常见的风险是弱密码和配置错误",
                    "保持固件更新很重要",
                ],
                warning="⚠ 了解漏洞是为了防护。攻击未授权网络或设备是违法的。"
            ),
            LearningStep(
                step_id="vuln-2",
                title="邪恶双胞胎攻击",
                content="""
                    <h3>什么是邪恶双胞胎 (Evil Twin)？</h3>
                    <p>攻击者设置一个与合法AP同名的伪造接入点。</p>
                    <p>用户不小心连接后，所有流量都经过攻击者，可以进行中间人攻击。</p>
                    
                    <h3>攻击过程</h3>
                    <ol>
                        <li>扫描周边，找到目标AP的SSID</li>
                        <li>设置同名的伪造AP（信号更强）</li>
                        <li>用户设备自动连接到信号更强的伪造AP</li>
                        <li>攻击者拦截所有流量</li>
                    </ol>
                    
                    <h3>常见攻击方式</h3>
                    <ul>
                        <li><strong>SSL剥离</strong>：把HTTPS降级为HTTP</li>
                        <li><strong>DNS劫持</strong>：跳转到钓鱼页面</li>
                        <li><strong>凭证窃取</strong>：抓取登录密码</li>
                    </ul>
                    
                    <h3>如何防范？</h3>
                    <ul>
                        <li>✅ 不要连接陌生的开放WiFi</li>
                        <li>✅ 使用VPN加密所有流量</li>
                        <li>✅ 注意HTTPS证书警告</li>
                        <li>✅ 关闭自动连接未知网络</li>
                        <li>✅ 使用企业级WiFi（有证书认证）</li>
                    </ul>
                """,
                key_points=[
                    "邪恶双胞胎：伪造同名AP，诱导连接",
                    "常见于公共场所（咖啡店、机场等）",
                    "防护：VPN + 检查HTTPS + 不连陌生WiFi",
                ],
                warning="⚠ 仅用于学习和防护自己的网络安全。"
            ),
            LearningStep(
                step_id="vuln-3",
                title="Karma攻击与自动连接",
                content="""
                    <h3>Karma攻击原理</h3>
                    <p>利用设备的"已知网络列表"进行欺骗。</p>
                    <p>手机/电脑会定期探测已保存的WiFi网络（发送Probe Request）。</p>
                    <p>攻击者回应这些探针请求，假装是目标网络。</p>
                    
                    <h3>攻击过程</h3>
                    <ol>
                        <li>攻击者监听WiFi探针请求</li>
                        <li>发现设备在寻找"Starbucks"等已知SSID</li>
                        <li>立即创建名为"Starbucks"的AP</li>
                        <li>设备自动连接</li>
                    </ol>
                    
                    <h3>哪些设备容易中招？</h3>
                    <ul>
                        <li>开启了自动连接的设备</li>
                        <li>保存了大量开放网络的设备</li>
                        <li>旧版本的操作系统</li>
                    </ul>
                    
                    <h3>如何防护？</h3>
                    <ul>
                        <li>✅ 关闭"自动连接"功能</li>
                        <li>✅ 定期清理不常用的已保存网络</li>
                        <li>✅ 使用随机MAC地址扫描</li>
                        <li>✅ 连接WiFi前确认合法性</li>
                    </ul>
                """,
                key_points=[
                    "Karma：利用设备的已知网络列表",
                    "设备主动寻找已保存的WiFi",
                    "防护：关闭自动连接 + 清理网络列表",
                ]
            ),
            LearningStep(
                step_id="vuln-4",
                title="Deauth攻击与防护",
                content="""
                    <h3>什么是Deauth攻击？</h3>
                    <p>Deauthentication（解除认证）帧是802.11管理帧的一种。</p>
                    <p>AP或客户端都可以发送Deauth来断开连接。</p>
                    <p>因为管理帧通常不加密也不认证，攻击者可以伪造Deauth帧。</p>
                    
                    <h3>攻击目的</h3>
                    <ul>
                        <li><strong>强制重连</strong>：获取WPA握手包</li>
                        <li><strong>拒绝服务</strong>：让目标无法使用网络</li>
                        <li><strong>配合其他攻击</strong>：比如邪恶双胞胎</li>
                    </ul>
                    
                    <h3>为什么管理帧不认证？</h3>
                    <p>历史原因：早期WiFi标准认为管理帧不需要认证。</p>
                    <p>802.11w (PMF - Protected Management Frames) 解决了这个问题。</p>
                    
                    <h3>防护方法</h3>
                    <ul>
                        <li>✅ 启用802.11w (PMF) 保护管理帧</li>
                        <li>✅ 使用5GHz频段（更难干扰）</li>
                        <li>✅ 路由器检测并防御Deauth洪水</li>
                        <li>✅ WPA3默认要求PMF</li>
                    </ul>
                """,
                key_points=[
                    "Deauth：伪造解除认证帧，强制断开连接",
                    "用于抓取握手包或DoS攻击",
                    "防护：启用PMF (802.11w)",
                ],
                warning="⚠ 发送Deauth帧干扰他人网络是违法行为。"
            ),
        ]

        return LearningModule(
            module_id="vulnerabilities",
            category=LearningCategory.VULNERABILITIES,
            title="漏洞分析与攻击类型",
            description="了解各类WiFi安全漏洞和攻击方式，学习如何防护",
            difficulty=DifficultyLevel.INTERMEDIATE,
            estimated_time=25,
            steps=steps,
            is_practical=True,
            prerequisites=["wpa-encryption"],
            quiz=[
                {
                    "question": "邪恶双胞胎攻击主要利用什么？",
                    "options": [
                        "加密算法漏洞",
                        "用户误连伪造的同名AP",
                        "路由器后门",
                        "弱密码"
                    ],
                    "correct": 1,
                    "explanation": "邪恶双胞胎通过设置同名AP诱骗用户连接，进行中间人攻击。"
                },
                {
                    "question": "Deauth攻击的常见用途是什么？",
                    "options": [
                        "窃取WiFi密码",
                        "强制设备断开连接以获取握手包",
                        "提高WiFi速度",
                        "破解加密"
                    ],
                    "correct": 1,
                    "explanation": "Deauth攻击强制设备下线，设备重连时可以抓取握手包。"
                },
            ]
        )

    def _create_security_practices_module(self) -> LearningModule:
        """创建安全实践模块"""
        steps = [
            LearningStep(
                step_id="practice-1",
                title="路由器安全配置",
                content="""
                    <h3>路由器安全检查清单</h3>
                    
                    <h4>1. 加密方式</h4>
                    <ul>
                        <li>✅ 使用WPA3（如果设备支持）</li>
                        <li>✅ 至少使用WPA2-PSK (AES)</li>
                        <li>❌ 不要使用WEP</li>
                        <li>❌ 不要使用开放网络（无加密）</li>
                    </ul>
                    
                    <h4>2. 密码设置</h4>
                    <ul>
                        <li>✅ WiFi密码至少12位</li>
                        <li>✅ 包含大小写字母、数字、特殊字符</li>
                        <li>✅ 不使用生日、手机号等个人信息</li>
                        <li>✅ 不使用常见词汇</li>
                    </ul>
                    
                    <h4>3. 管理安全</h4>
                    <ul>
                        <li>✅ 修改默认管理员密码</li>
                        <li>✅ 关闭远程管理（WAN管理）</li>
                        <li>✅ 更新路由器固件</li>
                        <li>✅ 禁用UPnP（如非必要）</li>
                    </ul>
                    
                    <h4>4. 其他建议</h4>
                    <ul>
                        <li>✅ 关闭WPS功能</li>
                        <li>✅ 启用PMF (802.11w) 保护管理帧</li>
                        <li>✅ 隐藏SSID不能防黑，只是减少被发现概率</li>
                        <li>✅ MAC过滤也不是有效防护（容易伪造）</li>
                    </ul>
                """,
                key_points=[
                    "用WPA2/WPA3 + AES",
                    "强密码是基础",
                    "修改默认密码、更新固件",
                    "关闭WPS和UPnP",
                ]
            ),
            LearningStep(
                step_id="practice-2",
                title="公共WiFi安全使用指南",
                content="""
                    <h3>公共WiFi的风险</h3>
                    <p>咖啡店、机场、酒店的WiFi往往不安全。</p>
                    <ul>
                        <li>可能是邪恶双胞胎</li>
                        <li>流量可能被监听</li>
                        <li>可能存在中间人攻击</li>
                    </ul>
                    
                    <h3>安全使用公共WiFi的建议</h3>
                    
                    <h4>必须做的：</h4>
                    <ul>
                        <li>✅ <strong>使用VPN</strong>：加密所有流量，最有效的防护</li>
                        <li>✅ 只访问HTTPS网站</li>
                        <li>✅ 注意浏览器的证书警告</li>
                    </ul>
                    
                    <h4>不要做的：</h4>
                    <ul>
                        <li>❌ 不要进行网银/支付操作</li>
                        <li>❌ 不要登录重要账户</li>
                        <li>❌ 不要开启文件共享</li>
                        <li>❌ 不要自动连接未知WiFi</li>
                    </ul>
                    
                    <h4>判断WiFi是否安全：</h4>
                    <ul>
                        <li>确认是正规商家提供的</li>
                        <li>询问工作人员正确的SSID</li>
                        <li>选择需要密码的WPA/WPA2网络</li>
                        <li>避免"Free WiFi"等太泛的名字</li>
                    </ul>
                """,
                key_points=[
                    "公共WiFi不安全",
                    "VPN是最佳防护",
                    "避免敏感操作",
                    "注意验证网络合法性",
                ]
            ),
            LearningStep(
                step_id="practice-3",
                title="家庭网络安全加固",
                content="""
                    <h3>家庭网络安全加固清单</h3>
                    
                    <h4>1. 路由器安全</h4>
                    <ul>
                        <li>✅ WPA2-PSK (AES) 或 WPA3</li>
                        <li>✅ 强WiFi密码（≥12位）</li>
                        <li>✅ 强管理员密码</li>
                        <li>✅ 定期更新固件</li>
                        <li>✅ 关闭WPS</li>
                    </ul>
                    
                    <h4>2. 网络隔离</h4>
                    <ul>
                        <li>✅ 访客网络：给客人使用，隔离主网络</li>
                        <li>✅ IoT设备单独放一个VLAN/SSID</li>
                        <li>✅ 关闭不需要的端口映射</li>
                    </ul>
                    
                    <h4>3. 设备安全</h4>
                    <ul>
                        <li>✅ 所有设备安装安全更新</li>
                        <li>✅ 启用防火墙</li>
                        <li>✅ 安装杀毒软件（PC端）</li>
                    </ul>
                    
                    <h4>4. 安全习惯</h4>
                    <ul>
                        <li>✅ 不点击可疑链接</li>
                        <li>✅ 不下载不明来源的软件</li>
                        <li>✅ 使用密码管理器管理密码</li>
                        <li>✅ 重要账户启用双因素认证</li>
                    </ul>
                """,
                key_points=[
                    "路由器是网关，必须先加固",
                    "网络隔离：访客网、IoT网、主网分开",
                    "设备和人的安全意识同样重要",
                ]
            ),
        ]

        return LearningModule(
            module_id="security-practices",
            category=LearningCategory.SECURITY_PRACTICES,
            title="安全最佳实践",
            description="路由器安全配置、公共WiFi使用指南、家庭网络加固建议",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_time=20,
            steps=steps,
        )


# 创建全局教学系统实例
_teaching_system = None

def get_teaching_system() -> TeachingSystem:
    """获取教学系统单例"""
    global _teaching_system
    if _teaching_system is None:
        _teaching_system = TeachingSystem()
    return _teaching_system

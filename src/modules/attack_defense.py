"""
攻防场景教学模块
用于WiFi安全学习，包含各类攻击原理、防御方法、模拟演练
完全在模拟环境中，不涉及任何实际攻击
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class AttackCategory(Enum):
    """攻击类别"""
    WEP_ATTACK = "wep_attack"
    WPA_ATTACK = "wpa_attack"
    DOS_ATTACK = "dos_attack"
    EVIL_TWIN = "evil_twin"
    KRACK_ATTACK = "krack_attack"


class DefenseLevel(Enum):
    """防御等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AttackScenario:
    """攻击场景"""
    scenario_id: str
    category: AttackCategory
    title: str
    description: str
    attack_principle: str  # 攻击原理
    attack_steps: List[str]  # 攻击步骤（教学用）
    impact: str  # 攻击影响
    defense_methods: List[str]  # 防御方法
    difficulty: str  # 难度: basic/intermediate/advanced
    is_safe: bool = True  # 是否安全（仅供学习）
    warning: str = "仅供学习研究，禁止用于未授权网络"


@dataclass
class SimulationResult:
    """模拟结果"""
    scenario_id: str
    step: int
    status: str  # running/success/failed
    message: str
    defense_triggered: bool = False
    details: Dict = field(default_factory=dict)


class AttackDefenseSimulator:
    """
    攻防场景模拟器
    纯教学用途，模拟各类WiFi攻击与防御场景
    """

    def __init__(self):
        self.scenarios = self._init_scenarios()
        self.current_scenario: Optional[AttackScenario] = None
        self.current_step = 0
        self.simulation_log: List[str] = []

    def _init_scenarios(self) -> List[AttackScenario]:
        """初始化攻击场景"""
        return [
            # WEP攻击场景
            AttackScenario(
                scenario_id="wep-iv-reuse",
                category=AttackCategory.WEP_ATTACK,
                title="WEP IV重用攻击",
                description="演示WEP的初始化向量(IV)重用漏洞如何导致密钥泄露",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>WEP使用24位IV（初始化向量）+ 密钥来加密每个数据包。</p>
                    <p>由于IV只有24位（约1600万种组合），在繁忙网络中IV很快就会重复使用。</p>
                    <p>当相同的IV被重用时，攻击者可以收集多个使用相同IV的数据包，
                    通过密码分析恢复出密钥流，进而恢复出WEP密钥。</p>
                    
                    <h4>核心问题：</h4>
                    <ul>
                        <li>IV太短（24位），容易重复</li>
                        <li>IV直接以明文发送</li>
                        <li>密钥流 = RC4(IV + 密钥)</li>
                        <li>相同IV → 相同密钥流</li>
                    </ul>
                """,
                attack_steps=[
                    "监听WEP网络，捕获数据包",
                    "收集使用相同IV的数据包",
                    "分析重复IV，推导密钥流",
                    "使用已知明文攻击恢复密钥",
                    "收集足够数据后，破解出完整WEP密钥",
                ],
                impact="WEP网络完全被攻破，攻击者可以读取所有网络流量，甚至冒充合法用户",
                defense_methods=[
                    "立即升级到WPA/WPA2/WPA3",
                    "如果必须使用WEP，使用更长的密钥（128位以上）",
                    "频繁更换WEP密钥",
                    "使用VPN作为额外保护层",
                ],
                difficulty="basic"
            ),
            AttackScenario(
                scenario_id="wep-fms-attack",
                category=AttackCategory.WEP_ATTACK,
                title="WEP FMS攻击 (弱IV攻击)",
                description="演示Fluhrer-Mantin-Shamir攻击如何利用弱IV快速破解WEP",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>FMS攻击由Fluhrer、Mantin、Shamir三位密码学家于2001年提出。</p>
                    <p>他们发现RC4算法存在弱点：某些特定的IV（弱IV）会泄露密钥的字节信息。</p>
                    
                    <h4>攻击过程：</h4>
                    <ol>
                        <li>攻击者被动监听，收集含有弱IV的数据包</li>
                        <li>利用弱IV的特性，逐个字节推导密钥</li>
                        <li>收集约40000个弱IV数据包后，就能以很高概率恢复密钥</li>
                    </ol>
                    
                    <p><strong>著名工具：</strong>aircrack-ng 等工具正是利用了这个原理。</p>
                """,
                attack_steps=[
                    "启动无线网卡监听模式",
                    "选择目标WEP网络",
                    "使用 aireplay-ng 注入流量加速数据收集",
                    "持续捕获IV数据包",
                    "使用 aircrack-ng 分析IV并破解密钥",
                ],
                impact="几分钟内即可破解WEP密钥，网络完全沦陷",
                defense_methods=[
                    "弃用WEP，升级到WPA2或WPA3",
                    "这是WEP的根本性设计缺陷，无法通过配置修复",
                ],
                difficulty="intermediate"
            ),

            # WPA攻击场景
            AttackScenario(
                scenario_id="wpa-dictionary",
                category=AttackCategory.WPA_ATTACK,
                title="WPA/WPA2 字典攻击",
                description="演示握手包捕获后的离线字典攻击原理",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>WPA/WPA2的四次握手中，MIC（消息完整性校验）是用PTK计算的。</p>
                    <p>而PTK = PRF(PMK, ...)，PMK = PBKDF2(密码, SSID, 4096次迭代)。</p>
                    
                    <h4>攻击过程：</h4>
                    <ol>
                        <li>攻击者捕获四次握手的消息1和消息2（或消息2和3）</li>
                        <li>从握手包中提取 ANonce, SNonce, MAC地址, MIC等信息</li>
                        <li>准备密码字典（常见密码组合）</li>
                        <li>对字典中的每个密码：
                            <ul>
                                <li>计算 PMK = PBKDF2(密码, SSID, 4096)</li>
                                <li>计算 PTK = PRF(PMK, ANonce, SNonce, MAC...)</li>
                                <li>计算 MIC，与握手包中的MIC对比</li>
                            </ul>
                        </li>
                        <li>如果MIC匹配，则找到了正确密码</li>
                    </ol>
                    
                    <h4>关键事实：</h4>
                    <ul>
                        <li>攻击完全离线进行，不需要与目标网络交互</li>
                        <li>速度取决于CPU/GPU性能和字典大小</li>
                        <li>强密码（12位以上随机字符）几乎不可能被破解</li>
                        <li>弱密码（8位数字/常见单词）几秒就能破解</li>
                    </ul>
                """,
                attack_steps=[
                    "捕获WPA四次握手包",
                    "准备密码字典文件",
                    "使用破解工具（如aircrack-ng, hashcat）",
                    "逐一对字典中的密码计算并比对MIC",
                    "找到匹配的密码即为破解成功",
                ],
                impact="如果密码在字典中且足够弱，网络密钥会被破解",
                defense_methods=[
                    "使用强密码：至少12位，混合大小写+数字+特殊字符",
                    "避免使用常见单词、生日、电话号码等",
                    "启用WPA3（SAE握手能抵抗字典攻击）",
                    "定期更换WiFi密码",
                    "使用企业级认证（WPA2-Enterprise / 802.1X）",
                ],
                difficulty="basic"
            ),
            AttackScenario(
                scenario_id="wpa-pmkid",
                category=AttackCategory.WPA_ATTACK,
                title="WPA PMKID 攻击",
                description="演示无需完整握手的PMKID攻击原理",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>PMKID攻击由Stefan Viehböck在2018年发现。</p>
                    <p>某些路由器（特别是启用了漫游功能的）会在EAPOL帧中包含PMKID。</p>
                    
                    <h4>PMKID是什么？</h4>
                    <p>PMKID = HMAC-SHA1-128(PMK, "PMK Name" + BSSID + STA_MAC)</p>
                    <p>PMKID用于快速漫游（802.11r），让客户端在AP间切换时不需要重新认证。</p>
                    
                    <h4>攻击优势：</h4>
                    <ul>
                        <li><strong>不需要完整四次握手</strong>，只需要一个EAPOL帧</li>
                        <li>不需要等待客户端连接，直接向AP发送认证请求即可</li>
                        <li>成功率更高，不容易被打断</li>
                    </ul>
                    
                    <p>破解过程与字典攻击相同：用字典密码计算PMK，再计算PMKID，对比是否匹配。</p>
                """,
                attack_steps=[
                    "向目标AP发送关联请求",
                    "捕获包含PMKID的EAPOL帧",
                    "提取PMKID、BSSID、客户端MAC",
                    "使用字典攻击离线计算并比对PMKID",
                    "找到匹配的密码",
                ],
                impact="与字典攻击相同，但更容易获取攻击所需数据",
                defense_methods=[
                    "使用强密码是最根本的防御",
                    "如果路由器支持，禁用802.11r快速漫游（但会影响漫游体验）",
                    "升级到WPA3",
                    "使用企业级认证",
                ],
                difficulty="intermediate"
            ),

            # DoS攻击场景
            AttackScenario(
                scenario_id="deauth-flood",
                category=AttackCategory.DOS_ATTACK,
                title="Deauthentication 洪水攻击",
                description="演示解除认证帧洪水攻击如何导致客户端断网",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>Deauthentication（解除认证）帧是802.11管理帧的一种。</p>
                    <p>AP或客户端都可以发送Deauth帧来终止连接。</p>
                    
                    <h4>问题所在：</h4>
                    <ul>
                        <li>管理帧<strong>不需要认证</strong>，任何人都可以伪造</li>
                        <li>攻击者可以伪装成AP，向客户端发送Deauth帧</li>
                        <li>也可以伪装成客户端，向AP发送Deauth帧</li>
                        <li>收到Deauth帧后，连接立即断开</li>
                    </ul>
                    
                    <h4>攻击目的：</h4>
                    <ul>
                        <li>DoS（拒绝服务）：让目标无法使用WiFi</li>
                        <li>捕获握手包：客户端重连时，可以捕获四次握手</li>
                        <li>迫使客户端连接恶意AP（邪恶双生子攻击的前置步骤）</li>
                    </ul>
                    
                    <p><strong>注意：</strong>即使在WPA2/WPA3网络中，管理帧保护（MFP）不是必选项。</p>
                """,
                attack_steps=[
                    "扫描目标网络，获取AP和客户端MAC地址",
                    "使用工具（如aireplay-ng）发送Deauth帧",
                    "伪装成AP，向客户端发送解除认证",
                    "客户端被迫断开连接",
                    "客户端尝试重连时，可以进一步攻击",
                ],
                impact="目标客户端断网，无法使用WiFi服务",
                defense_methods=[
                    "启用管理帧保护（MFP / 802.11w）",
                    "使用5GHz频段（攻击难度略高）",
                    "WPA3默认要求管理帧保护",
                    "使用有线连接（针对关键设备）",
                ],
                difficulty="basic"
            ),

            # Evil Twin攻击场景
            AttackScenario(
                scenario_id="evil-twin",
                category=AttackCategory.EVIL_TWIN,
                title="邪恶双生子 (Evil Twin) 攻击",
                description="演示伪造AP如何诱骗用户连接并窃取数据",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>攻击者搭建一个与合法AP同名（同SSID）的恶意AP。</p>
                    <p>如果攻击者的信号更强，或者合法AP不可用，客户端可能会自动连接恶意AP。</p>
                    
                    <h4>攻击方式：</h4>
                    <ol>
                        <li><strong>同名AP欺骗：</strong>创建与目标相同SSID的AP</li>
                        <li><strong>信号压制：</strong>用更强的信号吸引客户端</li>
                        <li><strong>Deauth配合：</strong>先把用户从合法AP踢下线，再让他们连到恶意AP</li>
                        <li><strong>Portal认证：</strong>伪造登录页面，骗取账号密码</li>
                    </ol>
                    
                    <h4>连接后的危害：</h4>
                    <ul>
                        <li>中间人攻击（MITM）：读取甚至修改所有流量</li>
                        <li>窃取密码、Cookie、敏感信息</li>
                        <li>注入恶意代码</li>
                        <li>DNS劫持，重定向到钓鱼网站</li>
                    </ul>
                    
                    <h4>为什么有效？</h4>
                    <p>客户端通常只看SSID来选择网络，不会验证AP的真实身份。</p>
                """,
                attack_steps=[
                    "侦察目标网络的SSID和配置",
                    "部署恶意AP（相同SSID，更强信号）",
                    "（可选）发送Deauth帧让用户断开合法AP",
                    "等待或诱使用户连接恶意AP",
                    "进行中间人攻击，窃取数据",
                ],
                impact="用户所有网络流量可被监控和篡改，敏感信息泄露",
                defense_methods=[
                    "不随便连接陌生WiFi，尤其是不需要密码的开放网络",
                    "使用HTTPS / VPN 加密所有流量",
                    "关闭WiFi自动连接功能",
                    "注意证书警告，不要忽略安全提示",
                    "公共WiFi下不进行敏感操作（网银、支付等）",
                    "企业使用802.1X认证，可以验证AP身份",
                ],
                difficulty="intermediate"
            ),

            # KRACK攻击场景
            AttackScenario(
                scenario_id="krack-attack",
                category=AttackCategory.KRACK_ATTACK,
                title="KRACK 攻击 (密钥重装攻击)",
                description="演示WPA2的KRACK漏洞原理及其影响",
                attack_principle="""
                    <h3>攻击原理</h3>
                    <p>KRACK（Key Reinstallation Attack）由Mathy Vanhoef在2017年发现。</p>
                    <p>这是WPA2协议本身的一个严重漏洞，影响几乎所有WPA2设备。</p>
                    
                    <h4>漏洞本质：</h4>
                    <p>四次握手中的消息3可能被重传。当客户端收到重传的消息3时，
                    会重新安装PTK，并重置nonce（序列号）。</p>
                    
                    <h4>攻击方式：</h4>
                    <ol>
                        <li>攻击者处于中间人位置（需要在范围内）</li>
                        <li>阻止消息4到达AP，导致AP重传消息3</li>
                        <li>客户端收到重复的消息3，重新安装密钥</li>
                        <li>nonce被重置，导致密钥流被重用</li>
                        <li>利用重用的密钥流，可以解密甚至篡改数据包</li>
                    </ol>
                    
                    <h4>影响范围：</h4>
                    <ul>
                        <li>几乎所有WPA2设备都受影响</li>
                        <li>Android 6.0+ 和 Linux 受影响最严重</li>
                        <li>可以解密TCP流量，注入恶意内容</li>
                    </ul>
                    
                    <p><strong>好消息：</strong>各厂商已发布补丁修复此漏洞。</p>
                """,
                attack_steps=[
                    "设置恶意AP进行中间人攻击",
                    "等待客户端连接时进行四次握手",
                    "拦截并阻止消息4到达AP",
                    "重传消息3给客户端",
                    "客户端重新安装密钥，nonce重置",
                    "利用nonce重用解密流量",
                ],
                impact="数据包可被解密，敏感信息泄露，数据可能被篡改",
                defense_methods=[
                    "及时更新路由器固件和设备系统",
                    "使用HTTPS / VPN 作为额外保护层",
                    "升级到WPA3（从协议层面修复了此问题）",
                    "禁用WiFi连接时的自动重连",
                ],
                difficulty="advanced"
            ),
        ]

    def get_all_scenarios(self, category: Optional[str] = None) -> List[Dict]:
        """获取所有攻击场景"""
        result = []
        for s in self.scenarios:
            if category and s.category.value != category:
                continue
            result.append({
                "id": s.scenario_id,
                "category": s.category.value,
                "title": s.title,
                "description": s.description,
                "difficulty": s.difficulty,
                "warning": s.warning,
            })
        return result

    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """获取指定场景详情"""
        for s in self.scenarios:
            if s.scenario_id == scenario_id:
                return {
                    "id": s.scenario_id,
                    "category": s.category.value,
                    "title": s.title,
                    "description": s.description,
                    "attack_principle": s.attack_principle,
                    "attack_steps": s.attack_steps,
                    "impact": s.impact,
                    "defense_methods": s.defense_methods,
                    "difficulty": s.difficulty,
                    "warning": s.warning,
                    "is_safe": s.is_safe,
                }
        return None

    def start_simulation(self, scenario_id: str) -> Dict:
        """开始模拟"""
        for s in self.scenarios:
            if s.scenario_id == scenario_id:
                self.current_scenario = s
                self.current_step = 0
                self.simulation_log = [
                    f"[{self._current_time()}] 开始模拟: {s.title}",
                    f"[{self._current_time()}] 警告: 本模拟仅供学习研究，禁止用于未授权网络",
                ]
                return {
                    "status": "started",
                    "scenario_id": scenario_id,
                    "title": s.title,
                    "total_steps": len(s.attack_steps),
                    "current_step": 0,
                    "warning": s.warning,
                    "log": self.simulation_log,
                }
        return {"error": "场景不存在"}

    def next_simulation_step(self, use_defense: bool = False) -> SimulationResult:
        """执行下一步模拟"""
        if not self.current_scenario:
            return SimulationResult(
                scenario_id="",
                step=0,
                status="failed",
                message="请先开始模拟"
            )

        if self.current_step >= len(self.current_scenario.attack_steps):
            return SimulationResult(
                scenario_id=self.current_scenario.scenario_id,
                step=self.current_step,
                status="success",
                message="攻击模拟完成（教学演示）",
                details={"note": "这只是原理演示，不是真实攻击"}
            )

        step_desc = self.current_scenario.attack_steps[self.current_step]
        self.current_step += 1

        self.simulation_log.append(
            f"[{self._current_time()}] [攻击步骤 {self.current_step}] {step_desc}"
        )

        # 模拟防御效果
        defense_triggered = False
        if use_defense and self.current_step >= 2:
            defense_triggered = True
            self.simulation_log.append(
                f"[{self._current_time()}] [防御触发] 检测到异常行为，已采取防御措施"
            )

        is_last = self.current_step >= len(self.current_scenario.attack_steps)
        status = "success" if is_last and not defense_triggered else "running"

        return SimulationResult(
            scenario_id=self.current_scenario.scenario_id,
            step=self.current_step,
            status=status,
            message=step_desc,
            defense_triggered=defense_triggered,
            details={
                "step_description": step_desc,
                "defense_tip": self._get_defense_tip(self.current_step),
                "log": list(self.simulation_log),
            }
        )

    def _get_defense_tip(self, step: int) -> str:
        """获取对应步骤的防御提示"""
        if not self.current_scenario:
            return ""
        if step - 1 < len(self.current_scenario.defense_methods):
            return self.current_scenario.defense_methods[step - 1]
        return self.current_scenario.defense_methods[-1] if self.current_scenario.defense_methods else ""

    def get_defense_methods(self, scenario_id: str) -> List[str]:
        """获取防御方法"""
        for s in self.scenarios:
            if s.scenario_id == scenario_id:
                return s.defense_methods
        return []

    def get_all_defense_summary(self) -> List[Dict]:
        """获取所有防御方法汇总"""
        return [
            {
                "title": "强密码原则",
                "icon": "lock",
                "description": "使用至少12位的复杂密码，混合大小写、数字和特殊字符",
                "importance": "critical"
            },
            {
                "title": "选择正确的加密方式",
                "icon": "shield",
                "description": "优先使用WPA3，其次WPA2，绝对不要使用WEP",
                "importance": "critical"
            },
            {
                "title": "管理帧保护",
                "icon": "shield",
                "description": "启用802.11w/MFP，防止Deauth等管理帧攻击",
                "importance": "high"
            },
            {
                "title": "定期更新固件",
                "icon": "refresh",
                "description": "保持路由器和设备固件更新，修复已知漏洞",
                "importance": "high"
            },
            {
                "title": "隐藏SSID？",
                "icon": "eye-off",
                "description": "隐藏SSID的安全性很有限，不应作为主要安全措施",
                "importance": "low"
            },
            {
                "title": "MAC地址过滤",
                "icon": "filter",
                "description": "MAC地址可以被伪造，只能增加攻击门槛，不能真正防护",
                "importance": "low"
            },
            {
                "title": "使用VPN",
                "icon": "globe",
                "description": "在公共WiFi或不信任的网络中使用VPN，端到端加密流量",
                "importance": "high"
            },
            {
                "title": "企业级认证",
                "icon": "building",
                "description": "使用WPA2-Enterprise/WPA3-Enterprise（802.1X），每个用户独立凭证",
                "importance": "medium"
            },
        ]

    def reset_simulation(self) -> Dict:
        """重置模拟"""
        self.current_scenario = None
        self.current_step = 0
        self.simulation_log = []
        return {"status": "reset"}

    def _current_time(self) -> str:
        """获取当前时间字符串"""
        import time
        return time.strftime("%H:%M:%S", time.localtime())

    def get_categories(self) -> List[Dict]:
        """获取攻击类别列表"""
        return [
            {"id": "wep_attack", "name": "WEP攻击", "count": len([s for s in self.scenarios if s.category == AttackCategory.WEP_ATTACK])},
            {"id": "wpa_attack", "name": "WPA/WPA2攻击", "count": len([s for s in self.scenarios if s.category == AttackCategory.WPA_ATTACK])},
            {"id": "dos_attack", "name": "拒绝服务攻击", "count": len([s for s in self.scenarios if s.category == AttackCategory.DOS_ATTACK])},
            {"id": "evil_twin", "name": "邪恶双生子", "count": len([s for s in self.scenarios if s.category == AttackCategory.EVIL_TWIN])},
            {"id": "krack_attack", "name": "KRACK攻击", "count": len([s for s in self.scenarios if s.category == AttackCategory.KRACK_ATTACK])},
        ]


# 全局实例
_ad_simulator = None

def get_attack_defense_simulator() -> AttackDefenseSimulator:
    """获取攻防模拟器单例"""
    global _ad_simulator
    if _ad_simulator is None:
        _ad_simulator = AttackDefenseSimulator()
    return _ad_simulator

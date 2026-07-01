"""
大模型提示词管理 - WiFi可视化安全学习工具 v2
包含各类场景的提示词设计
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class Prompt:
    """提示词"""
    system: str
    user_template: str
    description: str


class PromptManager:
    """
    提示词管理器
    管理各类场景的提示词
    """

    # 系统级提示词
    SYSTEM_PROMPT = """你是WiFi网络安全教育专家助手。你的使命是帮助用户学习和理解WiFi安全技术，而不是提供攻击方法。

【核心原则】
1. 只教授防御和安全知识，不提供任何攻击指导
2. 鼓励用户在自己授权的网络上进行学习
3. 强调网络安全的重要性，倡导合法合规
4. 回答要专业但易懂，结合实际案例

【专业领域】
- WiFi加密协议原理（WEP/WPA/WPA2/WPA3）
- WiFi握手过程和密钥交换
- 常见WiFi安全漏洞和防护措施
- WiFi安全最佳实践
- 网络安全基础知识

【回答风格】
- 专业但不晦涩
- 结合实际案例
- 鼓励思考和探索
- 适当使用类比和图解

【边界约束】
- 拒绝回答如何破解他人WiFi的问题
- 拒绝提供攻击工具的使用方法
- 拒绝指导任何未经授权的网络测试
- 遇到边界问题，引导到安全学习方向"""

    # 教学导师提示词
    TEACHING_ASSISTANT_PROMPT = """【角色定义】
你是一位循循善诱的WiFi安全课程导师，善于用生动的比喻和实例解释复杂概念。

【教学风格】
- 先了解用户的知识水平
- 由浅入深，循序渐进
- 善于提问引导思考
- 及时肯定和鼓励

【互动模式】
- 询问用户是否理解
- 提供思考题和练习
- 根据反馈调整讲解深度
- 串联相关知识点"""

    # 攻防演练提示词
    ATTACK_DEFENSE_PROMPT = """【角色定义】
你是一个专业的网络安全演练教练，负责设计攻防场景并指导学习者。

【演练模式】
模拟真实攻防场景：
- 攻击场景：模拟黑客入侵，分析攻击步骤和防御要点
- 防御场景：模拟安全加固，分析薄弱环节和改进方案

【指导方式】
1. 先讲解背景和目标
2. 分步演示过程
3. 分析每步的原理和意义
4. 给出防御建议
5. 引导学习者思考

【安全提醒】
- 始终强调授权测试的重要性
- 提醒不要在实际生产环境中尝试
- 强调学习目的是提高安全意识"""

    # CTF助手提示词
    CTF_HELPER_PROMPT = """【角色定义】
你是一位经验丰富的CTF选手和出题者，帮助学习者解决WiFi安全相关的CTF题目。

【解题辅助】
- 不直接给答案，而是引导思考
- 提供分级提示（从模糊到明确）
- 讲解涉及的知识点的
- 分析常见陷阱和误区

【提示分级】
1. 方向性提示（点到即止）
2. 方法性提示（指出方向）
3. 技术性提示（提供工具/方法）
4. 接近答案的提示（差一步）
5. 最终答案（不得已再用）

【复盘讲解】
- 详细讲解解题思路
- 涉及的知识点
- 工具使用技巧
- 相关题目推荐"""

    # 智能陪练提示词
    PRACTICE_PARTNER_PROMPT = """【角色定义】
你是一位耐心陪练的WiFi安全学习伙伴，通过对话和场景模拟帮助你巩固知识。

【陪练方式】
- 情景对话练习
- 问答式复习
- 错误纠正和解释
- 鼓励和激励

【个性化学习】
- 根据学习进度调整难度
- 识别薄弱环节并加强
- 创造练习机会
- 记录学习轨迹"""

    # WiFi基础问答提示词
    WIFI_BASIC_PROMPT = """【专注领域】
WiFi基础知识、安全原理、加密协议

【回答要求】
- 用通俗易懂的语言解释专业术语
- 适当使用类比帮助理解
- 结合实际应用场景
- 鼓励动手实践"""

    def __init__(self):
        """初始化提示词管理器"""
        self._prompts: Dict[str, Prompt] = {
            "default": Prompt(
                system=self.SYSTEM_PROMPT,
                user_template="{message}",
                description="默认问答"
            ),
            "teaching": Prompt(
                system=self.SYSTEM_PROMPT + "\n\n" + self.TEACHING_ASSISTANT_PROMPT,
                user_template="{message}",
                description="教学导师"
            ),
            "attack_defense": Prompt(
                system=self.SYSTEM_PROMPT + "\n\n" + self.ATTACK_DEFENSE_PROMPT,
                user_template="{message}",
                description="攻防演练"
            ),
            "ctf": Prompt(
                system=self.SYSTEM_PROMPT + "\n\n" + self.CTF_HELPER_PROMPT,
                user_template="{message}",
                description="CTF挑战助手"
            ),
            "practice": Prompt(
                system=self.SYSTEM_PROMPT + "\n\n" + self.PRACTICE_PARTNER_PROMPT,
                user_template="{message}",
                description="智能陪练"
            ),
            "wifi_basic": Prompt(
                system=self.SYSTEM_PROMPT + "\n\n" + self.WIFI_BASIC_PROMPT,
                user_template="{message}",
                description="WiFi基础问答"
            )
        }

    def get_prompt(self, scenario: str = "default") -> Prompt:
        """
        获取提示词

        Args:
            scenario: 场景名称

        Returns:
            对应的提示词
        """
        return self._prompts.get(scenario, self._prompts["default"])

    def get_system_prompt(self, scenario: str = "default") -> str:
        """
        获取系统提示词

        Args:
            scenario: 场景名称

        Returns:
            系统提示词
        """
        prompt = self.get_prompt(scenario)
        return prompt.system

    def format_user_message(self, scenario: str, message: str) -> str:
        """
        格式化用户消息

        Args:
            scenario: 场景名称
            message: 用户原始消息

        Returns:
            格式化后的消息
        """
        prompt = self.get_prompt(scenario)
        return prompt.user_template.format(message=message)

    def list_scenarios(self) -> Dict[str, str]:
        """
        列出所有场景

        Returns:
            场景名称到描述的映射
        """
        return {
            name: prompt.description
            for name, prompt in self._prompts.items()
        }

    def get_ctf_hint(self, hint_level: int) -> str:
        """
        获取CTF分级提示

        Args:
            hint_level: 提示级别(1-5)

        Returns:
            对应级别的提示内容
        """
        hints = {
            1: "【方向性提示】请仔细阅读题目，思考涉及的知识点...",
            2: "【方法性提示】这个题目可能需要用到XXX工具或方法...",
            3: "【技术性提示】可以尝试使用XXX工具，分析数据包中的XXX字段...",
            4: "【接近答案】答案可能隐藏在XXX位置，尝试XXX操作...",
            5: "【最终答案】答案是: XXX（请确保已理解原理）"
        }
        return hints.get(hint_level, hints[1])

    def get_learning_path_prompt(self, user_level: str) -> str:
        """
        获取学习路径推荐提示

        Args:
            user_level: 用户水平(beginner/intermediate/advanced)

        Returns:
            学习路径推荐提示词
        """
        level_prompts = {
            "beginner": """请为初学者设计一个WiFi安全学习路径：
1. 从基础概念开始（什么是WiFi、WLAN）
2. 了解WiFi加密的必要性
3. 学习WEP的原理和为什么它不安全
4. 进阶到WPA/WPA2
5. 了解四次握手过程
请给出循序渐进的学习计划，包括每个阶段需要掌握的知识点。""",
            "intermediate": """请为有一定基础的学习者设计进阶路径：
1. 深入理解WPA2-PSK的密钥交换
2. 学习如何分析握手包
3. 了解常见的WiFi攻击原理
4. 掌握防御措施
请设计一个包含实践的进阶计划。""",
            "advanced": """请为高级学习者设计专家路径：
1. WPA3的新特性
2. 企业级WiFi安全
3. WiFi安全审计
4. 渗透测试实战
请推荐专业的学习资源和实战方向。"""
        }
        return level_prompts.get(user_level, level_prompts["beginner"])

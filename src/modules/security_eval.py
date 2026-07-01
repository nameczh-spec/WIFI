"""
安全评估模块 - WiFi可视化安全学习工具 v2
评估自有网络的安全性
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from src.core.safety import SafetyManager, OperationLevel
from src.core.logger import get_logger

logger = get_logger("security_eval")


@dataclass
class PasswordStrength:
    """密码强度评估结果"""
    total_score: int  # 0-100
    level: str  # 弱/中/强/很强
    length_score: int
    complexity_score: int
    weak_pattern_score: int
    suggestions: List[str]


@dataclass
class EncryptionRating:
    """加密方式评级"""
    encryption_type: str
    score: int  # 0-100
    level: str  # 危险/弱/中/强
    advice: str


@dataclass
class SecurityReport:
    """安全评估报告"""
    password_strength: PasswordStrength
    encryption_rating: EncryptionRating
    overall_score: int
    overall_level: str
    risks: List[str]
    suggestions: List[str]


class NetworkSecurityEvaluator:
    """
    网络安全评估器
    评估自有网络的安全性
    """

    # 常见弱密码列表（精简版）
    COMMON_WEAK_PASSWORDS = {
        "123456", "password", "admin", "12345678", "qwerty",
        "111111", "000000", "123456789", "1234567", "abc123",
        "iloveyou", "monkey", "dragon", "master", "login",
        "88888888", "696969", "666666", "123123", "letmein",
        "12345", "sunshine", "princess", "welcome", "shadow",
        "1234", "password1", "baseball", "football", "soccer",
        "qwerty123", "1q2w3e4r", "1qaz2wsx", "admin123", "root"
    }

    # 弱密码文件路径
    WEAK_PASSWORDS_FILE = None  # 可配置

    def __init__(self, safety_manager: SafetyManager = None):
        """初始化评估器"""
        self.safety = safety_manager
        if safety_manager:
            safety_manager.register_operation(
                "security_eval",
                OperationLevel.SAFE,
                "评估自有网络安全性"
            )

        # 加载弱密码库
        self._load_weak_passwords()

    def _load_weak_passwords(self):
        """加载弱密码库"""
        from pathlib import Path

        default_file = Path(__file__).parent.parent.parent / "data" / "weak_passwords.txt"
        if default_file.exists():
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    self.WEAK_PASSWORDS_FILE = set(
                        line.strip().lower() for line in f if line.strip()
                    )
            except:
                self.WEAK_PASSWORDS_FILE = self.COMMON_WEAK_PASSWORDS
        else:
            self.WEAK_PASSWORDS_FILE = self.COMMON_WEAK_PASSWORDS

    def evaluate_password(self, password: str) -> PasswordStrength:
        """
        评估密码强度

        Args:
            password: 要评估的密码

        Returns:
            密码强度评估结果
        """
        # 长度评分
        length_score = self._check_length(password)

        # 复杂度评分
        complexity_score = self._check_complexity(password)

        # 弱密码检测
        weak_pattern_score = self._check_weak_patterns(password)

        # 总分
        total_score = min(100, length_score + complexity_score + weak_pattern_score)

        # 等级
        if total_score < 40:
            level = "弱"
        elif total_score < 60:
            level = "中"
        elif total_score < 80:
            level = "强"
        else:
            level = "很强"

        # 建议
        suggestions = self._generate_suggestions(
            password, length_score, complexity_score, weak_pattern_score
        )

        return PasswordStrength(
            total_score=total_score,
            level=level,
            length_score=length_score,
            complexity_score=complexity_score,
            weak_pattern_score=weak_pattern_score,
            suggestions=suggestions
        )

    def _check_length(self, password: str) -> int:
        """检查密码长度"""
        length = len(password)
        if length < 8:
            return 0
        elif length <= 10:
            return 15
        elif length <= 15:
            return 25
        else:
            return 30

    def _check_complexity(self, password: str) -> int:
        """检查密码复杂度"""
        score = 0

        if re.search(r'\d', password):
            score += 7  # 包含数字
        if re.search(r'[a-z]', password):
            score += 7  # 包含小写字母
        if re.search(r'[A-Z]', password):
            score += 8  # 包含大写字母
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 8  # 包含特殊字符

        return min(30, score)

    def _check_weak_patterns(self, password: str) -> int:
        """检查弱密码模式"""
        score = 40  # 满分40

        pwd_lower = password.lower()

        # 检查是否在弱密码库
        if pwd_lower in self.WEAK_PASSWORDS_FILE:
            return 0

        # 检查连续数字
        if re.search(r'12345|23456|34567|45678|56789|67890', password):
            score -= 20

        # 检查连续字母
        if re.search(r'abc|bcd|cde|def|efg|fgh|qwe|wer|ert', pwd_lower):
            score -= 15

        # 检查键盘顺序
        keyboard_patterns = ['qwerty', 'asdf', 'zxcv', 'qazwsx', '1qaz', '2wsx']
        for pattern in keyboard_patterns:
            if pattern in pwd_lower:
                score -= 15
                break

        # 检查重复字符
        if re.search(r'(.)\1{2,}', password):
            score -= 10

        # 检查纯数字/纯字母
        if password.isdigit():
            score -= 20
        elif password.isalpha():
            score -= 15

        return max(0, min(40, score))

    def _generate_suggestions(
        self,
        password: str,
        length_score: int,
        complexity_score: int,
        weak_score: int
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if length_score < 15:
            suggestions.append("密码长度建议至少8位以上，推荐12位以上")
        if complexity_score < 14:
            suggestions.append("建议包含数字、大小写字母和特殊字符")
        if weak_score < 20:
            suggestions.append("检测到弱密码模式，请避免使用常见密码或键盘顺序")

        if not suggestions:
            suggestions.append("密码强度良好，继续保持！")

        return suggestions

    def rate_encryption(self, encryption: str) -> EncryptionRating:
        """
        评级加密方式

        Args:
            encryption: 加密方式字符串

        Returns:
            加密方式评级结果
        """
        enc_lower = encryption.lower()

        # WEP - 危险
        if "wep" in enc_lower:
            return EncryptionRating(
                encryption_type="WEP",
                score=0,
                level="危险",
                advice="WEP加密已完全淘汰，请立即更换为WPA2或WPA3"
            )

        # WPA - 中等
        if "wpa2" in enc_lower:
            if "ccmp" in enc_lower or "aes" in enc_lower:
                return EncryptionRating(
                    encryption_type="WPA2-AES",
                    score=70,
                    level="中",
                    advice="WPA2-AES是当前主流安全方案，建议使用"
                )
            return EncryptionRating(
                encryption_type="WPA2",
                score=70,
                level="中",
                advice="WPA2是较好的选择，推荐使用AES加密"
            )
        if "wpa" in enc_lower:
            return EncryptionRating(
                encryption_type="WPA",
                score=30,
                level="弱",
                advice="WPA已逐渐淘汰，建议升级到WPA2"
            )

        # Open - 无加密
        if "open" in enc_lower or "none" in enc_lower:
            return EncryptionRating(
                encryption_type="无加密",
                score=0,
                level="危险",
                advice="开放网络极不安全，请立即启用加密"
            )

        # 未知
        return EncryptionRating(
            encryption_type="未知",
            score=50,
            level="未知",
            advice="无法识别的加密方式，请确认设置"
        )

    def evaluate_network(
        self,
        ssid: str,
        password: str,
        encryption: str
    ) -> SecurityReport:
        """
        综合评估网络安全

        Args:
            ssid: 网络名称
            password: 密码
            encryption: 加密方式

        Returns:
            综合安全评估报告
        """
        logger.info(f"开始评估网络 '{ssid}' 的安全性")

        # 评估密码
        pwd_strength = self.evaluate_password(password)

        # 评级加密
        enc_rating = self.rate_encryption(encryption)

        # 综合评分（密码占60%，加密占40%）
        overall_score = int(pwd_strength.total_score * 0.6 + enc_rating.score * 0.4)

        # 综合等级
        if overall_score < 40:
            overall_level = "危险"
        elif overall_score < 60:
            overall_level = "弱"
        elif overall_score < 80:
            overall_level = "中"
        else:
            overall_level = "强"

        # 风险点
        risks = []
        if enc_rating.level == "危险":
            risks.append(f"加密方式{enc_rating.level}：{enc_rating.advice}")
        if pwd_strength.level in ["弱", "中"]:
            risks.append(f"密码强度{pwd_strength.level}，存在被破解风险")
        if not encryption or "open" in encryption.lower():
            risks.append("网络无加密保护，数据传输完全暴露")

        # 建议
        suggestions = pwd_strength.suggestions.copy()
        if enc_rating.advice:
            suggestions.append(enc_rating.advice)

        logger.info(f"网络 '{ssid}' 评估完成，综合评分: {overall_score} ({overall_level})")

        return SecurityReport(
            password_strength=pwd_strength,
            encryption_rating=enc_rating,
            overall_score=overall_score,
            overall_level=overall_level,
            risks=risks,
            suggestions=suggestions
        )

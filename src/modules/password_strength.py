"""
密码强度测试练习模块
纯本地计算，不涉及网络
帮助用户理解密码安全原理
"""

import re
import math
import hashlib
from typing import List, Dict, Tuple


class PasswordStrengthTester:
    """
    密码强度测试器
    评估密码强度、识别弱模式、估算破解时间
    """

    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "password1", "1234567", "123456789", "12345", "iloveyou",
        "admin", "welcome", "monkey", "dragon", "master",
        "letmein", "sunshine", "princess", "football", "111111",
        "passw0rd", "shadow", "sunshine", "trustno1", "michael",
        "666666", "1qaz2wsx", "qwerty123", "asdfghjkl", "000000",
        "test", "test123", "root", "toor", "admin123",
    }

    def __init__(self):
        self.cache = {}

    def evaluate(self, password: str, detail_level: str = "basic") -> Dict:
        """评估密码强度"""
        if not password:
            return {"success": False, "error": "密码不能为空"}

        cache_key = hashlib.md5(password.encode()).hexdigest()
        if cache_key in self.cache and detail_level in self.cache[cache_key]:
            return self.cache[cache_key][detail_level]

        length = len(password)
        char_types = self._get_char_types(password)
        type_count = sum(1 for v in char_types.values() if v)
        
        score = 0
        score += min(length * 4, 40)
        score += type_count * 10
        
        patterns = self.detect_weak_patterns(password)
        pattern_penalty = len(patterns) * 15
        score = max(0, score - pattern_penalty)
        
        if self.check_dictionary(password)["found"]:
            score = min(score, 10)
        
        score = min(100, score)
        
        level = self._get_level(score)
        crack_time = self.estimate_crack_time(password)
        
        basic = {
            "success": True,
            "score": score,
            "level": level,
            "length": length,
        }
        
        if detail_level == "basic":
            return basic
        
        detailed = {
            **basic,
            "char_types": char_types,
            "char_type_count": type_count,
            "weak_patterns": patterns,
            "crack_time": crack_time["time_human"],
        }
        
        if detail_level == "detailed":
            return detailed
        
        full = {
            **detailed,
            "crack_time_detail": crack_time,
            "improvement_advice": self.get_improvement_advice(password)["advice"],
            "dictionary_check": self.check_dictionary(password),
            "entropy": self._calculate_entropy(password),
        }
        
        if cache_key not in self.cache:
            self.cache[cache_key] = {}
        self.cache[cache_key][detail_level] = full
        
        return full

    def _get_char_types(self, password: str) -> Dict:
        """获取字符类型"""
        return {
            "lowercase": bool(re.search(r'[a-z]', password)),
            "uppercase": bool(re.search(r'[A-Z]', password)),
            "digits": bool(re.search(r'[0-9]', password)),
            "symbols": bool(re.search(r'[^a-zA-Z0-9]', password)),
        }

    def _get_level(self, score: int) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "极强"
        elif score >= 75:
            return "强"
        elif score >= 60:
            return "中等"
        elif score >= 40:
            return "弱"
        elif score >= 20:
            return "很弱"
        else:
            return "极弱"

    def detect_weak_patterns(self, password: str) -> List[Dict]:
        """检测弱密码模式"""
        patterns = []
        
        if self._is_common_password(password):
            patterns.append({
                "type": "common_password",
                "name": "常见密码",
                "severity": "critical",
                "description": "该密码在常见密码字典中，极易被破解",
            })
        
        if self._is_sequential(password):
            patterns.append({
                "type": "sequential",
                "name": "序列字符",
                "severity": "high",
                "description": "密码包含连续的数字或字母序列",
            })
        
        if self._is_repeating(password):
            patterns.append({
                "type": "repeating",
                "name": "重复字符",
                "severity": "high",
                "description": "密码包含大量重复字符",
            })
        
        if len(password) < 8:
            patterns.append({
                "type": "too_short",
                "name": "长度不足",
                "severity": "high",
                "description": "密码长度小于8位，安全性不足",
            })
        
        if password.isalpha():
            patterns.append({
                "type": "letters_only",
                "name": "纯字母",
                "severity": "medium",
                "description": "密码只有字母，没有数字或符号",
            })
        
        if password.isdigit():
            patterns.append({
                "type": "digits_only",
                "name": "纯数字",
                "severity": "high",
                "description": "密码只有数字，组合空间太小",
            })
        
        if re.match(r'^[a-z]+[0-9]+$', password):
            patterns.append({
                "type": "letters_plus_digits",
                "name": "字母+数字后缀",
                "severity": "medium",
                "description": "常见的弱模式：字母后面加数字后缀",
            })
        
        return patterns

    def _is_common_password(self, password: str) -> bool:
        """检查是否为常见密码"""
        return password.lower() in self.COMMON_PASSWORDS

    def _is_sequential(self, password: str) -> bool:
        """检查是否包含序列字符"""
        if len(password) < 3:
            return False
        
        pwd = password.lower()
        
        for i in range(len(pwd) - 2):
            if (ord(pwd[i+1]) == ord(pwd[i]) + 1 and
                ord(pwd[i+2]) == ord(pwd[i]) + 2):
                return True
            if (ord(pwd[i+1]) == ord(pwd[i]) - 1 and
                ord(pwd[i+2]) == ord(pwd[i]) - 2):
                return True
        
        return False

    def _is_repeating(self, password: str) -> bool:
        """检查是否有大量重复字符"""
        if len(password) < 3:
            return False
        
        for char in set(password):
            if password.count(char) / len(password) > 0.6:
                return True
        
        return False

    def estimate_crack_time(self, password: str) -> Dict:
        """估算破解时间"""
        combinations = self._calculate_combinations(password)
        guesses_per_second = 100_000_000  # 假设每秒1亿次猜测（GPU）
        
        seconds = combinations / guesses_per_second
        
        return {
            "time_seconds": seconds,
            "time_human": self._format_time(seconds),
            "combinations": combinations,
            "guesses_per_second": guesses_per_second,
            "hardware": "GPU（每秒1亿次猜测）",
            "note": "这是理论估算。WPA2实际破解速度受PBKDF2迭代次数限制，会慢很多。",
        }

    def _calculate_combinations(self, password: str) -> int:
        """计算可能的组合数"""
        char_types = self._get_char_types(password)
        pool_size = 0
        
        if char_types["lowercase"]:
            pool_size += 26
        if char_types["uppercase"]:
            pool_size += 26
        if char_types["digits"]:
            pool_size += 10
        if char_types["symbols"]:
            pool_size += 33
        
        if pool_size == 0:
            pool_size = 1
        
        return pool_size ** len(password)

    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        if seconds < 1:
            return "瞬间（小于1秒）"
        elif seconds < 60:
            return f"{seconds:.1f} 秒"
        elif seconds < 3600:
            return f"{seconds/60:.1f} 分钟"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} 小时"
        elif seconds < 86400 * 30:
            return f"{seconds/86400:.1f} 天"
        elif seconds < 86400 * 365:
            return f"{seconds/(86400*30):.1f} 个月"
        elif seconds < 86400 * 365 * 100:
            return f"{seconds/(86400*365):.1f} 年"
        elif seconds < 86400 * 365 * 1_000_000:
            return f"{seconds/(86400*365*1000):.1f} 千年"
        else:
            return f"{seconds/(86400*365*1e9):.1f} 亿年（实际上不可破解）"

    def get_improvement_advice(self, password: str) -> Dict:
        """获取密码改进建议"""
        advice = []
        
        if len(password) < 12:
            advice.append({
                "type": "length",
                "priority": "high",
                "title": "增加长度",
                "description": f"当前 {len(password)} 位，建议至少12位。长度每增加1位，破解难度指数级上升。",
                "benefit": "安全性提升 26~100 倍",
            })
        
        char_types = self._get_char_types(password)
        if not char_types["uppercase"]:
            advice.append({
                "type": "uppercase",
                "priority": "medium",
                "title": "添加大写字母",
                "description": "混合大小写可以大幅增加密码的组合空间。",
                "benefit": "组合空间翻倍",
            })
        
        if not char_types["digits"]:
            advice.append({
                "type": "digits",
                "priority": "medium",
                "title": "添加数字",
                "description": "在密码中加入数字可以提高复杂度。",
                "benefit": "组合空间增加约38%",
            })
        
        if not char_types["symbols"]:
            advice.append({
                "type": "symbols",
                "priority": "medium",
                "title": "添加特殊符号",
                "description": "添加 !@#$%^&* 等符号可以显著增加破解难度。",
                "benefit": "组合空间增加约50%",
            })
        
        patterns = self.detect_weak_patterns(password)
        if patterns:
            for p in patterns:
                advice.append({
                    "type": f"fix_{p['type']}",
                    "priority": p["severity"],
                    "title": f"避免{p['name']}",
                    "description": p["description"],
                    "benefit": "消除明显弱点",
                })
        
        if not advice:
            advice.append({
                "type": "excellent",
                "priority": "low",
                "title": "密码强度很好！",
                "description": "您的密码已经很强了，继续保持良好的密码习惯。",
                "benefit": "",
            })
        
        return {
            "success": True,
            "advice": advice,
            "total_advice": len(advice),
        }

    def check_dictionary(self, password: str) -> Dict:
        """检查是否在常见密码字典中"""
        found = password.lower() in self.COMMON_PASSWORDS
        return {
            "success": True,
            "found": found,
            "dictionary_size": len(self.COMMON_PASSWORDS),
            "note": "仅内置少量常见密码用于演示，实际字典有数百万条。",
        }

    def get_strength_curve(self) -> Dict:
        """获取密码强度曲线数据（用于可视化）"""
        lengths = [4, 6, 8, 10, 12, 14, 16, 20]
        strengths_lower = []
        strengths_mixed = []
        
        for length in lengths:
            lower_entropy = math.log2(26 ** length)
            mixed_entropy = math.log2(94 ** length)
            
            strength_lower = min(100, lower_entropy * 2)
            strength_mixed = min(100, mixed_entropy * 1.2)
            
            strengths_lower.append(round(strength_lower, 1))
            strengths_mixed.append(round(strength_mixed, 1))
        
        return {
            "success": True,
            "lengths": lengths,
            "strengths": {
                "纯小写字母": strengths_lower,
                "混合字符（大小写+数字+符号）": strengths_mixed,
            },
            "x_label": "密码长度（位）",
            "y_label": "强度评分（满分100）",
        }

    def _calculate_entropy(self, password: str) -> Dict:
        """计算密码熵"""
        char_types = self._get_char_types(password)
        pool_size = 0
        
        if char_types["lowercase"]:
            pool_size += 26
        if char_types["uppercase"]:
            pool_size += 26
        if char_types["digits"]:
            pool_size += 10
        if char_types["symbols"]:
            pool_size += 33
        
        if pool_size == 0:
            pool_size = 1
        
        entropy = len(password) * math.log2(pool_size)
        
        return {
            "bits": round(entropy, 1),
            "pool_size": pool_size,
            "interpretation": self._interpret_entropy(entropy),
        }

    def _interpret_entropy(self, entropy: float) -> str:
        """解释熵值含义"""
        if entropy < 28:
            return "非常弱：几分钟内可破解"
        elif entropy < 36:
            return "弱：几小时到几天可破解"
        elif entropy < 60:
            return "中等：GPU需要数月到数年"
        elif entropy < 80:
            return "强：超级计算机需要数百年"
        else:
            return "极强：实际上不可破解"


_password_strength_tester = None


def get_password_strength_tester() -> PasswordStrengthTester:
    """获取密码强度测试器单例"""
    global _password_strength_tester
    if _password_strength_tester is None:
        _password_strength_tester = PasswordStrengthTester()
    return _password_strength_tester

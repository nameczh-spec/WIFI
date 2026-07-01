"""
安全框架模块 - WiFi可视化安全学习工具 v2
包含操作权限分级和双密码验证
"""

from enum import Enum
from typing import Callable, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


class OperationLevel(Enum):
    """操作安全级别"""
    SAFE = "safe"           # 安全操作，直接执行
    CAUTION = "caution"     # 需确认后执行
    DANGEROUS = "dangerous" # 危险操作，默认禁用


@dataclass
class Operation:
    """操作定义"""
    name: str
    level: OperationLevel
    description: str
    requires_auth: bool = False  # 是否需要认证
    last_used: Optional[datetime] = None


class SafetyManager:
    """
    安全管理器
    管理操作权限和双密码验证
    """

    def __init__(self, gentle_mode: bool = True):
        """
        初始化安全管理器

        Args:
            gentle_mode: 温和模式开关
        """
        self.gentle_mode = gentle_mode
        self._operations: Dict[str, Operation] = {}
        self._confirm_callback: Optional[Callable[[str, str], bool]] = None

        # 双密码验证状态
        self._dual_password_enabled = False
        self._dual_password_verified = False
        self._password_1_verified = False
        self._password_2_verified = False

        # 授权状态
        self._network_authorized = False
        self._authorization_timestamp: Optional[datetime] = None

        # 注册默认操作
        self._register_default_operations()

    def _register_default_operations(self):
        """注册默认操作"""
        default_ops = [
            ("wifi_scan", OperationLevel.SAFE, "被动扫描WiFi网络"),
            ("view_knowledge", OperationLevel.SAFE, "查看学习资料"),
            ("security_eval", OperationLevel.SAFE, "安全评估"),
            ("handshake_verify", OperationLevel.SAFE, "握手验证"),
            ("view_learning", OperationLevel.SAFE, "教学模式"),
            ("advanced_practice", OperationLevel.DANGEROUS, "高级练习模式", True),
            ("password_attack", OperationLevel.DANGEROUS, "密码练习", True),
            ("packet_injection", OperationLevel.DANGEROUS, "数据包注入", True),
        ]

        for name, level, desc, *args in default_ops:
            requires_auth = args[0] if args else False
            self._operations[name] = Operation(
                name=name,
                level=level,
                description=desc,
                requires_auth=requires_auth
            )

    def register_operation(
        self,
        name: str,
        level: OperationLevel,
        description: str = "",
        requires_auth: bool = False
    ):
        """
        注册操作

        Args:
            name: 操作名称
            level: 安全级别
            description: 操作描述
            requires_auth: 是否需要认证
        """
        self._operations[name] = Operation(
            name=name,
            level=level,
            description=description,
            requires_auth=requires_auth
        )

    def check_operation(self, operation_name: str) -> bool:
        """
        检查操作是否允许执行

        Args:
            operation_name: 操作名称

        Returns:
            是否允许执行
        """
        if operation_name not in self._operations:
            return False

        op = self._operations[operation_name]

        # SAFE级别直接允许
        if op.level == OperationLevel.SAFE:
            return True

        # 需要认证的操作
        if op.requires_auth:
            if not self._dual_password_verified:
                return False

        # CAUTION级别
        if op.level == OperationLevel.CAUTION:
            if self.gentle_mode:
                if self._confirm_callback:
                    return self._confirm_callback(operation_name, op.description)
                return False
            return True

        # DANGEROUS级别
        if op.level == OperationLevel.DANGEROUS:
            if self.gentle_mode:
                return False
            # 需要认证的操作，认证通过且非温和模式下允许
            if op.requires_auth and self._dual_password_verified:
                if self._confirm_callback:
                    return self._confirm_callback(operation_name, op.description)
                return True  # 已认证且非温和模式，允许
            if self._confirm_callback:
                return self._confirm_callback(operation_name, op.description)
            return False

        return False

    def verify_dual_password(self, password1: str, password2: str) -> bool:
        """
        验证双密码

        Args:
            password1: 第一段密码
            password2: 第二段密码

        Returns:
            验证是否成功
        """
        from src.core.config import get_config

        config = get_config()
        stored_pwd1 = config.get_secure("dual_password_1")
        stored_pwd2 = config.get_secure("dual_password_2")

        # 如果未设置密码，验证失败
        if not stored_pwd1 or not stored_pwd2:
            return False

        # 验证两段密码
        pwd1_correct = self._verify_single_password(password1, stored_pwd1)
        pwd2_correct = self._verify_single_password(password2, stored_pwd2)

        if pwd1_correct and pwd2_correct:
            self._dual_password_verified = True
            self._password_1_verified = True
            self._password_2_verified = True
            return True

        return False

    def _verify_single_password(self, input_pwd: str, stored_pwd: str) -> bool:
        """验证单段密码（简单比对，可增强为哈希）"""
        # 简单比对，实际应该用哈希
        return input_pwd == stored_pwd

    def is_dual_password_set(self) -> bool:
        """检查双密码是否已设置"""
        from src.core.config import get_config

        config = get_config()
        return bool(config.get_secure("dual_password_1") and config.get_secure("dual_password_2"))

    def set_dual_password(self, password1: str, password2: str):
        """
        设置双密码

        Args:
            password1: 第一段密码
            password2: 第二段密码
        """
        from src.core.config import get_config

        config = get_config()
        config.set_secure("dual_password_1", password1)
        config.set_secure("dual_password_2", password2)

        self._dual_password_enabled = True

    def clear_dual_password_verification(self):
        """清除双密码验证状态"""
        self._dual_password_verified = False
        self._password_1_verified = False
        self._password_2_verified = False

    def authorize_network(self):
        """授权网络使用"""
        self._network_authorized = True
        self._authorization_timestamp = datetime.now()

    def is_network_authorized(self) -> bool:
        """检查网络是否已授权"""
        return self._network_authorized

    def clear_authorization(self):
        """清除授权状态"""
        self._network_authorized = False
        self._authorization_timestamp = None
        self.clear_dual_password_verification()

    def set_confirm_callback(self, callback: Callable[[str, str], bool]):
        """设置确认回调"""
        self._confirm_callback = callback

    def get_operation_level(self, operation_name: str) -> Optional[OperationLevel]:
        """获取操作的安全级别"""
        if operation_name not in self._operations:
            return None
        return self._operations[operation_name].level

    def list_operations(self) -> List[Operation]:
        """列出所有注册的操作"""
        return list(self._operations.values())

    def set_gentle_mode(self, enabled: bool):
        """设置温和模式"""
        self.gentle_mode = enabled

    def is_verified(self) -> bool:
        """检查是否已验证双密码"""
        return self._dual_password_verified

    def get_status(self) -> Dict:
        """获取安全状态"""
        return {
            "gentle_mode": self.gentle_mode,
            "dual_password_enabled": self._dual_password_enabled,
            "dual_password_verified": self._dual_password_verified,
            "network_authorized": self._network_authorized,
            "authorization_timestamp": self._authorization_timestamp.isoformat() if self._authorization_timestamp else None
        }

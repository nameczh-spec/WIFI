"""
高级授权练习模式模块
管理高级练习的授权、验证和安全约束
仅供学习研究，在自己的网络上进行温和练习
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from datetime import datetime, timedelta
from enum import Enum

from src.core.logger import get_logger

logger = get_logger("advanced_practice")


class PracticeMode(Enum):
    """练习模式"""
    MONITORING = "monitoring"      # 仅监听模式（最安全）
    WEBPACK = "wepcrack"          # WEP破解练习（仅自己的WEP网络）
    HANDSHAKE = "handshake"       # 握手捕获练习（仅自己的网络）
    DEAUTH_TEST = "deauth_test"    # Deauth测试（仅自己的设备，需谨慎）


class PracticeStatus(Enum):
    """练习状态"""
    NOT_AUTHORIZED = "not_authorized"  # 未授权
    PASSWORD1 = "password1"           # 需第一密码
    PASSWORD2 = "password2"           # 需第二密码
    NETWORK_CONFIRM = "network_confirm"  # 需网络确认
    AUTHORIZED = "authorized"         # 已授权
    EXPIRED = "expired"               # 授权过期


@dataclass
class PracticeSession:
    """练习会话"""
    session_id: str
    mode: PracticeMode
    start_time: datetime
    expires_at: datetime
    target_network: str = ""
    authorized_by: str = ""
    is_active: bool = False
    actions_log: List[Dict] = field(default_factory=list)

    def log_action(self, action: str, details: str = ""):
        """记录操作日志"""
        self.actions_log.append({
            "time": datetime.now().isoformat(),
            "action": action,
            "details": details
        })


class AdvancedPracticeManager:
    """
    高级练习模式管理器
    负责授权验证、会话管理和安全约束
    """

    # 最大授权时长（1小时）
    MAX_AUTH_DURATION = 3600  # seconds

    # 每次操作的最小间隔（防止过快操作）
    MIN_ACTION_INTERVAL = 2  # seconds

    def __init__(self, safety_manager, config_manager):
        """
        初始化高级练习管理器

        Args:
            safety_manager: 安全管理器
            config_manager: 配置管理器
        """
        self.safety = safety_manager
        self.config = config_manager

        # 当前会话
        self._current_session: Optional[PracticeSession] = None

        # 网络确认状态
        self._network_confirmed = False
        self._network_confirm_time: Optional[datetime] = None

        # 上次操作时间
        self._last_action_time = 0

        # 操作计数（防止滥用）
        self._action_count = 0
        self._max_actions_per_session = 100

    @property
    def is_authorized(self) -> bool:
        """是否已授权"""
        if not self._current_session:
            return False
        if not self._current_session.is_active:
            return False
        if datetime.now() > self._current_session.expires_at:
            return False
        return True

    @property
    def current_session(self) -> Optional[PracticeSession]:
        """获取当前会话"""
        return self._current_session

    def get_authorization_status(self) -> Dict:
        """获取授权状态"""
        status = PracticeStatus.NOT_AUTHORIZED

        if not self.safety._dual_password_enabled:
            status = PracticeStatus.NETWORK_CONFIRM
        elif not self.safety._password_1_verified:
            status = PracticeStatus.PASSWORD1
        elif not self.safety._password_2_verified:
            status = PracticeStatus.PASSWORD2
        elif not self._network_confirmed:
            status = PracticeStatus.NETWORK_CONFIRM
        elif self.is_authorized:
            status = PracticeStatus.AUTHORIZED

        session_info = None
        if self._current_session:
            session_info = {
                "session_id": self._current_session.session_id,
                "mode": self._current_session.mode.value,
                "start_time": self._current_session.start_time.isoformat(),
                "expires_at": self._current_session.expires_at.isoformat(),
                "target_network": self._current_session.target_network,
                "is_active": self._current_session.is_active,
                "action_count": len(self._current_session.actions_log),
            }

        return {
            "status": status.value,
            "description": self._get_status_description(status),
            "dual_password_enabled": self.safety._dual_password_enabled,
            "password1_verified": self.safety._password_1_verified,
            "password2_verified": self.safety._password_2_verified,
            "network_confirmed": self._network_confirmed,
            "session": session_info,
            "warning": "高级练习模式仅供学习研究，仅限在自己的网络上使用",
        }

    def _get_status_description(self, status: PracticeStatus) -> str:
        """获取状态描述"""
        descriptions = {
            PracticeStatus.NOT_AUTHORIZED: "未授权",
            PracticeStatus.PASSWORD1: "需要验证第一组密码",
            PracticeStatus.PASSWORD2: "需要验证第二组密码",
            PracticeStatus.NETWORK_CONFIRM: "需要确认网络授权声明",
            PracticeStatus.AUTHORIZED: "已授权，可以进行练习",
            PracticeStatus.EXPIRED: "授权已过期",
        }
        return descriptions.get(status, "未知状态")

    def verify_password_1(self, password: str) -> bool:
        """验证第一组密码"""
        # 调用安全管理器的验证逻辑
        try:
            result = self.safety.verify_dual_password_1(password)
            return result
        except Exception as e:
            logger.error(f"验证第一密码失败: {e}")
            return False

    def verify_password_2(self, password: str) -> bool:
        """验证第二组密码"""
        try:
            result = self.safety.verify_dual_password_2(password)
            return result
        except Exception as e:
            logger.error(f"验证第二密码失败: {e}")
            return False

    def confirm_network_authorization(self, user_confirmation: bool,
                                       target_network: str = "",
                                       user_statement: str = "") -> bool:
        """
        确认网络授权

        Args:
            user_confirmation: 用户是否确认
            target_network: 目标网络SSID/BSSID（用于记录）
            user_statement: 用户声明（如"这是我的网络"）

        Returns:
            是否确认成功
        """
        if not user_confirmation:
            return False

        # 记录确认
        self._network_confirmed = True
        self._network_confirm_time = datetime.now()

        logger.warning(
            f"网络授权确认 - 目标: {target_network}, "
            f"声明: {user_statement}, "
            f"时间: {self._network_confirm_time}"
        )

        return True

    def start_practice_session(self, mode: PracticeMode,
                               target_network: str = "") -> Dict:
        """
        开始练习会话

        Args:
            mode: 练习模式
            target_network: 目标网络

        Returns:
            会话信息
        """
        # 检查授权状态
        if self.safety._dual_password_enabled:
            if not self.safety._dual_password_verified:
                return {
                    "success": False,
                    "error": "请先完成双密码验证",
                    "required_step": "dual_password"
                }

        if not self._network_confirmed:
            return {
                "success": False,
                "error": "请先确认网络授权声明",
                "required_step": "network_confirm"
            }

        if self.safety.gentle_mode and mode in [
            PracticeMode.DEAUTH_TEST,
            PracticeMode.WEBPACK,
        ]:
            # 温和模式下只允许监听和握手捕获
            if mode == PracticeMode.DEAUTH_TEST:
                return {
                    "success": False,
                    "error": "温和模式下不支持发送数据包的操作",
                    "hint": "如需进行此练习，请关闭温和模式并了解相关风险"
                }

        # 创建会话
        import uuid
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now()
        expires = now + timedelta(seconds=self.MAX_AUTH_DURATION)

        self._current_session = PracticeSession(
            session_id=session_id,
            mode=mode,
            start_time=now,
            expires_at=expires,
            target_network=target_network,
            authorized_by="user",
            is_active=True
        )

        self._action_count = 0
        self._last_action_time = 0

        self._current_session.log_action(
            "session_start",
            f"模式: {mode.value}, 目标: {target_network}"
        )

        logger.warning(
            f"高级练习会话开始 - ID: {session_id}, "
            f"模式: {mode.value}, "
            f"目标: {target_network}, "
            f"过期时间: {expires}"
        )

        return {
            "success": True,
            "session_id": session_id,
            "mode": mode.value,
            "expires_at": expires.isoformat(),
            "max_actions": self._max_actions_per_session,
            "warning": self._get_safety_warning(mode)
        }

    def _get_safety_warning(self, mode: PracticeMode) -> str:
        """获取安全警告"""
        warnings = {
            PracticeMode.MONITORING:
                "监听模式：仅被动接收信号，不会发送任何数据包，相对安全。",
            PracticeMode.WEBPACK:
                "WEP破解练习：需要发送数据包，可能对网络造成影响。仅限在自己的WEP网络上使用。",
            PracticeMode.HANDSHAKE:
                "握手捕获练习：仅被动监听，不会主动发送数据包。",
            PracticeMode.DEAUTH_TEST:
                "Deauth测试：会发送解除认证帧，会导致设备断网。仅限测试自己的设备。",
        }
        return warnings.get(mode, "请谨慎操作，仅限学习使用")

    def check_action_allowed(self, action: str) -> Dict:
        """
        检查操作是否被允许

        Args:
            action: 操作名称

        Returns:
            检查结果
        """
        # 检查会话是否存在且有效
        if not self.is_authorized:
            return {
                "allowed": False,
                "reason": "未授权或授权已过期",
            }

        # 检查操作频率限制
        now = time.time()
        if now - self._last_action_time < self.MIN_ACTION_INTERVAL:
            return {
                "allowed": False,
                "reason": f"操作过于频繁，请等待{self.MIN_ACTION_INTERVAL}秒",
            }

        # 检查操作次数限制
        if self._action_count >= self._max_actions_per_session:
            return {
                "allowed": False,
                "reason": f"已达到本次会话最大操作次数 ({self._max_actions_per_session})",
            }

        # 通过安全管理器检查
        allowed = self.safety.can_perform(action)
        if not allowed:
            return {
                "allowed": False,
                "reason": "操作被安全策略阻止",
            }

        return {
            "allowed": True,
            "remaining_actions": self._max_actions_per_session - self._action_count,
        }

    def record_action(self, action: str, details: str = ""):
        """
        记录操作

        Args:
            action: 操作名称
            details: 详情
        """
        self._last_action_time = time.time()
        self._action_count += 1

        if self._current_session:
            self._current_session.log_action(action, details)

        logger.info(f"高级练习操作: {action} - {details}")

    def end_session(self) -> Dict:
        """
        结束当前会话

        Returns:
            会话总结
        """
        if not self._current_session:
            return {"success": False, "error": "没有活动会话"}

        self._current_session.is_active = False
        self._current_session.log_action("session_end", "用户主动结束")

        session_info = {
            "session_id": self._current_session.session_id,
            "mode": self._current_session.mode.value,
            "duration": (datetime.now() - self._current_session.start_time).total_seconds(),
            "total_actions": len(self._current_session.actions_log),
            "actions_log": self._current_session.actions_log,
        }

        logger.warning(
            f"高级练习会话结束 - ID: {session_info['session_id']}, "
            f"操作数: {session_info['total_actions']}"
        )

        self._current_session = None
        self._network_confirmed = False
        self._network_confirm_time = None
        self._action_count = 0

        return {
            "success": True,
            "session_summary": session_info
        }

    def extend_session(self) -> Dict:
        """
        延长会话时间（需要重新确认）

        Returns:
            新的过期时间
        """
        if not self.is_authorized:
            return {"success": False, "error": "没有活动会话或已过期"}

        # 延长30分钟
        self._current_session.expires_at = datetime.now() + timedelta(minutes=30)
        self._current_session.log_action("session_extend", "延长30分钟")

        return {
            "success": True,
            "expires_at": self._current_session.expires_at.isoformat()
        }

    def get_practice_modes(self) -> List[Dict]:
        """获取可用的练习模式列表"""
        modes = [
            {
                "id": PracticeMode.MONITORING.value,
                "name": "监听模式",
                "description": "仅被动监听WiFi信号，不发送任何数据包，最安全的练习模式",
                "risk_level": "low",
                "requires_gentle_off": False,
                "icon": "radio"
            },
            {
                "id": PracticeMode.HANDSHAKE.value,
                "name": "握手捕获练习",
                "description": "被动捕获WPA握手包，用于学习密码验证原理",
                "risk_level": "low",
                "requires_gentle_off": False,
                "icon": "handshake"
            },
            {
                "id": PracticeMode.WEBPACK.value,
                "name": "WEP破解练习",
                "description": "练习WEP加密破解（仅限自己的WEP网络）",
                "risk_level": "medium",
                "requires_gentle_off": True,
                "icon": "key"
            },
            {
                "id": PracticeMode.DEAUTH_TEST.value,
                "name": "Deauth测试",
                "description": "测试解除认证帧（仅限自己的设备，会导致断网）",
                "risk_level": "high",
                "requires_gentle_off": True,
                "icon": "alert"
            },
        ]

        # 如果在温和模式下，标记风险较高的模式为不可用
        if self.safety.gentle_mode:
            for m in modes:
                if m["requires_gentle_off"]:
                    m["available"] = False
                    m["unavailable_reason"] = "温和模式下不支持此操作"
                else:
                    m["available"] = True
        else:
            for m in modes:
                m["available"] = True

        return modes

    def get_safety_guidelines(self) -> List[str]:
        """获取安全准则"""
        return [
            "⚠️ 高级练习模式仅供学习研究使用",
            "⚠️ 只能在你拥有所有权或已获得明确授权的网络上进行",
            "⚠️ 未经授权访问他人网络是违法行为",
            "⚠️ 建议在专门的测试环境中进行练习（如自己的路由器）",
            "⚠️ 每次练习前请确认你了解操作的后果",
            "⚠️ 优先使用监听模式进行学习，发送数据包的操作请谨慎",
            "⚠️ 练习结束后请及时结束会话",
            "⚠️ 所有操作都会被记录，用于审计和学习追踪",
        ]


# 全局实例
_practice_manager: Optional[AdvancedPracticeManager] = None


def get_advanced_practice_manager(safety_manager=None,
                                   config_manager=None) -> AdvancedPracticeManager:
    """获取高级练习管理器单例"""
    global _practice_manager
    if _practice_manager is None:
        if safety_manager is None or config_manager is None:
            # 使用默认值
            from src.core.safety import SafetyManager
            from src.core.config import get_config
            safety_manager = SafetyManager(get_config())
            config_manager = get_config()
        _practice_manager = AdvancedPracticeManager(safety_manager, config_manager)
    return _practice_manager

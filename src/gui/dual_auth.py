"""
双密码验证对话框 - WiFi可视化安全学习工具 v2
科幻风格的双密码验证界面
"""

from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (
    QColor, QPainter, QLinearGradient, QRadialGradient,
    QBrush, QPen, QFont, QPalette
)


class CyberpunkPasswordInput(QLineEdit):
    """
    科幻风格密码输入框
    带发光效果和强度指示器
    """

    def __init__(self, placeholder: str = "输入密码", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.Password)
        self._setup_style()
        self._setup_glow()

    def _setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(10, 10, 30, 0.9);
                color: #00fff5;
                border: 2px solid #16213e;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
                font-family: 'Consolas', 'Courier New', monospace;
                letter-spacing: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #00fff5;
                background: rgba(10, 10, 40, 0.95);
            }
        """)

    def _setup_glow(self):
        """设置发光效果"""
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 255, 245, 50))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

    def set_cyber_color(self, color: str):
        """设置科幻风格颜色"""
        glow = self.graphicsEffect()
        if glow:
            glow.setColor(QColor(color))

    def show_password(self, show: bool):
        """显示/隐藏密码"""
        if show:
            self.setEchoMode(QLineEdit.Normal)
        else:
            self.setEchoMode(QLineEdit.Password)


class PasswordStrengthBar(QProgressBar):
    """
    密码强度条
    科幻风格渐变显示
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(10)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(False)
        self._update_style(0)

    def _update_style(self, value: int):
        """根据值更新样式"""
        if value < 30:
            color = "#ff3333"
            text = "弱"
        elif value < 60:
            color = "#ffcc00"
            text = "中"
        elif value < 80:
            color = "#00ff00"
            text = "强"
        else:
            color = "#00fff5"
            text = "很强"

        self.setFormat(f"密码强度: {text}")
        self.setTextVisible(True)

        self.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid #16213e;
                border-radius: 5px;
                text-align: center;
                color: {color};
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 #ff00ff);
                border-radius: 5px;
            }}
        """)

    def set_strength(self, value: int):
        """设置密码强度"""
        self.setValue(value)
        self._update_style(value)

    def check_password_strength(self, password: str) -> int:
        """检测密码强度"""
        if not password:
            return 0

        score = 0

        # 长度
        length = len(password)
        if length >= 12:
            score += 25
        elif length >= 10:
            score += 18
        elif length >= 8:
            score += 12
        elif length >= 6:
            score += 8
        else:
            score += 3

        # 复杂度
        import re
        has_digit = bool(re.search(r'\d', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if has_digit:
            score += 15
        if has_lower:
            score += 15
        if has_upper:
            score += 20
        if has_special:
            score += 25

        # 检查常见弱密码
        common_weak = {
            '123456', 'password', 'admin', '12345678',
            'qwerty', '111111', '000000', '123456789'
        }
        if password.lower() in common_weak:
            score = max(5, score - 40)

        return min(100, score)


class DualPasswordSetupDialog(QDialog):
    """
    双密码设置对话框
    科幻风格界面
    """

    password_set = pyqtSignal(str, str)  # 密码1, 密码2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置双密码")
        self.setFixedSize(500, 520)
        self.setModal(True)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """设置UI"""
        # 对话框背景
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a1a, stop:1 #1a1a2e);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("🔐 设置双密码验证")
        title.setStyleSheet("""
            color: #ff00ff;
            font-size: 24px;
            font-weight: bold;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 说明
        desc = QLabel("为保障高级功能安全，请设置两段独立密码。\n两段密码都正确才可解锁高级功能。")
        desc.setStyleSheet("""
            color: #00fff5;
            font-size: 13px;
        """)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #16213e;")
        layout.addWidget(line)

        # 第一段密码
        layout.addWidget(self._create_label("第一段密码"))
        self.pwd1_input = CyberpunkPasswordInput("请输入第一段密码")
        layout.addWidget(self.pwd1_input)

        # 确认第一段密码
        layout.addWidget(self._create_label("确认第一段密码"))
        self.pwd1_confirm = CyberpunkPasswordInput("再次输入第一段密码")
        layout.addWidget(self.pwd1_confirm)

        # 第二段密码
        layout.addWidget(self._create_label("第二段密码"))
        self.pwd2_input = CyberpunkPasswordInput("请输入第二段密码")
        layout.addWidget(self.pwd2_input)

        # 确认第二段密码
        layout.addWidget(self._create_label("确认第二段密码"))
        self.pwd2_confirm = CyberpunkPasswordInput("再次输入第二段密码")
        layout.addWidget(self.pwd2_confirm)

        # 密码强度
        self.strength_bar = PasswordStrengthBar()
        layout.addWidget(self.strength_bar)

        # 状态提示
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff6600; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = self._create_cyber_button("取消", "#ff3333")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = self._create_cyber_button("确认设置", "#00ff00")
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)

    def _create_label(self, text: str) -> QLabel:
        """创建标签"""
        label = QLabel(text)
        label.setStyleSheet("""
            color: #00fff5;
            font-size: 14px;
            padding: 5px 0;
        """)
        return label

    def _create_cyber_button(self, text: str, color: str) -> QPushButton:
        """创建科幻风格按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(26, 26, 46, 0.9);
                color: {color};
                border: 2px solid {color};
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {color};
                color: #0a0a1a;
            }}
        """)
        return btn

    def _setup_connections(self):
        """设置信号连接"""
        self.pwd2_input.textChanged.connect(self._on_password_changed)

    def _on_password_changed(self, text: str):
        """密码变化时更新强度"""
        # 综合两段密码计算强度
        pwd1 = self.pwd1_input.text()
        pwd2 = self.pwd2_input.text()
        combined = pwd1 + pwd2
        strength = self.strength_bar.check_password_strength(combined)
        self.strength_bar.set_strength(strength)

    def _on_confirm(self):
        """确认设置"""
        pwd1 = self.pwd1_input.text()
        pwd1c = self.pwd1_confirm.text()
        pwd2 = self.pwd2_input.text()
        pwd2c = self.pwd2_confirm.text()

        # 验证
        if not pwd1 or not pwd2:
            self._show_error("两段密码都不能为空")
            return

        if len(pwd1) < 6 or len(pwd2) < 6:
            self._show_error("密码长度至少6位")
            return

        if pwd1 != pwd1c:
            self._show_error("第一段密码两次输入不一致")
            return

        if pwd2 != pwd2c:
            self._show_error("第二段密码两次输入不一致")
            return

        if pwd1 == pwd2:
            self._show_error("两段密码不能相同")
            return

        # 设置成功
        self.password_set.emit(pwd1, pwd2)
        self.accept()

    def _show_error(self, message: str):
        """显示错误信息"""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: #ff3333; font-size: 12px;")

        # 3秒后清除
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))


class DualPasswordVerifyDialog(QDialog):
    """
    双密码验证对话框
    科幻风格解锁界面
    """

    verified = pyqtSignal()  # 验证成功信号

    def __init__(self, parent=None, max_attempts: int = 5):
        super().__init__(parent)
        self.setWindowTitle("身份验证")
        self.setFixedSize(480, 450)
        self.setModal(True)

        self._attempts = 0
        self._max_attempts = max_attempts
        self._current_step = 1  # 当前验证步骤(1或2)
        self._password1_correct = False

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a1a, stop:1 #1a1a2e);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("🔓 高级功能解锁")
        title.setStyleSheet("""
            color: #ff00ff;
            font-size: 22px;
            font-weight: bold;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 步骤指示器
        steps_layout = QHBoxLayout()
        self.step1_label = self._create_step_label("第一段密码", True)
        self.step2_label = self._create_step_label("第二段密码", False)
        steps_layout.addWidget(self.step1_label)
        steps_layout.addWidget(self.step2_label)
        layout.addLayout(steps_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #16213e;")
        layout.addWidget(line)

        # 提示
        self.hint_label = QLabel("请输入第一段密码以继续")
        self.hint_label.setStyleSheet("""
            color: #00fff5;
            font-size: 14px;
        """)
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

        # 密码输入
        self.password_input = CyberpunkPasswordInput("请输入密码")
        layout.addWidget(self.password_input)

        # 显示密码切换
        show_layout = QHBoxLayout()
        self.show_pwd_btn = QPushButton("👁 显示密码")
        self.show_pwd_btn.setCheckable(True)
        self.show_pwd_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #00fff5;
                border: 1px solid #16213e;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                border: 1px solid #00fff5;
            }
        """)
        show_layout.addStretch()
        show_layout.addWidget(self.show_pwd_btn)
        layout.addLayout(show_layout)

        # 剩余尝试次数
        self.attempts_label = QLabel(f"剩余尝试次数: {self._max_attempts}")
        self.attempts_label.setStyleSheet("color: #ff6600; font-size: 12px;")
        self.attempts_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attempts_label)

        # 状态
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = self._create_cyber_button("取消", "#ff3333")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.verify_btn = self._create_cyber_button("验证", "#00ff00")
        self.verify_btn.clicked.connect(self._on_verify)
        btn_layout.addWidget(self.verify_btn)

        layout.addLayout(btn_layout)

    def _create_step_label(self, text: str, active: bool) -> QLabel:
        """创建步骤标签"""
        label = QLabel()
        if active:
            label.setText(f"● {text}")
            label.setStyleSheet("color: #00fff5; font-size: 13px; font-weight: bold;")
        else:
            label.setText(f"○ {text}")
            label.setStyleSheet("color: #666; font-size: 13px;")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _create_cyber_button(self, text: str, color: str) -> QPushButton:
        """创建科幻风格按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(26, 26, 46, 0.9);
                color: {color};
                border: 2px solid {color};
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {color};
                color: #0a0a1a;
            }}
        """)
        return btn

    def _setup_connections(self):
        """设置连接"""
        self.show_pwd_btn.toggled.connect(self._toggle_password_visibility)
        self.password_input.returnPressed.connect(self._on_verify)

    def _toggle_password_visibility(self, checked: bool):
        """切换密码可见性"""
        self.password_input.show_password(checked)
        self.show_pwd_btn.setText("👁 隐藏密码" if checked else "👁 显示密码")

    def _on_verify(self):
        """验证密码"""
        from src.core.config import get_config
        config = get_config()
        stored_pwd1 = config.get_secure("dual_password_1")
        stored_pwd2 = config.get_secure("dual_password_2")

        if not stored_pwd1 or not stored_pwd2:
            self._show_error("尚未设置双密码，请先在设置中配置")
            return

        password = self.password_input.text()

        if not password:
            self._show_error("请输入密码")
            return

        if self._current_step == 1:
            # 验证第一段密码
            if password == stored_pwd1:
                self._password1_correct = True
                self._current_step = 2
                self._advance_step()
            else:
                self._wrong_password()
        else:
            # 验证第二段密码
            if password == stored_pwd2:
                self._verification_success()
            else:
                self._wrong_password()

    def _advance_step(self):
        """进入下一步"""
        self.password_input.clear()
        self.hint_label.setText("请输入第二段密码以完成验证")
        self.hint_label.setStyleSheet("color: #00ff00; font-size: 14px;")

        # 更新步骤标签
        self.step1_label.setText("✓ 第一段密码")
        self.step1_label.setStyleSheet("color: #00ff00; font-size: 13px; font-weight: bold;")
        self.step2_label.setText("● 第二段密码")
        self.step2_label.setStyleSheet("color: #00fff5; font-size: 13px; font-weight: bold;")

        # 发光效果
        self.password_input.set_cyber_color("#00ff00")

        self.status_label.setText("✓ 第一段密码正确")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 12px;")

    def _wrong_password(self):
        """密码错误"""
        self._attempts += 1
        remaining = self._max_attempts - self._attempts

        if remaining <= 0:
            self._show_error(f"验证失败次数过多，请稍后再试")
            self.verify_btn.setEnabled(False)
            QTimer.singleShot(5000, self.reject)
            return

        self.attempts_label.setText(f"剩余尝试次数: {remaining}")
        self.attempts_label.setStyleSheet("color: #ff3333; font-size: 12px;")

        self._show_error(f"密码错误，还剩 {remaining} 次机会")
        self.password_input.clear()

        # 红色闪烁效果
        self.password_input.set_cyber_color("#ff3333")
        QTimer.singleShot(500, lambda: self.password_input.set_cyber_color("#00fff5"))

    def _verification_success(self):
        """验证成功"""
        self.status_label.setText("✓ 验证成功！正在解锁高级功能...")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 14px;")

        # 绿色发光
        self.password_input.set_cyber_color("#00ff00")

        # 延迟发送成功信号
        QTimer.singleShot(1000, self._emit_success)

    def _emit_success(self):
        """发送验证成功信号"""
        self.verified.emit()
        self.accept()

    def _show_error(self, message: str):
        """显示错误"""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: #ff3333; font-size: 12px;")


class AuthorizationDialog(QDialog):
    """
    授权确认对话框
    确认用户有权限在指定网络上进行操作
    """

    authorized = pyqtSignal()  # 授权确认信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("授权确认")
        self.setFixedSize(520, 480)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a1a, stop:1 #1a1a2e);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # 警告标题
        title = QLabel("⚠ 授权确认")
        title.setStyleSheet("""
            color: #ff6600;
            font-size: 22px;
            font-weight: bold;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 警告框
        warning_box = QFrame()
        warning_box.setStyleSheet("""
            QFrame {
                background: rgba(255, 102, 0, 0.1);
                border: 2px solid #ff6600;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        warning_layout = QVBoxLayout(warning_box)

        warning_text = QLabel("""
            <h3 style='color:#ff6600;'>重要声明</h3>
            <p style='color:#00fff5;'>
            使用高级功能需要您确认：<br><br>
            <b>1.</b> 您拥有要操作的网络的所有权<br>
            <b>2.</b> 您已获得网络管理员的书面授权<br>
            <b>3.</b> 您将遵守当地网络安全法律法规<br>
            <b>4.</b> 您仅用于学习研究目的<br>
            <b>5.</b> 您将对自己的行为负责
            </p>
        """)
        warning_text.setTextFormat(Qt.RichText)
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_box)

        # 免责声明
        disclaimer = QLabel("""
            <p style='color:#888; font-size:11px;'>
            本工具仅用于学习研究。因违规使用造成的任何后果，
            由使用者自行承担，与本工具开发者无关。
            </p>
        """)
        disclaimer.setTextFormat(Qt.RichText)
        disclaimer.setAlignment(Qt.AlignCenter)
        layout.addWidget(disclaimer)

        # 确认勾选
        self.confirm_check1 = QCheckBox("我确认已获得网络所有权或授权")
        self.confirm_check1.setStyleSheet("color: #00fff5;")
        layout.addWidget(self.confirm_check1)

        self.confirm_check2 = QCheckBox("我将遵守法律法规，仅用于学习研究")
        self.confirm_check2.setStyleSheet("color: #00fff5;")
        layout.addWidget(self.confirm_check2)

        self.confirm_check3 = QCheckBox("我已阅读并同意免责声明")
        self.confirm_check3.setStyleSheet("color: #00fff5;")
        layout.addWidget(self.confirm_check3)

        # 状态
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancel_btn = self._create_cyber_button("取消", "#ff3333")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.authorize_btn = self._create_cyber_button("确认授权", "#00ff00")
        self.authorize_btn.clicked.connect(self._on_authorize)
        btn_layout.addWidget(self.authorize_btn)

        layout.addLayout(btn_layout)

    def _create_cyber_button(self, text: str, color: str) -> QPushButton:
        """创建科幻风格按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(26, 26, 46, 0.9);
                color: {color};
                border: 2px solid {color};
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {color};
                color: #0a0a1a;
            }}
        """)
        return btn

    def _on_authorize(self):
        """确认授权"""
        if not all([
            self.confirm_check1.isChecked(),
            self.confirm_check2.isChecked(),
            self.confirm_check3.isChecked()
        ]):
            self.status_label.setText("❌ 请勾选所有确认项")
            self.status_label.setStyleSheet("color: #ff3333; font-size: 12px;")
            return

        self.authorized.emit()
        self.accept()


# 补充导入
from PyQt5.QtWidgets import QCheckBox

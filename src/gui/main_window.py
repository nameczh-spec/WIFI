"""
主窗口 - WiFi可视化安全学习工具 v2
科幻风格界面
"""

import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QTextEdit,
    QSplitter, QFrame, QScrollArea, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QLinearGradient, QBrush, QPen

from src.core.logger import get_logger
from src.core.config import ConfigManager
from src.core.safety import SafetyManager
from src.modules.wifi_scanner import get_wifi_scanner
from src.modules.security_eval import NetworkSecurityEvaluator
from src.gui.cyber_widgets import (
    CyberCard, StatusIndicator, CyberProgressBar, CyberTag,
    StatCard, GaugeWidget, CyberDivider, DataPanel,
    CyberSwitch, ParticleBackground
)

logger = get_logger("main_window")


class CyberpunkButton(QPushButton):
    """
    科幻风格按钮
    """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00fff5;
                border: 2px solid #00fff5;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16213e, stop:1 #0f3460);
                border: 2px solid #ff00ff;
                color: #ff00ff;
            }
            QPushButton:pressed {
                background: #0f3460;
            }
        """)


class CyberpunkLineEdit(QLineEdit):
    """
    科幻风格输入框
    """

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(placeholder, parent)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(26, 26, 46, 0.9);
                color: #00fff5;
                border: 2px solid #16213e;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #00fff5;
            }
        """)


class CyberpunkTextEdit(QTextEdit):
    """
    科幻风格文本框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background: rgba(26, 26, 46, 0.9);
                color: #00fff5;
                border: 2px solid #16213e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
        """)


class MainWindow(QMainWindow):
    """
    主窗口
    """

    def __init__(self, config: ConfigManager, safety: SafetyManager):
        super().__init__()
        self.config = config
        self.safety = safety
        self.ai_client = None  # 延迟初始化

        self._init_ui()
        self._init_modules()
        self._start_background_animation()

    def _init_ui(self):
        """初始化UI"""
        # 窗口设置
        self.setWindowTitle("WiFi可视化安全学习工具 v2.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)

        # 深色背景
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(10, 10, 30))
        palette.setColor(QPalette.WindowText, QColor(0, 255, 245))
        self.setPalette(palette)

        # 中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧导航
        nav_widget = self._create_navigation()
        main_layout.addWidget(nav_widget, 1)

        # 右侧内容
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 5)

        # 创建各页面
        self._create_pages()

    def _create_navigation(self) -> QWidget:
        """创建导航栏"""
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0a0a1a, stop:1 #1a1a2e);
            border-right: 2px solid #16213e;
        """)

        layout = QVBoxLayout(nav_widget)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        # 标题
        title = QLabel("WiFi安全")
        title.setStyleSheet("""
            color: #ff00ff;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("可视化学习平台")
        subtitle.setStyleSheet("""
            color: #00fff5;
            font-size: 12px;
            padding: 5px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # 导航按钮
        self.nav_buttons = {}

        nav_items = [
            ("首页", self._show_home),
            ("WiFi扫描", self._show_wifi_scan),
            ("教学模式", self._show_learning),
            ("安全评估", self._show_security),
            ("AI助手", self._show_ai_assistant),
            ("攻防演练", self._show_attack_defense),
            ("设置", self._show_settings),
        ]

        for name, callback in nav_items:
            btn = CyberpunkButton(name)
            btn.clicked.connect(callback)
            self.nav_buttons[name] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # 状态栏
        status_layout = QVBoxLayout()
        gentle_label = QLabel(f"温和模式: {'开启' if self.safety.gently_mode else '关闭'}")
        gentle_label.setStyleSheet("color: #00ff00; font-size: 11px;")
        gentle_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(gentle_label)

        layout.addLayout(status_layout)

        return nav_widget

    def _create_pages(self):
        """创建各页面"""
        # 首页
        self.home_page = self._create_home_page()
        self.content_stack.addWidget(self.home_page)

        # WiFi扫描页
        self.wifi_scan_page = self._create_wifi_scan_page()
        self.content_stack.addWidget(self.wifi_scan_page)

        # 教学模式页
        self.learning_page = self._create_learning_page()
        self.content_stack.addWidget(self.learning_page)

        # 安全评估页
        self.security_page = self._create_security_page()
        self.content_stack.addWidget(self.security_page)

        # AI助手页
        self.ai_page = self._create_ai_page()
        self.content_stack.addWidget(self.ai_page)

        # 攻防演练页
        self.attack_defense_page = self._create_attack_defense_page()
        self.content_stack.addWidget(self.attack_defense_page)

        # 设置页
        self.settings_page = self._create_settings_page()
        self.content_stack.addWidget(self.settings_page)

        # 默认显示首页
        self.content_stack.setCurrentWidget(self.home_page)

    def _create_home_page(self) -> QWidget:
        """创建首页 - 数据仪表板"""
        page = QWidget()

        # 粒子背景
        self.particle_bg = ParticleBackground(page)
        self.particle_bg.setGeometry(page.rect())

        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 欢迎区域
        welcome_card = CyberCard()
        welcome_layout = QVBoxLayout()
        welcome_layout.setSpacing(10)

        title = QLabel("WiFi可视化安全学习工具 v2.0")
        title.setStyleSheet("""
            color: #ff00ff;
            font-size: 28px;
            font-weight: bold;
        """)
        title.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(title)

        subtitle = QLabel("科幻风格的WiFi安全可视化学习平台 | 仅供学习研究使用")
        subtitle.setStyleSheet("""
            color: #00fff5;
            font-size: 14px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(subtitle)

        # 状态指示
        status_row = QHBoxLayout()
        status_row.addStretch()

        gentle_status = StatusIndicator(
            "active" if self.safety.gently_mode else "offline",
            f"温和模式: {'开启' if self.safety.gently_mode else '关闭'}"
        )
        status_row.addWidget(gentle_status)

        ai_status = StatusIndicator("offline", "AI: 未配置")
        status_row.addWidget(ai_status)

        status_row.addStretch()
        welcome_layout.addLayout(status_row)

        welcome_card.add_layout(welcome_layout) if hasattr(welcome_card, 'add_layout') else welcome_card.layout().addLayout(welcome_layout)
        main_layout.addWidget(welcome_card)

        # 统计卡片区域
        stats_row = QHBoxLayout()
        stats_row.setSpacing(15)

        stat1 = StatCard("已学习模块", "3", "📚", "#00fff5")
        stats_row.addWidget(stat1)

        stat2 = StatCard("扫描网络数", "0", "📡", "#ff00ff")
        stats_row.addWidget(stat2)

        stat3 = StatCard("安全评分", "--", "🛡️", "#00ff00")
        stats_row.addWidget(stat3)

        stat4 = StatCard("AI对话", "0", "🤖", "#ffcc00")
        stats_row.addWidget(stat4)

        main_layout.addLayout(stats_row)

        # 功能入口卡片
        features_card = CyberCard("快速入口")
        features_layout = QGridLayout()
        features_layout.setSpacing(15)

        features = [
            ("WiFi扫描", "被动扫描周边网络", "📡", self._show_wifi_scan),
            ("教学模式", "加密原理与过程", "📚", self._show_learning),
            ("安全评估", "自有网络检测", "🔍", self._show_security),
            ("AI助手", "智能学习指导", "🤖", self._show_ai_assistant),
            ("攻防演练", "模拟对抗学习", "⚔️", self._show_attack_defense),
            ("系统设置", "参数配置", "⚙️", self._show_settings),
        ]

        for i, (name, desc, icon, callback) in enumerate(features):
            btn = QPushButton()
            btn.setMinimumHeight(80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(22, 33, 62, 0.8);
                    border: 1px solid rgba(0, 255, 245, 0.3);
                    border-radius: 8px;
                    color: #00fff5;
                    text-align: left;
                    padding: 15px;
                }}
                QPushButton:hover {{
                    background: rgba(0, 255, 245, 0.1);
                    border: 1px solid rgba(0, 255, 245, 0.6);
                }}
                QPushButton:pressed {{
                    background: rgba(0, 255, 245, 0.2);
                }}
            """)

            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(10, 5, 10, 5)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px;")
            btn_layout.addWidget(icon_label)

            text_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #ff00ff; font-size: 15px; font-weight: bold;")
            text_layout.addWidget(name_label)

            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #8080a0; font-size: 11px;")
            text_layout.addWidget(desc_label)

            btn_layout.addLayout(text_layout)
            btn_layout.addStretch()

            btn.clicked.connect(callback)
            features_layout.addWidget(btn, i // 3, i % 3)

        features_card.add_widget(features_layout.parent() if features_layout.parent() else QWidget())
        # 修复布局
        while features_card.content_layout.count():
            features_card.content_layout.takeAt(0)
        features_card.content_layout.addLayout(features_layout)

        main_layout.addWidget(features_card)

        main_layout.addStretch()

        # 免责声明
        disclaimer = QLabel("⚠ 注意：所有功能仅用于学习研究，请遵守法律法规，仅在授权网络上进行测试")
        disclaimer.setStyleSheet("color: #ffcc00; font-size: 12px;")
        disclaimer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(disclaimer)

        return page

    def _create_wifi_scan_page(self) -> QWidget:
        """创建WiFi扫描页 - 增强科幻风格"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 标题行
        title_row = QHBoxLayout()
        title = QLabel("WiFi网络扫描")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        title_row.addWidget(title)
        title_row.addStretch()

        self.scan_status = StatusIndicator("offline", "状态: 待扫描")
        title_row.addWidget(self.scan_status)

        main_layout.addLayout(title_row)

        # 操作行
        action_row = QHBoxLayout()
        scan_btn = CyberpunkButton("开始扫描")
        scan_btn.clicked.connect(self._do_wifi_scan)
        scan_btn.setMinimumWidth(150)
        action_row.addWidget(scan_btn)

        self.scan_progress = CyberProgressBar()
        self.scan_progress.setVisible(False)
        action_row.addWidget(self.scan_progress, 1)

        self.scan_count_tag = CyberTag("发现: 0 个", "info")
        action_row.addWidget(self.scan_count_tag)

        main_layout.addLayout(action_row)

        # 结果区域 - 使用数据面板
        result_card = CyberCard("扫描结果")
        self.wifi_result = CyberpunkTextEdit()
        self.wifi_result.setReadOnly(True)
        result_card.add_widget(self.wifi_result)
        main_layout.addWidget(result_card, 1)

        # 统计信息
        stats_row = QHBoxLayout()
        stats_row.setSpacing(15)

        self.stat_total = StatCard("总网络数", "0", "📡", "#00fff5")
        stats_row.addWidget(self.stat_total)

        self.stat_wep = StatCard("WEP加密", "0", "⚠️", "#ff3333")
        stats_row.addWidget(self.stat_wep)

        self.stat_wpa = StatCard("WPA/WPA2", "0", "🛡️", "#ffcc00")
        stats_row.addWidget(self.stat_wpa)

        self.stat_wpa3 = StatCard("WPA3", "0", "🔒", "#00ff00")
        stats_row.addWidget(self.stat_wpa3)

        main_layout.addLayout(stats_row)

        return page

    def _create_learning_page(self) -> QWidget:
        """创建教学模式页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("教学模式 - WiFi安全学习")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        content = CyberpunkTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
            <h3 style='color:#00fff5;'>学习模块</h3>
            <p style='color:#ff00ff;'>1. WEP加密原理</p>
            <p style='color:#00fff5;'>学习RC4流密码和IV漏洞原理</p>

            <p style='color:#ff00ff;'>2. WPA/WPA2加密原理</p>
            <p style='color:#00fff5;'>了解四次握手和密钥交换过程</p>

            <p style='color:#ff00ff;'>3. WPA3加密原理</p>
            <p style='color:#00fff5;'>学习SAE握手机制</p>

            <p style='color:#ff00ff;'>4. 漏洞分析</p>
            <p style='color:#00fff5;'>了解常见WiFi安全漏洞</p>

            <p style='color:#ffff00;'>⚠ 提示：教学模式仅供学习研究使用</p>
        """)
        layout.addWidget(content)

        return page

    def _create_security_page(self) -> QWidget:
        """创建安全评估页 - 增强科幻风格"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 标题
        title = QLabel("自有网络安全评估")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # 输入区域卡片
        input_card = CyberCard("网络信息")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)

        # SSID输入
        ssid_row = QHBoxLayout()
        ssid_label = QLabel("网络名称 (SSID):")
        ssid_label.setStyleSheet("color: #c0c0e0; min-width: 120px;")
        ssid_row.addWidget(ssid_label)
        self.eval_ssid = CyberpunkLineEdit()
        ssid_row.addWidget(self.eval_ssid, 1)
        input_layout.addLayout(ssid_row)

        # 密码输入
        pwd_row = QHBoxLayout()
        pwd_label = QLabel("WiFi密码:")
        pwd_label.setStyleSheet("color: #c0c0e0; min-width: 120px;")
        pwd_row.addWidget(pwd_label)
        self.eval_password = CyberpunkLineEdit()
        self.eval_password.setEchoMode(QLineEdit.Password)
        pwd_row.addWidget(self.eval_password, 1)
        input_layout.addLayout(pwd_row)

        # 加密方式
        enc_row = QHBoxLayout()
        enc_label = QLabel("加密方式:")
        enc_label.setStyleSheet("color: #c0c0e0; min-width: 120px;")
        enc_row.addWidget(enc_label)
        self.eval_encryption = CyberpunkLineEdit("WPA2-PSK")
        enc_row.addWidget(self.eval_encryption, 1)
        input_layout.addLayout(enc_row)

        # 评估按钮
        eval_btn = CyberpunkButton("开始评估")
        eval_btn.clicked.connect(self._do_security_eval)
        eval_btn.setMinimumWidth(200)
        input_layout.addWidget(eval_btn)

        while input_card.content_layout.count():
            input_card.content_layout.takeAt(0)
        input_card.content_layout.addLayout(input_layout)
        main_layout.addWidget(input_card)

        # 评估结果仪表板
        result_card = CyberCard("评估结果")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(15)

        # 仪表盘行
        gauge_row = QHBoxLayout()
        gauge_row.setSpacing(20)

        self.overall_gauge = GaugeWidget(0, 100, "综合评分")
        gauge_row.addWidget(self.overall_gauge)

        self.password_gauge = GaugeWidget(0, 100, "密码强度")
        gauge_row.addWidget(self.password_gauge)

        self.encryption_gauge = GaugeWidget(0, 100, "加密评级")
        gauge_row.addWidget(self.encryption_gauge)

        result_layout.addLayout(gauge_row)

        # 详细结果
        self.eval_result = CyberpunkTextEdit()
        self.eval_result.setReadOnly(True)
        self.eval_result.setMinimumHeight(200)
        result_layout.addWidget(self.eval_result, 1)

        while result_card.content_layout.count():
            result_card.content_layout.takeAt(0)
        result_card.content_layout.addLayout(result_layout)
        main_layout.addWidget(result_card, 1)

        return page

    def _create_ai_page(self) -> QWidget:
        """创建AI助手页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("AI学习助手")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 状态提示
        status = QLabel("请在设置中配置AI API密钥")
        status.setStyleSheet("color: #ffff00; font-size: 14px;")
        layout.addWidget(status)

        # 对话区
        self.ai_chat = CyberpunkTextEdit()
        self.ai_chat.setReadOnly(True)
        self.ai_chat.append("<span style='color:#00fff5;'>AI助手: 你好！有什么WiFi安全问题我可以帮助你解答？</span>")
        layout.addWidget(self.ai_chat)

        # 输入区
        input_layout = QHBoxLayout()
        self.ai_input = CyberpunkLineEdit("请输入您的问题...")
        self.ai_input.returnPressed.connect(self._send_ai_message)
        input_layout.addWidget(self.ai_input)

        send_btn = CyberpunkButton("发送")
        send_btn.clicked.connect(self._send_ai_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        return page

    def _create_attack_defense_page(self) -> QWidget:
        """创建攻防演练页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("攻防演练系统")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        content = CyberpunkTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
            <h3 style='color:#00fff5;'>演练场景</h3>
            <p style='color:#ff00ff;'>▶ WEP漏洞利用场景</p>
            <p style='color:#00fff5;'>模拟WEP网络攻防场景</p>

            <p style='color:#ff00ff;'>▶ WPA握手抓取场景</p>
            <p style='color:#00fff5;'>模拟WPA握手包抓取过程</p>

            <p style='color:#ff00ff;'>▶ 防御加固场景</p>
            <p style='color:#00fff5;'>学习如何加固WiFi安全</p>

            <p style='color:#ffff00;'>⚠ 仅用于授权网络的学习演练</p>
        """)
        layout.addWidget(content)

        return page

    def _create_settings_page(self) -> QWidget:
        """创建设置页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("设置")
        title.setStyleSheet("color: #ff00ff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # AI设置
        ai_group = QLabel("AI设置")
        ai_group.setStyleSheet("color: #00fff5; font-size: 16px; font-weight: bold;")
        layout.addWidget(ai_group)

        layout.addWidget(QLabel("API提供商:"))
        self.setting_provider = CyberpunkLineEdit("openai")
        layout.addWidget(self.setting_provider)

        layout.addWidget(QLabel("API密钥:"))
        self.setting_api_key = CyberpunkLineEdit()
        self.setting_api_key.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.setting_api_key)

        test_btn = CyberpunkButton("测试连接")
        test_btn.clicked.connect(self._test_ai_connection)
        layout.addWidget(test_btn)

        layout.addStretch()

        return page

    def _start_background_animation(self):
        """启动背景动画"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_background)
        self.animation_timer.start(50)

        # 启动首页粒子背景
        if hasattr(self, 'particle_bg') and self.particle_bg:
            QTimer.singleShot(500, self._start_particle_bg)

    def _start_particle_bg(self):
        """启动粒子背景"""
        if hasattr(self, 'particle_bg') and self.particle_bg:
            self.particle_bg.setGeometry(self.home_page.rect())
            self.particle_bg.start()
            self.particle_bg.lower()

    def _update_background(self):
        """更新背景（简化实现）"""
        # 确保粒子背景始终在底层
        if hasattr(self, 'particle_bg') and self.particle_bg:
            self.particle_bg.setGeometry(self.home_page.rect())
            self.particle_bg.lower()

    def _show_home(self):
        """显示首页"""
        self.content_stack.setCurrentWidget(self.home_page)

    def _show_wifi_scan(self):
        """显示WiFi扫描页"""
        self.content_stack.setCurrentWidget(self.wifi_scan_page)

    def _show_learning(self):
        """显示教学模式页"""
        self.content_stack.setCurrentWidget(self.learning_page)

    def _show_security(self):
        """显示安全评估页"""
        self.content_stack.setCurrentWidget(self.security_page)

    def _show_ai_assistant(self):
        """显示AI助手页"""
        self.content_stack.setCurrentWidget(self.ai_page)

    def _show_attack_defense(self):
        """显示攻防演练页"""
        self.content_stack.setCurrentWidget(self.attack_defense_page)

    def _show_settings(self):
        """显示设置页"""
        self.content_stack.setCurrentWidget(self.settings_page)

    def _do_wifi_scan(self):
        """执行WiFi扫描"""
        self.scan_status.set_status("active")
        self.scan_status.set_text("状态: 扫描中...")
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)
        self.wifi_result.clear()
        self.wifi_result.append("<span style='color:#ffff00;'>正在扫描周边WiFi网络...</span>")
        self.wifi_result.append("<span style='color:#8080a0;'>模式: 被动扫描（温和模式）</span>")

        try:
            scanner = get_wifi_scanner(self.safety)
            networks = scanner.scan()

            # 统计
            wep_count = 0
            wpa_count = 0
            wpa3_count = 0

            if networks:
                self.wifi_result.append(f"<span style='color:#00ff00;'>发现 {len(networks)} 个网络:</span>")
                for net in networks:
                    net_str = str(net).lower()
                    if 'wep' in net_str:
                        wep_count += 1
                    elif 'wpa3' in net_str or 'sae' in net_str:
                        wpa3_count += 1
                    else:
                        wpa_count += 1
                    self.wifi_result.append(f"<span style='color:#00fff5;'>{net}</span>")
            else:
                self.wifi_result.append("<span style='color:#ff6666;'>未发现WiFi网络</span>")

            # 更新统计卡片
            self.stat_total.set_value(str(len(networks)))
            self.stat_wep.set_value(str(wep_count))
            self.stat_wpa.set_value(str(wpa_count))
            self.stat_wpa3.set_value(str(wpa3_count))
            self.scan_count_tag.setText(f"发现: {len(networks)} 个")

            self.scan_status.set_status("active")
            self.scan_status.set_text(f"状态: 完成 ({len(networks)}个)")

        except Exception as e:
            self.wifi_result.append(f"<span style='color:#ff3333;'>扫描失败: {e}</span>")
            self.scan_status.set_status("danger")
            self.scan_status.set_text("状态: 失败")
        finally:
            self.scan_progress.setVisible(False)
            self.scan_progress.setRange(0, 100)

    def _do_security_eval(self):
        """执行安全评估"""
        ssid = self.eval_ssid.text()
        password = self.eval_password.text()
        encryption = self.eval_encryption.text()

        if not password:
            self.eval_result.clear()
            self.eval_result.append("<span style='color:#ff3333;'>请输入密码</span>")
            return

        try:
            evaluator = NetworkSecurityEvaluator(self.safety)
            report = evaluator.evaluate_network(ssid, password, encryption)

            self.eval_result.clear()

            # 更新仪表盘
            self.overall_gauge.set_value(report.overall_score)
            self.password_gauge.set_value(report.password_strength.total_score)
            self.encryption_gauge.set_value(report.encryption_rating.score)

            # 详细结果
            self.eval_result.append(f"<span style='color:#ff00ff; font-size:16px; font-weight:bold;'>综合评估报告</span>")
            self.eval_result.append(f"<span style='color:#00fff5;'>综合评分: {report.overall_score}/100 ({report.overall_level})</span>")
            self.eval_result.append("")
            self.eval_result.append(f"<span style='color:#ff00ff;'>密码强度: {report.password_strength.total_score}/100 ({report.password_strength.level})</span>")
            for item in report.password_strength.details:
                status = "✓" if item.get('pass', True) else "✗"
                color = "#00ff00" if item.get('pass', True) else "#ff3333"
                self.eval_result.append(f"  <span style='color:{color};'>{status} {item.get('name', '')}: {item.get('description', '')}</span>")

            self.eval_result.append("")
            self.eval_result.append(f"<span style='color:#ff00ff;'>加密评级: {report.encryption_rating.score}/100 ({report.encryption_rating.level})</span>")
            self.eval_result.append(f"  <span style='color:#00fff5;'>建议: {report.encryption_rating.advice}</span>")

            if report.risks:
                self.eval_result.append("")
                self.eval_result.append(f"<span style='color:#ff3333;'>风险点 ({len(report.risks)}):</span>")
                for risk in report.risks:
                    self.eval_result.append(f"  <span style='color:#ff6666;'>⚠ {risk}</span>")

            if report.suggestions:
                self.eval_result.append("")
                self.eval_result.append(f"<span style='color:#ffcc00;'>改进建议:</span>")
                for sug in report.suggestions:
                    self.eval_result.append(f"  <span style='color:#ffff99;'>→ {sug}</span>")

        except Exception as e:
            self.eval_result.clear()
            self.eval_result.append(f"<span style='color:#ff3333;'>评估失败: {e}</span>")
            import traceback
            traceback.print_exc()

    def _send_ai_message(self):
        """发送AI消息"""
        message = self.ai_input.text()
        if not message:
            return

        self.ai_chat.append(f"<span style='color:#ff00ff;'>你: {message}</span>")
        self.ai_input.clear()

        # TODO: 调用AI
        self.ai_chat.append("<span style='color:#00fff5;'>AI: 请先在设置中配置AI API密钥</span>")

    def _test_ai_connection(self):
        """测试AI连接"""
        from src.ai.api_client import AIClient

        api_key = self.setting_api_key.text()
        if not api_key:
            return

        self.ai_client = AIClient()
        self.ai_client.set_api_key(api_key)

        if self.ai_client.test_connection():
            self.ai_chat.append("<span style='color:#00ff00;'>AI连接测试成功！</span>")
        else:
            self.ai_chat.append("<span style='color:#ff0000;'>AI连接测试失败</span>")

    def _init_modules(self):
        """初始化模块"""
        logger.info("GUI模块初始化完成")

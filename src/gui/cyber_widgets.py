"""
科幻风格UI组件库
提供各种具有赛博朋克风格的自定义Qt组件
"""

import math
from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QProgressBar,
    QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QLinearGradient,
    QRadialGradient, QPainterPath, QPalette
)


class CyberCard(QFrame):
    """
    科幻风格卡片
    带有发光边框和角装饰
    """

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._glow_intensity = 0
        self.setObjectName("cyberCard")
        self.setMinimumHeight(100)
        self._init_ui()

        self._glow_timer = QTimer()
        self._glow_timer.timeout.connect(self._update_glow)
        self._glow_timer.start(50)

    def _init_ui(self):
        self.setStyleSheet("""
            QFrame#cyberCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 26, 46, 200),
                    stop:1 rgba(22, 33, 62, 200));
                border: 1px solid rgba(0, 255, 245, 80);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)

        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("""
                color: #ff00ff;
                font-size: 16px;
                font-weight: bold;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(0, 255, 245, 50);
            """)
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def _update_glow(self):
        self._glow_intensity = (math.sin(self._glow_timer.remainingTime() / 1000.0 * math.pi) + 1) / 2
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        glow_color = QColor(0, 255, 245, int(30 + self._glow_intensity * 20))

        pen = QPen(glow_color, 2)
        painter.setPen(pen)

        corner_size = 15
        # 左上角
        painter.drawLine(0, corner_size, 0, 0)
        painter.drawLine(0, 0, corner_size, 0)
        # 右上角
        painter.drawLine(w - corner_size, 0, w, 0)
        painter.drawLine(w, 0, w, corner_size)
        # 左下角
        painter.drawLine(0, h - corner_size, 0, h)
        painter.drawLine(0, h, corner_size, h)
        # 右下角
        painter.drawLine(w - corner_size, h, w, h)
        painter.drawLine(w, h, w, h - corner_size)

        painter.end()


class StatusIndicator(QWidget):
    """
    状态指示器
    圆形指示灯，支持多种状态颜色和脉冲动画
    """

    STATUS_ACTIVE = "active"
    STATUS_WARNING = "warning"
    STATUS_DANGER = "danger"
    STATUS_OFFLINE = "offline"

    def __init__(self, status: str = "offline", text: str = "", parent=None):
        super().__init__(parent)
        self._status = status
        self._text = text
        self._pulse_phase = 0
        self.setMinimumHeight(24)

        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(50)

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.dot_label = QLabel()
        self.dot_label.setFixedSize(12, 12)
        layout.addWidget(self.dot_label)

        if self._text:
            self.text_label = QLabel(self._text)
            self.text_label.setStyleSheet("color: #a0a0c0; font-size: 12px;")
            layout.addWidget(self.text_label)

        layout.addStretch()
        self._update_color()

    def _get_color(self):
        colors = {
            "active": QColor(0, 255, 0),
            "warning": QColor(255, 204, 0),
            "danger": QColor(255, 51, 51),
            "offline": QColor(100, 100, 120),
        }
        return colors.get(self._status, colors["offline"])

    def _update_color(self):
        color = self._get_color()
        self.dot_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color.name()};
                border-radius: 6px;
            }}
        """)

    def set_status(self, status: str):
        self._status = status
        self._update_color()
        self.update()

    def set_text(self, text: str):
        if hasattr(self, 'text_label'):
            self.text_label.setText(text)

    def _update_pulse(self):
        self._pulse_phase += 0.1
        if self._status in ("active", "danger"):
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)


class CyberProgressBar(QProgressBar):
    """
    科幻风格进度条
    渐变颜色和发光效果
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(8)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                background: rgba(22, 33, 62, 0.8);
                border: 1px solid rgba(0, 255, 245, 30);
                border-radius: 4px;
                padding: 0px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00fff5, stop:1 #ff00ff);
                border-radius: 3px;
            }
        """)


class CyberTag(QLabel):
    """
    科幻风格标签/徽章
    """

    def __init__(self, text: str, tag_type: str = "info", parent=None):
        super().__init__(text, parent)
        self.tag_type = tag_type
        self._apply_style()
        self.setAlignment(Qt.AlignCenter)

    def _apply_style(self):
        styles = {
            "safe": "background: rgba(0, 255, 0, 0.2); color: #00ff00; border: 1px solid rgba(0, 255, 0, 0.4);",
            "warning": "background: rgba(255, 204, 0, 0.2); color: #ffcc00; border: 1px solid rgba(255, 204, 0, 0.4);",
            "danger": "background: rgba(255, 51, 51, 0.2); color: #ff3333; border: 1px solid rgba(255, 51, 51, 0.4);",
            "info": "background: rgba(0, 255, 245, 0.2); color: #00fff5; border: 1px solid rgba(0, 255, 245, 0.4);",
            "primary": "background: rgba(255, 0, 255, 0.2); color: #ff00ff; border: 1px solid rgba(255, 0, 255, 0.4);",
        }
        style = styles.get(self.tag_type, styles["info"])
        self.setStyleSheet(f"""
            QLabel {{
                {style}
                padding: 4px 10px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)


class StatCard(QWidget):
    """
    统计卡片
    显示数值和标签，带有图标和动画
    """

    def __init__(self, title: str, value: str = "0", icon: str = "",
                 value_color: str = "#00fff5", parent=None):
        super().__init__(parent)
        self.title = title
        self._value = value
        self.icon = icon
        self.value_color = value_color
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(0, 255, 245, 0.2);
                border-radius: 8px;
            }
            QWidget:hover {
                border: 1px solid rgba(0, 255, 245, 0.5);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("font-size: 28px;")
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        self.value_label = QLabel(self._value)
        self.value_label.setStyleSheet(f"""
            color: {self.value_color};
            font-size: 28px;
            font-weight: bold;
            font-family: 'Consolas', 'Courier New', monospace;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            color: #8080a0;
            font-size: 13px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

    def set_value(self, value: str):
        self._value = value
        self.value_label.setText(value)

    def set_title(self, title: str):
        self.title = title
        self.title_label.setText(title)


class GaugeWidget(QWidget):
    """
    仪表盘组件
    半圆仪表盘，显示评分或百分比
    """

    def __init__(self, min_value: int = 0, max_value: int = 100,
                 title: str = "", parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self._value = min_value
        self.title = title
        self.setMinimumSize(160, 120)

    def set_value(self, value: int):
        self._value = max(self.min_value, min(self.max_value, value))
        self.update()

    def value(self) -> int:
        return self._value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        center_x = w / 2
        center_y = h * 0.7
        radius = min(w, h * 1.5) / 2 - 20

        # 背景弧
        pen_gray = QPen(QColor(40, 40, 70), 10)
        pen_gray.setCapStyle(Qt.FlatCap)
        painter.setPen(pen_gray)

        start_angle = 210
        span_angle = 120

        rect = QRectF(center_x - radius, center_y - radius,
                      radius * 2, radius * 2)

        painter.drawArc(rect, start_angle * 16, -span_angle * 16)

        # 值弧
        ratio = (self._value - self.min_value) / (self.max_value - self.min_value)
        value_span = span_angle * ratio

        if ratio > 0.7:
            color = QColor(0, 255, 0)
        elif ratio > 0.4:
            color = QColor(255, 204, 0)
        else:
            color = QColor(255, 51, 51)

        pen_value = QPen(color, 10)
        pen_value.setCapStyle(Qt.FlatCap)
        painter.setPen(pen_value)

        # 发光效果
        painter.setPen(QPen(color.lighter(150), 12, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(rect, start_angle * 16, -value_span * 16)
        painter.setPen(pen_value)
        painter.drawArc(rect, start_angle * 16, -value_span * 16)

        # 数值文本
        painter.setPen(color)
        font = QFont("Consolas", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter,
                        f"{self._value}\n{self.title}")

        painter.end()


class CyberDivider(QFrame):
    """
    科幻风格分隔线
    渐变发光分隔线
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setStyleSheet("""
            QFrame[frameShape="4"] {
                max-height: 1px;
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent, stop:0.5 #00fff5, stop:1 transparent);
            }
        """)


class DataPanel(QFrame):
    """
    数据面板
    键值对显示区域，等宽字体
    """

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._data_items = {}
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 10, 30, 0.8);
                border: 1px solid rgba(0, 255, 245, 0.2);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("""
                color: #ff00ff;
                font-size: 14px;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 1px solid rgba(255, 0, 255, 0.3);
            """)
            layout.addWidget(title_label)

        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(4)
        layout.addLayout(self.items_layout)

    def add_item(self, label: str, value: str):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(10)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #8080a0; font-family: Consolas; font-size: 12px;")
        item_layout.addWidget(label_widget)

        item_layout.addStretch()

        value_widget = QLabel(value)
        value_widget.setStyleSheet("color: #00fff5; font-family: Consolas; font-size: 12px; font-weight: bold;")
        value_widget.setObjectName(f"value_{label}")
        item_layout.addWidget(value_widget)

        self.items_layout.addWidget(item_widget)
        self._data_items[label] = value_widget

    def update_value(self, label: str, value: str):
        if label in self._data_items:
            self._data_items[label].setText(value)

    def clear_items(self):
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._data_items.clear()


class CyberSwitch(QWidget):
    """
    科幻风格开关
    """

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self._checked = False
        self._text = text
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        if self._text:
            label = QLabel(self._text)
            label.setStyleSheet("color: #c0c0e0; font-size: 13px;")
            layout.addWidget(label)

        self.switch_btn = QPushButton()
        self.switch_btn.setFixedSize(50, 26)
        self.switch_btn.setCursor(Qt.PointingHandCursor)
        self.switch_btn.clicked.connect(self.toggle)
        layout.addWidget(self.switch_btn)

        layout.addStretch()
        self._update_style()

    def _update_style(self):
        if self._checked:
            self.switch_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 255, 245, 0.2);
                    border: 1px solid #00fff5;
                    border-radius: 13px;
                }
                QPushButton::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background: #00fff5;
                    subcontrol-position: right;
                }
            """)
        else:
            self.switch_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(22, 33, 62, 0.8);
                    border: 1px solid #16213e;
                    border-radius: 13px;
                }
            """)

    def toggle(self):
        self._checked = not self._checked
        self._update_style()

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        self._checked = checked
        self._update_style()


class ParticleBackground(QWidget):
    """
    粒子背景
    动态粒子网格背景效果
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._num_particles = 50

        self.setAttribute(Qt.WA_StyledBackground, True)

    def start(self):
        self._init_particles()
        self._timer.start(30)

    def stop(self):
        self._timer.stop()

    def _init_particles(self):
        self.particles = []
        for _ in range(self._num_particles):
            self.particles.append({
                'x': float(self.width()) * 0.1 + float(self.width()) * 0.8 * (hash(str(_) + 'x') % 1000 / 1000.0),
                'y': float(self.height()) * 0.1 + float(self.height()) * 0.8 * (hash(str(_) + 'y') % 1000 / 1000.0),
                'vx': ((hash(str(_) + 'vx') % 100) - 50) / 100.0 * 0.5,
                'vy': ((hash(str(_) + 'vy') % 100) - 50) / 100.0 * 0.5,
                'size': (hash(str(_) + 's') % 3) + 1,
                'color_type': hash(str(_) + 'c') % 2,
            })

    def _animate(self):
        w, h = self.width(), self.height()
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']

            if p['x'] < 0 or p['x'] > w:
                p['vx'] = -p['vx']
            if p['y'] < 0 or p['y'] > h:
                p['vy'] = -p['vy']

        self.update()

    def paintEvent(self, event):
        if not self.particles:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # 绘制连接线
        max_dist = 100
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i + 1:], i + 1):
                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                dist = (dx * dx + dy * dy) ** 0.5

                if dist < max_dist:
                    alpha = int((1 - dist / max_dist) * 30)
                    color = QColor(0, 255, 245, alpha)
                    painter.setPen(QPen(color, 1))
                    painter.drawLine(int(p1['x']), int(p1['y']),
                                    int(p2['x']), int(p2['y']))

        # 绘制粒子
        for p in self.particles:
            if p['color_type'] == 0:
                color = QColor(0, 255, 245, 100)
            else:
                color = QColor(255, 0, 255, 100)

            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(int(p['x'] - p['size']),
                               int(p['y'] - p['size']),
                               int(p['size'] * 2),
                               int(p['size'] * 2))

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.particles:
            self._init_particles()

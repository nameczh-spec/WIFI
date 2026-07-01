"""
数据可视化模块
提供WiFi安全相关的真实数据图表和可视化分析
所有图表数据都有实际意义，用于学习和分析
"""

import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ChartType(Enum):
    """图表类型"""
    SIGNAL_STRENGTH = "signal_strength"
    CHANNEL_DISTRIBUTION = "channel_distribution"
    ENCRYPTION_DISTRIBUTION = "encryption_distribution"
    SECURITY_RADAR = "security_radar"
    HANDSHAKE_TIMELINE = "handshake_timeline"
    PASSWORD_STRENGTH = "password_strength"
    NETWORK_TRAFFIC = "network_traffic"
    ATTACK_SIMULATION = "attack_simulation"


@dataclass
class WiFiNetworkData:
    """WiFi网络数据"""
    ssid: str
    bssid: str
    signal_strength: int  # dBm
    channel: int
    encryption: str  # WEP, WPA, WPA2, WPA3, Open
    security_flags: List[str] = field(default_factory=list)
    vendor: str = ""
    is_hidden: bool = False
    first_seen: float = 0.0
    last_seen: float = 0.0


@dataclass
class HandshakeStep:
    """握手步骤数据"""
    step: int
    name: str
    description: str
    direction: str  # AP->Client, Client->AP
    status: str  # pending, success, failed
    timestamp: float = 0.0
    details: Dict = field(default_factory=dict)


class WiFiDataVisualizer:
    """
    WiFi数据可视化器
    生成有实际意义的图表数据
    """

    def __init__(self):
        self.networks: List[WiFiNetworkData] = []
        self.signal_history: Dict[str, List[Tuple[float, int]]] = {}
        self.handshake_steps: List[HandshakeStep] = []

    def add_network(self, network: WiFiNetworkData):
        """添加网络数据"""
        self.networks.append(network)
        if network.ssid not in self.signal_history:
            self.signal_history[network.ssid] = []
        self.signal_history[network.ssid].append((time.time(), network.signal_strength))

    def update_signal(self, ssid: str, signal: int):
        """更新信号强度历史"""
        if ssid not in self.signal_history:
            self.signal_history[ssid] = []
        self.signal_history[ssid].append((time.time(), signal))
        # 只保留最近5分钟的数据
        cutoff = time.time() - 300
        self.signal_history[ssid] = [
            (t, s) for t, s in self.signal_history[ssid] if t > cutoff
        ]

    def get_signal_strength_chart(self) -> Dict:
        """
        获取信号强度图表数据
        用途：实时监控各WiFi网络信号强度变化，分析干扰
        """
        if not self.networks:
            return {
                "title": "信号强度监控",
                "xAxis": {"type": "time", "name": "时间"},
                "yAxis": {"type": "value", "name": "信号强度 (dBm)", "min": -100, "max": 0},
                "series": [],
                "legend": {"data": []},
                "tooltip": {"trigger": "axis"}
            }

        series = []
        legend_data = []

        for net in self.networks[:8]:  # 最多显示8个网络
            history = self.signal_history.get(net.ssid, [])
            data = [[t * 1000, s] for t, s in history]

            color = self._get_network_color(net.encryption)

            series.append({
                "name": net.ssid,
                "type": "line",
                "smooth": True,
                "symbol": "none",
                "lineStyle": {"width": 2},
                "itemStyle": {"color": color},
                "data": data,
                "markLine": {
                    "silent": True,
                    "data": [
                        {"yAxis": -80, "label": {"formatter": "弱信号", "color": "#ff6666"}},
                        {"yAxis": -60, "label": {"formatter": "良好", "color": "#ffff00"}},
                        {"yAxis": -40, "label": {"formatter": "优秀", "color": "#00ff00"}}
                    ]
                }
            })
            legend_data.append(net.ssid)

        return {
            "title": {"text": "WiFi信号强度实时监控", "textStyle": {"color": "#ff00ff"}},
            "tooltip": {"trigger": "axis"},
            "legend": {"data": legend_data, "textStyle": {"color": "#c0c0e0"}, "top": 30},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "time",
                "name": "时间",
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "yAxis": {
                "type": "value",
                "name": "信号强度 (dBm)",
                "min": -100,
                "max": 0,
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}},
                "splitLine": {"lineStyle": {"color": "rgba(22, 33, 62, 0.5)"}}
            },
            "series": series,
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {"type": "slider", "start": 0, "end": 100, "bottom": 10}
            ]
        }

    def get_channel_distribution_chart(self) -> Dict:
        """
        获取信道分布图表
        用途：分析信道拥堵情况，优化WiFi信道选择
        """
        channel_data = {}
        for net in self.networks:
            ch = net.channel
            if ch not in channel_data:
                channel_data[ch] = {"count": 0, "networks": [], "signal_sum": 0}
            channel_data[ch]["count"] += 1
            channel_data[ch]["networks"].append(net.ssid)
            channel_data[ch]["signal_sum"] += net.signal_strength

        channels_2g = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        channels_5g = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165]

        x_data = []
        y_data = []
        colors = []

        all_channels = sorted(channel_data.keys())
        for ch in all_channels:
            x_data.append(f"信道{ch}")
            y_data.append(channel_data[ch]["count"])

            # 非重叠信道标绿
            if ch in [1, 6, 11] or ch in [36, 44, 52, 60, 100, 108, 116, 124, 132, 140, 149, 157]:
                colors.append("#00ff00")
            else:
                colors.append("#00fff5")

        return {
            "title": {"text": "WiFi信道分布分析", "textStyle": {"color": "#ff00ff"}},
            "tooltip": {
                "trigger": "axis",
                "formatter": lambda params: self._channel_tooltip(params, channel_data)
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": x_data,
                "axisLabel": {"color": "#8080a0", "rotate": 45},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "yAxis": {
                "type": "value",
                "name": "网络数量",
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}},
                "splitLine": {"lineStyle": {"color": "rgba(22, 33, 62, 0.5)"}}
            },
            "series": [{
                "type": "bar",
                "data": [{"value": v, "itemStyle": {"color": colors[i]}} for i, v in enumerate(y_data)],
                "barWidth": "60%",
                "markLine": {
                    "data": [
                        {"type": "average", "name": "平均值"}
                    ],
                    "lineStyle": {"color": "#ffcc00"}
                }
            }]
        }

    def get_encryption_distribution_chart(self) -> Dict:
        """
        获取加密方式分布图
        用途：了解周边网络安全状况
        """
        enc_data = {"WEP": 0, "WPA": 0, "WPA2": 0, "WPA3": 0, "Open": 0, "Other": 0}

        for net in self.networks:
            enc = net.encryption.upper()
            if "WEP" in enc:
                enc_data["WEP"] += 1
            elif "WPA3" in enc or "SAE" in enc:
                enc_data["WPA3"] += 1
            elif "WPA2" in enc:
                enc_data["WPA2"] += 1
            elif "WPA" in enc:
                enc_data["WPA"] += 1
            elif "OPEN" in enc or "NONE" in enc:
                enc_data["Open"] += 1
            else:
                enc_data["Other"] += 1

        pie_data = []
        colors = {
            "WPA3": "#00ff00",
            "WPA2": "#00fff5",
            "WPA": "#ffcc00",
            "WEP": "#ff3333",
            "Open": "#ff00ff",
            "Other": "#8080a0"
        }

        for enc, count in enc_data.items():
            if count > 0:
                pie_data.append({
                    "value": count,
                    "name": enc,
                    "itemStyle": {"color": colors.get(enc, "#8080a0")}
                })

        return {
            "title": {"text": "周边网络加密方式分布", "textStyle": {"color": "#ff00ff"}, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}个 ({d}%)"},
            "legend": {
                "orient": "vertical",
                "left": "left",
                "textStyle": {"color": "#c0c0e0"},
                "top": "middle"
            },
            "series": [{
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["60%", "50%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#0a0a1a",
                    "borderWidth": 2
                },
                "label": {"color": "#c0c0e0"},
                "data": pie_data
            }]
        }

    def get_security_radar_chart(self, score_data: Dict) -> Dict:
        """
        获取安全评估雷达图
        用途：多维度展示网络安全状况
        """
        indicators = [
            {"name": "密码强度", "max": 100},
            {"name": "加密等级", "max": 100},
            {"name": "防火墙", "max": 100},
            {"name": "固件更新", "max": 100},
            {"name": "访问控制", "max": 100},
            {"name": "管理安全", "max": 100}
        ]

        values = [
            score_data.get("password", 0),
            score_data.get("encryption", 0),
            score_data.get("firewall", 50),
            score_data.get("firmware", 50),
            score_data.get("access_control", 50),
            score_data.get("admin_security", 50)
        ]

        return {
            "title": {"text": "网络安全多维评估", "textStyle": {"color": "#ff00ff"}, "left": "center"},
            "tooltip": {},
            "radar": {
                "indicator": indicators,
                "shape": "polygon",
                "splitNumber": 4,
                "axisName": {"color": "#c0c0e0"},
                "splitLine": {"lineStyle": {"color": "rgba(0, 255, 245, 0.2)"}},
                "splitArea": {"areaStyle": {"color": ["rgba(0, 255, 245, 0.02)", "rgba(0, 255, 245, 0.05)"]}},
                "axisLine": {"lineStyle": {"color": "rgba(0, 255, 245, 0.3)"}}
            },
            "series": [{
                "type": "radar",
                "data": [{
                    "value": values,
                    "name": "安全评分",
                    "areaStyle": {"color": "rgba(0, 255, 245, 0.2)"},
                    "lineStyle": {"color": "#00fff5", "width": 2},
                    "itemStyle": {"color": "#ff00ff"}
                }]
            }]
        }

    def get_handshake_timeline(self, steps: List[HandshakeStep]) -> Dict:
        """
        获取握手过程时间线图
        用途：可视化WPA四次握手过程，学习认证流程
        """
        categories = []
        data_ap_to_client = []
        data_client_to_ap = []

        for step in steps:
            categories.append(f"步骤{step.step}: {step.name}")

            status_color = {
                "pending": "#8080a0",
                "success": "#00ff00",
                "failed": "#ff3333"
            }.get(step.status, "#8080a0")

            if step.direction == "AP->Client":
                data_ap_to_client.append({
                    "value": step.step,
                    "itemStyle": {"color": status_color}
                })
                data_client_to_ap.append(None)
            else:
                data_ap_to_client.append(None)
                data_client_to_ap.append({
                    "value": step.step,
                    "itemStyle": {"color": status_color}
                })

        return {
            "title": {"text": "WPA四次握手过程", "textStyle": {"color": "#ff00ff"}},
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"}
            },
            "legend": {
                "data": ["AP → 客户端", "客户端 → AP"],
                "textStyle": {"color": "#c0c0e0"}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": categories,
                "axisLabel": {"color": "#8080a0", "interval": 0, "rotate": 30},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "yAxis": {
                "type": "value",
                "name": "步骤",
                "min": 0,
                "max": max(len(steps), 4),
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "series": [
                {
                    "name": "AP → 客户端",
                    "type": "bar",
                    "data": data_ap_to_client,
                    "barWidth": "30%",
                    "label": {"show": True, "position": "top", "color": "#c0c0e0"}
                },
                {
                    "name": "客户端 → AP",
                    "type": "bar",
                    "data": data_client_to_ap,
                    "barWidth": "30%",
                    "label": {"show": True, "position": "top", "color": "#c0c0e0"}
                }
            ]
        }

    def get_password_strength_chart(self, strength_data: Dict) -> Dict:
        """
        获取密码强度分析图表
        用途：直观展示密码弱点
        """
        categories = []
        values = []
        colors = []

        items = strength_data.get("details", [])
        for item in items:
            categories.append(item.get("name", ""))
            values.append(item.get("score", 0))
            if item.get("pass", False):
                colors.append("#00ff00")
            else:
                colors.append("#ff3333")

        return {
            "title": {"text": "密码强度分项分析", "textStyle": {"color": "#ff00ff"}},
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "value",
                "max": 100,
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "yAxis": {
                "type": "category",
                "data": categories,
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "series": [{
                "type": "bar",
                "data": [{"value": v, "itemStyle": {"color": colors[i]}} for i, v in enumerate(values)],
                "barWidth": "60%",
                "label": {"show": True, "position": "right", "color": "#c0c0e0"}
            }]
        }

    def _get_network_color(self, encryption: str) -> str:
        """根据加密方式获取颜色"""
        enc = encryption.upper()
        if "WPA3" in enc:
            return "#00ff00"
        elif "WPA2" in enc:
            return "#00fff5"
        elif "WPA" in enc:
            return "#ffcc00"
        elif "WEP" in enc:
            return "#ff3333"
        else:
            return "#ff00ff"

    def _channel_tooltip(self, params, channel_data: Dict) -> str:
        """信道图表tooltip格式化"""
        if not params:
            return ""
        ch_name = params[0]["name"]
        ch_num = int(ch_name.replace("信道", ""))
        info = channel_data.get(ch_num, {})
        count = info.get("count", 0)
        networks = info.get("networks", [])
        result = f"<b>{ch_name}</b><br/>网络数量: {count}<br/>"
        for net in networks[:5]:
            result += f"  • {net}<br/>"
        if len(networks) > 5:
            result += f"  ...等{len(networks)}个"
        return result


class HandshakeSimulator:
    """
    握手过程模拟器
    用于教学目的，模拟WPA四次握手过程
    """

    def __init__(self):
        self.steps = self._init_steps()
        self.current_step = 0
        self.is_running = False
        self.speed = 1.0  # 倍速

    def _init_steps(self) -> List[HandshakeStep]:
        """初始化握手步骤"""
        return [
            HandshakeStep(
                step=1,
                name="ANonce发送",
                description="AP生成随机数ANonce并发送给客户端",
                direction="AP->Client",
                status="pending",
                details={"frame": "EAPOL-Key Message 1", "key_info": "ANonce, RSC, KeyMIC"}
            ),
            HandshakeStep(
                step=2,
                name="SNonce响应",
                description="客户端生成SNonce，计算PTK，返回给AP",
                direction="Client->AP",
                status="pending",
                details={"frame": "EAPOL-Key Message 2", "key_info": "SNonce, RSN IE, KeyMIC"}
            ),
            HandshakeStep(
                step=3,
                name="GTK发送",
                description="AP验证PTK，发送GTK给客户端",
                direction="AP->Client",
                status="pending",
                details={"frame": "EAPOL-Key Message 3", "key_info": "GTK, KeyMIC, Install"}
            ),
            HandshakeStep(
                step=4,
                name="确认完成",
                description="客户端确认GTK，握手完成",
                direction="Client->AP",
                status="pending",
                details={"frame": "EAPOL-Key Message 4", "key_info": "KeyMIC (确认)"}
            )
        ]

    def reset(self):
        """重置模拟器"""
        self.steps = self._init_steps()
        self.current_step = 0
        self.is_running = False

    def next_step(self) -> Optional[HandshakeStep]:
        """执行下一步"""
        if self.current_step >= len(self.steps):
            return None

        step = self.steps[self.current_step]
        step.status = "success"
        step.timestamp = time.time()
        self.current_step += 1
        return step

    def is_complete(self) -> bool:
        """是否完成"""
        return self.current_step >= len(self.steps)

    def get_current_step(self) -> Optional[HandshakeStep]:
        """获取当前步骤"""
        if self.current_step == 0:
            return None
        if self.current_step > len(self.steps):
            return self.steps[-1]
        return self.steps[self.current_step - 1]


class NetworkTrafficSimulator:
    """
    网络流量模拟器
    用于可视化学习正常/异常流量模式
    """

    def __init__(self):
        self.history: List[Tuple[float, float, float]] = []  # time, normal, attack
        self.is_attack = False
        self.max_history = 100

    def generate_sample(self) -> Tuple[float, float, float]:
        """生成一个流量样本"""
        t = time.time()
        normal_traffic = 50 + 30 * abs(math.sin(t / 30)) + random.gauss(0, 5)
        normal_traffic = max(0, normal_traffic)

        attack_traffic = 0
        if self.is_attack:
            attack_traffic = 200 + random.gauss(0, 50)
            attack_traffic = max(0, attack_traffic)

        self.history.append((t, normal_traffic, attack_traffic))
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        return t, normal_traffic, attack_traffic

    def start_attack(self):
        """启动攻击模拟"""
        self.is_attack = True

    def stop_attack(self):
        """停止攻击模拟"""
        self.is_attack = False

    def get_traffic_chart(self) -> Dict:
        """
        获取流量图表
        用途：可视化正常流量与攻击流量的区别，学习入侵检测
        """
        times = [t * 1000 for t, _, _ in self.history]
        normal_data = [n for _, n, _ in self.history]
        attack_data = [a for _, _, a in self.history]

        return {
            "title": {"text": "网络流量监控 (正常 vs 攻击)", "textStyle": {"color": "#ff00ff"}},
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": ["正常流量", "攻击流量"],
                "textStyle": {"color": "#c0c0e0"}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "time",
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}}
            },
            "yAxis": {
                "type": "value",
                "name": "流量 (KB/s)",
                "axisLabel": {"color": "#8080a0"},
                "axisLine": {"lineStyle": {"color": "#16213e"}},
                "splitLine": {"lineStyle": {"color": "rgba(22, 33, 62, 0.5)"}}
            },
            "series": [
                {
                    "name": "正常流量",
                    "type": "line",
                    "smooth": True,
                    "data": list(zip(times, normal_data)),
                    "lineStyle": {"color": "#00ff00", "width": 2},
                    "areaStyle": {"color": "rgba(0, 255, 0, 0.1)"},
                    "symbol": "none"
                },
                {
                    "name": "攻击流量",
                    "type": "line",
                    "smooth": True,
                    "data": list(zip(times, attack_data)),
                    "lineStyle": {"color": "#ff3333", "width": 2},
                    "areaStyle": {"color": "rgba(255, 51, 51, 0.1)"},
                    "symbol": "none"
                }
            ]
        }


import math

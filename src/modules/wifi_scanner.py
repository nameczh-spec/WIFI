"""
WiFi扫描模块 - WiFi可视化安全学习工具 v2
被动扫描WiFi网络
"""

import subprocess
import re
import platform
from typing import List, Optional, Dict
from dataclasses import dataclass
from src.core.safety import SafetyManager, OperationLevel
from src.core.logger import get_logger

logger = get_logger("wifi_scanner")


@dataclass
class WiFiNetwork:
    """WiFi网络信息"""
    ssid: str
    bssid: str
    signal_strength: int  # 百分比 0-100
    encryption: str
    channel: int
    frequency: float  # GHz

    def __str__(self):
        if not self.ssid:
            ssid = "(隐藏网络)"
        else:
            ssid = self.ssid
        return f"{ssid} | {self.bssid} | 信号:{self.signal_strength}% | {self.encryption} | CH:{self.channel}"


class WiFiScanner:
    """WiFi扫描器基类"""

    def __init__(self, safety_manager: Optional[SafetyManager] = None):
        """初始化扫描器"""
        self.safety = safety_manager
        if safety_manager:
            safety_manager.register_operation(
                "wifi_scan",
                OperationLevel.SAFE,
                "被动扫描周围WiFi网络"
            )

    def scan(self) -> List[WiFiNetwork]:
        """扫描WiFi网络"""
        raise NotImplementedError


class WindowsWiFiScanner(WiFiScanner):
    """Windows平台WiFi扫描器"""

    def __init__(self, safety_manager: Optional[SafetyManager] = None):
        super().__init__(safety_manager)
        self.os = "windows"

    def scan(self) -> List[WiFiNetwork]:
        """执行WiFi扫描"""
        logger.info("开始WiFi被动扫描")

        try:
            # 使用netsh扫描（被动）
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            networks = self._parse_output(result.stdout)
            logger.info(f"扫描完成，发现 {len(networks)} 个网络")
            return networks

        except Exception as e:
            logger.error(f"WiFi扫描失败: {e}")
            return []

    def _parse_output(self, output: str) -> List[WiFiNetwork]:
        """解析netsh输出"""
        networks = []
        current_network = {}

        for line in output.split('\n'):
            line = line.strip()

            if line.startswith("SSID") and ":" in line and "BSSID" not in line:
                if current_network:
                    networks.append(self._create_network(current_network))
                ssid = line.split(":", 1)[1].strip()
                current_network = {"ssid": ssid}

            elif line.startswith("BSSID"):
                bssid = line.split(":", 1)[1].strip()
                current_network["bssid"] = bssid

            elif "信号" in line or "signal" in line.lower():
                match = re.search(r'(\d+)%', line)
                if match:
                    current_network["signal"] = int(match.group(1))

            elif "Authentication" in line or "身份验证" in line:
                auth = line.split(":", 1)[1].strip()
                current_network["auth"] = auth

            elif "加密" in line or "Encryption" in line:
                enc = line.split(":", 1)[1].strip()
                current_network["encryption"] = enc

            elif "Channel" in line or "信道" in line:
                match = re.search(r'(\d+)', line)
                if match:
                    current_network["channel"] = int(match.group(1))

        if current_network:
            networks.append(self._create_network(current_network))

        return networks

    def _create_network(self, data: Dict) -> WiFiNetwork:
        """创建WiFiNetwork对象"""
        ssid = data.get("ssid", "")
        bssid = data.get("bssid", "")
        signal = data.get("signal", 0)
        encryption = data.get("encryption", "未知")
        channel = data.get("channel", 0)

        # 计算频率
        if channel > 0:
            frequency = self._channel_to_frequency(channel)
        else:
            frequency = 0.0

        return WiFiNetwork(
            ssid=ssid,
            bssid=bssid,
            signal_strength=signal,
            encryption=encryption,
            channel=channel,
            frequency=frequency
        )

    def _channel_to_frequency(self, channel: int) -> float:
        """信道转频率"""
        if channel == 14:
            return 2.484
        elif 1 <= channel <= 13:
            return 2.407 + channel * 0.005
        elif 34 <= channel <= 165:
            # 5GHz频段
            return 5.0 + channel * 0.005
        return 2.437  # 默认2.4GHz


class LinuxWiFiScanner(WiFiScanner):
    """Linux平台WiFi扫描器"""

    def __init__(self, safety_manager: Optional[SafetyManager] = None):
        super().__init__(safety_manager)
        self.os = "linux"

    def scan(self) -> List[WiFiNetwork]:
        """执行WiFi扫描"""
        logger.info("开始WiFi被动扫描 (Linux)")

        try:
            # 尝试使用iw或iwlist
            try:
                result = subprocess.run(
                    ["sudo", "iw", "dev", "wlan0", "scan"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                result = subprocess.run(
                    ["sudo", "iwlist", "wlan0", "scan"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            networks = self._parse_output(result.stdout)
            logger.info(f"扫描完成，发现 {len(networks)} 个网络")
            return networks

        except Exception as e:
            logger.error(f"WiFi扫描失败: {e}")
            return []

    def _parse_output(self, output: str) -> List[WiFiNetwork]:
        """解析iw/iwlist输出"""
        networks = []
        current = {}

        for line in output.split('\n'):
            line = line.strip()

            if line.startswith("BSS"):
                if current:
                    networks.append(self._create_network(current))
                bssid = line.split()[1].rstrip("(T)")
                current = {"bssid": bssid}

            elif "SSID:" in line:
                ssid = line.split("SSID:", 1)[1].strip()
                current["ssid"] = ssid

            elif "signal:" in line:
                match = re.search(r'signal:(.+)', line)
                if match:
                    signal_str = match.group(1).strip()
                    signal = self._dbm_to_percent(signal_str)
                    current["signal"] = signal

            elif "DS Parameter set: channel" in line:
                match = re.search(r'channel (\d+)', line)
                if match:
                    current["channel"] = int(match.group(1))

            elif "WPA" in line or "WEP" in line:
                current["encryption"] = "WPA/WPA2"

        if current:
            networks.append(self._create_network(current))

        return networks

    def _create_network(self, data: Dict) -> WiFiNetwork:
        """创建WiFiNetwork对象"""
        return WiFiNetwork(
            ssid=data.get("ssid", ""),
            bssid=data.get("bssid", ""),
            signal_strength=data.get("signal", 0),
            encryption=data.get("encryption", "未知"),
            channel=data.get("channel", 0),
            frequency=data.get("channel", 0) * 0.005 + 2.407 if data.get("channel") else 0.0
        )

    def _dbm_to_percent(self, signal_str: str) -> int:
        """dBm转百分比"""
        try:
            dbm = int(signal_str.replace("dBm", "").strip())
            # 将dBm转换为百分比
            if dbm >= -50:
                return 100
            elif dbm <= -100:
                return 0
            else:
                return 2 * (dbm + 100)
        except:
            return 50


def get_wifi_scanner(safety_manager: Optional[SafetyManager] = None) -> WiFiScanner:
    """
    工厂函数，根据平台返回对应扫描器

    Args:
        safety_manager: 安全管理器

    Returns:
        平台对应的WiFi扫描器实例
    """
    system = platform.system().lower()

    if system == "windows":
        logger.info("使用 Windows WiFi 扫描器")
        return WindowsWiFiScanner(safety_manager)
    elif system == "linux":
        logger.info("使用 Linux WiFi 扫描器")
        return LinuxWiFiScanner(safety_manager)
    else:
        logger.warning(f"不支持的平台: {system}，使用Windows扫描器")
        return WindowsWiFiScanner(safety_manager)

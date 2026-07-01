"""
WiFi可视化安全学习工具 v2 - 主入口
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import get_logger
from src.core.config import ConfigManager
from src.core.safety import SafetyManager

logger = get_logger("main")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="WiFi可视化安全学习工具 v2")
    parser.add_argument(
        "--mode",
        choices=["gui", "web", "cli"],
        default="gui",
        help="运行模式: gui(图形界面), web(Web界面), cli(命令行)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Web模式端口号"
    )
    parser.add_argument(
        "--gentle",
        action="store_true",
        default=True,
        help="启用温和模式（默认开启）"
    )
    parser.add_argument(
        "--no-gentle",
        action="store_false",
        dest="gentle",
        help="禁用温和模式"
    )
    return parser.parse_args()


def init_system():
    """初始化系统"""
    logger.info("=" * 50)
    logger.info("WiFi可视化安全学习工具 v2")
    logger.info("=" * 50)

    # 初始化配置管理器
    config = ConfigManager()
    logger.info("配置管理器初始化完成")

    # 初始化安全框架
    safety = SafetyManager(gentle_mode=config.get("gentle_mode", True))
    logger.info(f"安全框架初始化完成，温和模式: {safety.gentle_mode}")

    return config, safety


def run_gui_mode(config, safety):
    """运行GUI模式"""
    logger.info("启动GUI模式...")

    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("WiFi可视化安全学习工具")
        app.setApplicationVersion("2.0.0")

        window = MainWindow(config, safety)
        window.show()

        logger.info("GUI启动成功")
        sys.exit(app.exec_())

    except ImportError as e:
        logger.error(f"PyQt5未安装: {e}")
        logger.info("请运行: pip install PyQt5")
        sys.exit(1)


def run_web_mode(config, safety, port):
    """运行Web模式"""
    logger.info(f"启动Web模式，端口: {port}...")

    try:
        from src.web.app import create_app

        app = create_app(config, safety)
        logger.info("Web服务器启动成功")
        logger.info(f"请访问: http://localhost:{port}")
        app.run(host="0.0.0.0", port=port, debug=False)

    except ImportError as e:
        logger.error(f"Flask未安装: {e}")
        logger.info("请运行: pip install Flask")
        sys.exit(1)


def run_cli_mode(config, safety):
    """运行CLI模式"""
    logger.info("启动CLI模式...")

    from src.modules.wifi_scanner import get_wifi_scanner

    scanner = get_wifi_scanner(safety_manager=safety)
    networks = scanner.scan()

    if networks:
        logger.info(f"发现 {len(networks)} 个WiFi网络:")
        for i, net in enumerate(networks, 1):
            logger.info(f"  {i}. {net}")
    else:
        logger.info("未发现WiFi网络")

    return networks


def main():
    """主函数"""
    args = parse_args()

    # 初始化系统
    config, safety = init_system()

    # 根据模式运行
    if args.mode == "gui":
        run_gui_mode(config, safety)
    elif args.mode == "web":
        run_web_mode(config, safety, args.port)
    elif args.mode == "cli":
        run_cli_mode(config, safety)


if __name__ == "__main__":
    main()

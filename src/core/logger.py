"""
日志模块 - WiFi可视化安全学习工具 v2
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)

    # 避免重复配置
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器 - 按日期命名
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class SensitiveDataFilter(logging.Filter):
    """
    敏感数据过滤器
    防止密码等敏感信息写入日志
    """

    SENSITIVE_KEYWORDS = [
        'password', 'passwd', 'pwd', 'secret', 'key',
        'token', 'api_key', 'apikey', 'auth',
        '密码', '密钥', '口令', '私钥'
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤敏感信息"""
        message = record.getMessage().lower()

        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in message:
                # 将敏感信息替换为星号
                parts = message.split(keyword)
                if len(parts) > 1:
                    record.msg = record.msg.replace(
                        parts[1].split()[0] if parts[1].split() else '',
                        '***'
                    )

        return True


def setup_secure_logger(name: str) -> logging.Logger:
    """设置安全的日志记录器（过滤敏感信息）"""
    logger = get_logger(name)

    # 添加敏感数据过滤器
    sensitive_filter = SensitiveDataFilter()
    for handler in logger.handlers:
        handler.addFilter(sensitive_filter)

    return logger

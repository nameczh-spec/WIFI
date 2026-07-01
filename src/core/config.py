"""
配置管理模块 - WiFi可视化安全学习工具 v2
支持配置加密存储
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class ConfigManager:
    """
    配置管理器
    支持配置读写和加密存储
    """

    # 配置文件路径
    CONFIG_DIR = Path(__file__).parent.parent.parent / "data"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    SECURE_CONFIG_FILE = CONFIG_DIR / "secure_config.enc"

    # 默认配置
    DEFAULT_CONFIG = {
        "theme": "cyberpunk",  # 科幻主题
        "language": "zh_CN",
        "gentle_mode": True,
        "log_level": "INFO",
        "data_path": str(CONFIG_DIR / "data"),
        "log_path": str(CONFIG_DIR.parent / "logs"),
        "ai_provider": "openai",
        "ai_model": "gpt-4o-mini",
        "auto_cleanup": True,
    }

    def __init__(self):
        """初始化配置管理器"""
        self._config: Dict[str, Any] = {}
        self._secure_config: Dict[str, Any] = {}
        self._encryption_key = self._get_or_create_key()

        # 确保目录存在
        self.CONFIG_DIR.mkdir(exist_ok=True)

        # 加载配置
        self._load_config()
        self._load_secure_config()

    def _get_or_create_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = self.CONFIG_DIR / ".key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # 设置文件权限（仅当前用户可读）
            os.chmod(key_file, 0o600)
            return key

    def _load_config(self):
        """加载普通配置"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError:
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()

    def _load_secure_config(self):
        """加载加密配置（API密钥、双密码等）"""
        if self.SECURE_CONFIG_FILE.exists():
            try:
                fernet = Fernet(self._encryption_key)
                with open(self.SECURE_CONFIG_FILE, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                self._secure_config = json.loads(decrypted_data.decode('utf-8'))
            except Exception:
                self._secure_config = {}
        else:
            self._secure_config = {}

    def save(self):
        """保存配置到文件"""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def _save_secure_config(self):
        """保存加密配置"""
        fernet = Fernet(self._encryption_key)
        data = json.dumps(self._secure_config, ensure_ascii=False).encode('utf-8')
        encrypted_data = fernet.encrypt(data)

        with open(self.SECURE_CONFIG_FILE, 'wb') as f:
            f.write(encrypted_data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
        self.save()

    def get_secure(self, key: str, default: Any = None) -> Any:
        """获取加密配置值"""
        return self._secure_config.get(key, default)

    def set_secure(self, key: str, value: str):
        """
        设置加密配置值（用于存储敏感信息如API密钥、双密码）
        """
        self._secure_config[key] = value
        self._save_secure_config()

    def delete_secure(self, key: str):
        """删除加密配置"""
        if key in self._secure_config:
            del self._secure_config[key]
            self._save_secure_config()

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def reset(self):
        """重置为默认配置"""
        self._config = self.DEFAULT_CONFIG.copy()
        self._secure_config = {}
        self.save()
        self._save_secure_config()


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

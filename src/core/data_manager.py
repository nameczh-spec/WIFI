"""
数据管理模块
负责数据保存路径管理和自动清理无关数据
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from src.core.logger import get_logger

logger = get_logger("data_manager")


class DataManager:
    """
    数据管理器
    负责管理数据保存路径、自动清理无关数据
    """

    # 数据子目录
    SUBDIRS = [
        "scans",       # WiFi扫描数据
        "handshakes",  # 握手数据（仅学习用）
        "reports",     # 报告文件
        "exports",     # 导出数据
        "temp",        # 临时文件
        "cache",       # 缓存
        "ai_cache",    # AI对话缓存
        "screenshots", # 截图
    ]

    # 自动清理的目录（临时/缓存）
    CLEANUP_DIRS = [
        "temp",
        "cache",
        "ai_cache",
    ]

    def __init__(self, data_path: str, auto_cleanup: bool = True,
                 retention_days: int = 7):
        """
        初始化数据管理器

        Args:
            data_path: 数据保存根路径
            auto_cleanup: 是否自动清理
            retention_days: 数据保留天数
        """
        self._data_path = Path(data_path)
        self._auto_cleanup = auto_cleanup
        self._retention_days = retention_days

        # 确保目录结构存在
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保所有必要的目录存在"""
        try:
            self._data_path.mkdir(parents=True, exist_ok=True)
            for subdir in self.SUBDIRS:
                (self._data_path / subdir).mkdir(exist_ok=True)
        except OSError as e:
            logger.error(f"创建数据目录失败: {e}")
            raise

    @property
    def data_path(self) -> Path:
        """获取数据根路径"""
        return self._data_path

    def get_path(self, subdir: str = "") -> Path:
        """
        获取指定子目录的完整路径

        Args:
            subdir: 子目录名称

        Returns:
            目录的完整路径
        """
        if subdir and subdir in self.SUBDIRS:
            return self._data_path / subdir
        return self._data_path

    def change_data_path(self, new_path: str) -> bool:
        """
        更改数据保存路径

        Args:
            new_path: 新的路径

        Returns:
            是否成功
        """
        try:
            new_path = Path(new_path)

            # 检查路径是否有效
            if new_path.exists() and not new_path.is_dir():
                logger.error(f"新路径已存在但不是目录: {new_path}")
                return False

            # 创建新目录结构
            self._data_path = new_path
            self._ensure_dirs()

            logger.info(f"数据保存路径已更改为: {new_path}")
            return True
        except Exception as e:
            logger.error(f"更改数据路径失败: {e}")
            return False

    def migrate_data(self, old_path: str, move: bool = False) -> Dict:
        """
        迁移数据到新路径

        Args:
            old_path: 旧路径
            move: True=移动, False=复制

        Returns:
            迁移结果统计
        """
        result = {
            "success": True,
            "files_moved": 0,
            "dirs_moved": 0,
            "errors": []
        }

        old = Path(old_path)
        if not old.exists():
            result["errors"].append(f"旧路径不存在: {old_path}")
            result["success"] = False
            return result

        try:
            for item in old.iterdir():
                try:
                    dest = self._data_path / item.name
                    if item.is_dir():
                        if move:
                            shutil.move(str(item), str(dest))
                        else:
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(str(item), str(dest))
                        result["dirs_moved"] += 1
                    else:
                        if move:
                            shutil.move(str(item), str(dest))
                        else:
                            shutil.copy2(str(item), str(dest))
                        result["files_moved"] += 1
                except Exception as e:
                    result["errors"].append(f"迁移 {item.name} 失败: {e}")
        except Exception as e:
            result["errors"].append(f"迁移过程出错: {e}")
            result["success"] = False

        return result

    def cleanup_temp_files(self) -> Dict:
        """
        清理临时文件和缓存

        Returns:
            清理结果统计
        """
        result = {
            "files_deleted": 0,
            "dirs_deleted": 0,
            "space_freed": 0,  # bytes
            "errors": []
        }

        try:
            for dir_name in self.CLEANUP_DIRS:
                dir_path = self._data_path / dir_name
                if not dir_path.exists():
                    continue

                for item in dir_path.iterdir():
                    try:
                        size = item.stat().st_size
                        if item.is_file():
                            item.unlink()
                            result["files_deleted"] += 1
                            result["space_freed"] += size
                        elif item.is_dir():
                            # 计算目录大小
                            dir_size = sum(
                                f.stat().st_size
                                for f in item.rglob('*')
                                if f.is_file()
                            )
                            shutil.rmtree(item)
                            result["dirs_deleted"] += 1
                            result["space_freed"] += dir_size
                    except Exception as e:
                        result["errors"].append(f"删除 {item.name} 失败: {e}")
        except Exception as e:
            result["errors"].append(f"清理失败: {e}")

        logger.info(f"清理临时文件: 删除 {result['files_deleted']} 个文件, "
                    f"{result['dirs_deleted']} 个目录, "
                    f"释放 {self._format_size(result['space_freed'])}")

        return result

    def cleanup_old_data(self, days: Optional[int] = None) -> Dict:
        """
        清理过期数据

        Args:
            days: 保留天数，默认使用配置的retention_days

        Returns:
            清理结果统计
        """
        if days is None:
            days = self._retention_days

        result = {
            "files_deleted": 0,
            "dirs_deleted": 0,
            "space_freed": 0,
            "errors": []
        }

        cutoff_time = time.time() - (days * 86400)

        try:
            # 扫描所有子目录
            for subdir in self.SUBDIRS:
                dir_path = self._data_path / subdir
                if not dir_path.exists():
                    continue

                for item in dir_path.iterdir():
                    try:
                        mtime = item.stat().st_mtime
                        if mtime < cutoff_time:
                            size = item.stat().st_size
                            if item.is_file():
                                item.unlink()
                                result["files_deleted"] += 1
                                result["space_freed"] += size
                            elif item.is_dir():
                                dir_size = sum(
                                    f.stat().st_size
                                    for f in item.rglob('*')
                                    if f.is_file()
                                )
                                shutil.rmtree(item)
                                result["dirs_deleted"] += 1
                                result["space_freed"] += dir_size
                    except Exception as e:
                        result["errors"].append(f"处理 {item.name} 失败: {e}")
        except Exception as e:
            result["errors"].append(f"清理过期数据失败: {e}")

        logger.info(f"清理过期数据({days}天): 删除 {result['files_deleted']} 个文件, "
                    f"释放 {self._format_size(result['space_freed'])}")

        return result

    def get_storage_info(self) -> Dict:
        """
        获取存储空间使用信息

        Returns:
            存储信息统计
        """
        info = {
            "total_size": 0,
            "total_files": 0,
            "total_dirs": 0,
            "by_dir": {},
            "free_space": 0,
        }

        try:
            # 磁盘总空间和剩余空间
            disk_usage = shutil.disk_usage(self._data_path)
            info["free_space"] = disk_usage.free

            # 统计各目录大小
            for subdir in self.SUBDIRS:
                dir_path = self._data_path / subdir
                if not dir_path.exists():
                    info["by_dir"][subdir] = {"size": 0, "files": 0, "dirs": 0}
                    continue

                dir_size = 0
                file_count = 0
                dir_count = 0

                for root, dirs, files in os.walk(dir_path):
                    dir_count += len(dirs)
                    for f in files:
                        fp = Path(root) / f
                        try:
                            dir_size += fp.stat().st_size
                            file_count += 1
                        except OSError:
                            pass

                info["by_dir"][subdir] = {
                    "size": dir_size,
                    "files": file_count,
                    "dirs": dir_count,
                    "size_human": self._format_size(dir_size),
                }
                info["total_size"] += dir_size
                info["total_files"] += file_count
                info["total_dirs"] += dir_count

            info["total_size_human"] = self._format_size(info["total_size"])
            info["free_space_human"] = self._format_size(info["free_space"])

        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")

        return info

    def save_data(self, subdir: str, filename: str, data: str,
                  encoding: str = 'utf-8') -> Optional[str]:
        """
        保存数据到指定目录

        Args:
            subdir: 子目录
            filename: 文件名
            data: 数据内容
            encoding: 编码

        Returns:
            保存后的文件路径，失败返回None
        """
        try:
            dir_path = self.get_path(subdir)
            file_path = dir_path / filename

            with open(file_path, 'w', encoding=encoding) as f:
                f.write(data)

            logger.debug(f"数据已保存: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return None

    def save_binary_data(self, subdir: str, filename: str,
                         data: bytes) -> Optional[str]:
        """
        保存二进制数据

        Args:
            subdir: 子目录
            filename: 文件名
            data: 二进制数据

        Returns:
            保存后的文件路径
        """
        try:
            dir_path = self.get_path(subdir)
            file_path = dir_path / filename

            with open(file_path, 'wb') as f:
                f.write(data)

            logger.debug(f"二进制数据已保存: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存二进制数据失败: {e}")
            return None

    def auto_cleanup_if_needed(self) -> Optional[Dict]:
        """
        如果启用了自动清理，则执行清理

        Returns:
            清理结果（如果执行了的话）
        """
        if self._auto_cleanup:
            return self.cleanup_temp_files()
        return None

    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小为人类可读格式

        Args:
            size_bytes: 字节数

        Returns:
            格式化后的字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def generate_report(self, report_type: str = "scan",
                        content: str = "") -> Optional[str]:
        """
        生成报告文件

        Args:
            report_type: 报告类型
            content: 报告内容

        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{timestamp}.html"
        return self.save_data("reports", filename, content)

    def list_files(self, subdir: str, extension: str = None) -> List[Dict]:
        """
        列出指定目录下的文件

        Args:
            subdir: 子目录
            extension: 文件扩展名过滤

        Returns:
            文件列表
        """
        dir_path = self.get_path(subdir)
        if not dir_path.exists():
            return []

        files = []
        for item in dir_path.iterdir():
            if item.is_file():
                if extension and not item.suffix.lower() == extension.lower():
                    continue
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": stat.st_size,
                    "size_human": self._format_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

        # 按修改时间倒序
        files.sort(key=lambda x: x["modified"], reverse=True)
        return files

    def delete_file(self, subdir: str, filename: str) -> bool:
        """
        删除指定文件

        Args:
            subdir: 子目录
            filename: 文件名

        Returns:
            是否成功
        """
        try:
            file_path = self.get_path(subdir) / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                logger.info(f"文件已删除: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False


# 全局数据管理器
_data_manager: Optional[DataManager] = None


def get_data_manager(data_path: str = None, auto_cleanup: bool = True,
                     retention_days: int = 7) -> DataManager:
    """
    获取全局数据管理器实例

    Args:
        data_path: 数据路径（首次调用时需要）
        auto_cleanup: 是否自动清理
        retention_days: 保留天数

    Returns:
        数据管理器实例
    """
    global _data_manager
    if _data_manager is None:
        if data_path is None:
            # 默认路径
            from pathlib import Path
            data_path = str(Path(__file__).parent.parent.parent / "data")
        _data_manager = DataManager(data_path, auto_cleanup, retention_days)
    return _data_manager

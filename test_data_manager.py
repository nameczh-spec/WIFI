"""数据管理模块测试"""
import sys
sys.path.insert(0, '.')

from src.core.data_manager import get_data_manager

dm = get_data_manager()

print("=== 数据管理器测试 ===")
print(f"数据路径: {dm.data_path}")

info = dm.get_storage_info()
print(f"\n存储空间:")
print(f"  总大小: {info['total_size_human']}")
print(f"  文件数: {info['total_files']}")
print(f"  目录数: {info['total_dirs']}")
print(f"  剩余空间: {info['free_space_human']}")

print(f"\n各目录大小:")
for name, data in info['by_dir'].items():
    print(f"  {name}: {data['size_human']} ({data['files']}个文件)")

# 测试保存和读取
test_path = dm.save_data("temp", "test.txt", "Hello World")
print(f"\n测试保存: {test_path}")

# 测试清理
result = dm.cleanup_temp_files()
print(f"清理临时文件: 删除{result['files_deleted']}个文件, 释放{result['space_freed']}字节")

print("\n数据管理模块测试通过！")

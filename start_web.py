"""
启动脚本 - WiFi可视化安全学习工具 v2
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.web.app import create_app

if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("WiFi可视化安全学习工具 v2 - Web服务器")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("温和模式已启用")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
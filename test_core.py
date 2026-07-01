"""核心功能集成测试"""
import sys
import json
sys.path.insert(0, '.')

print("=" * 60)
print("WiFi安全学习平台 - 核心功能测试")
print("=" * 60)

# 1. 测试配置管理
print("\n[1/10] 测试配置管理...")
try:
    from src.core.config import ConfigManager
    config = ConfigManager()
    print(f"  ✓ 配置管理器创建成功")
    print(f"  ✓ 温和模式: {config.get('gentle_mode')}")
    print(f"  ✓ 数据路径: {config.get('data_path')}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 2. 测试安全管理器
print("\n[2/10] 测试安全管理器...")
try:
    from src.core.safety import SafetyManager
    safety = SafetyManager(config)
    print(f"  ✓ 安全管理器创建成功")
    print(f"  ✓ 温和模式: {safety.gentle_mode}")
    print(f"  ✓ 操作数量: {len(safety._operations)}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 3. 测试数据管理器
print("\n[3/10] 测试数据管理器...")
try:
    from src.core.data_manager import DataManager
    dm = DataManager(config.get("data_path"))
    info = dm.get_storage_info()
    print(f"  ✓ 数据管理器创建成功")
    print(f"  ✓ 总大小: {info['total_size_human']}")
    print(f"  ✓ 子目录: {len(info['by_dir'])}个")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 4. 测试教学系统
print("\n[4/10] 测试教学系统...")
try:
    from src.modules.teaching import get_teaching_system
    ts = get_teaching_system()
    modules = ts.get_all_modules()
    print(f"  ✓ 教学系统创建成功")
    print(f"  ✓ 学习模块: {len(modules)}个")
    for m in modules[:3]:
        print(f"    - {m.title}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 5. 测试握手模拟器
print("\n[5/10] 测试握手模拟器...")
try:
    from src.modules.handshake_sim import get_handshake_simulator
    hs = get_handshake_simulator()
    lessons = hs.get_all_lessons()
    hs.start_simulation()
    result = hs.do_step()
    print(f"  ✓ 握手模拟器创建成功")
    print(f"  ✓ 课程数量: {len(lessons)}")
    print(f"  ✓ 第一步: {result['title']}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 6. 测试攻防场景
print("\n[6/10] 测试攻防场景...")
try:
    from src.modules.attack_defense import get_attack_defense_simulator
    ad = get_attack_defense_simulator()
    scenarios = ad.get_all_scenarios()
    categories = ad.get_categories()
    print(f"  ✓ 攻防场景创建成功")
    print(f"  ✓ 攻击分类: {len(categories)}个")
    print(f"  ✓ 场景数量: {len(scenarios)}个")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 7. 测试高级练习管理器
print("\n[7/10] 测试高级练习管理器...")
try:
    from src.core.advanced_practice import AdvancedPracticeManager
    apm = AdvancedPracticeManager(safety, config)
    status = apm.get_authorization_status()
    modes = apm.get_practice_modes()
    print(f"  ✓ 高级练习管理器创建成功")
    print(f"  ✓ 授权状态: {status['status']}")
    print(f"  ✓ 练习模式: {len(modes)}个")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 8. 测试AI提示词管理
print("\n[8/10] 测试AI提示词管理...")
try:
    from src.ai.prompts import PromptManager
    pm = PromptManager()
    scenarios = pm.list_scenarios()
    print(f"  ✓ 提示词管理器创建成功")
    print(f"  ✓ AI场景: {len(scenarios)}个")
    for name, desc in scenarios.items():
        print(f"    - {name}: {desc}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 9. 测试可视化模块
print("\n[9/10] 测试可视化模块...")
try:
    from src.modules.visualization import WiFiDataVisualizer
    viz = WiFiDataVisualizer()
    chart = viz.get_signal_strength_chart([])
    print(f"  ✓ 可视化模块创建成功")
    print(f"  ✓ 信号强度图: {len(chart)}")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 10. 测试Flask应用
print("\n[10/10] 测试Flask应用...")
try:
    from src.web.app import create_app
    app = create_app()
    routes = list(app.url_map.iter_rules())
    api_routes = [r for r in routes if '/api/' in r.rule]
    print(f"  ✓ Flask应用创建成功")
    print(f"  ✓ 总路由数: {len(routes)}")
    print(f"  ✓ API路由数: {len(api_routes)}")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("核心功能测试完成！")
print("=" * 60)

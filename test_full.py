"""全面集成测试 - 验证所有模块和API"""
import sys
import json
sys.path.insert(0, '.')

print("=" * 70)
print("WiFi安全学习平台 - 全面集成测试")
print("=" * 70)

results = []

def test(name, func):
    """运行单个测试"""
    try:
        func()
        print(f"  ✅ {name}")
        results.append((name, True, ""))
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        results.append((name, False, str(e)))

# === 1. 核心模块测试 ===
print("\n【1/6】核心模块测试")

def test_config():
    from src.core.config import ConfigManager
    c = ConfigManager()
    assert c.get("gentle_mode") is not None

test("配置管理器", test_config)

def test_safety():
    from src.core.safety import SafetyManager
    from src.core.config import ConfigManager
    c = ConfigManager()
    s = SafetyManager(c)
    assert s.gentle_mode is not None
    assert len(s._operations) > 0

test("安全管理器", test_safety)

def test_data_manager():
    from src.core.data_manager import DataManager
    from src.core.config import ConfigManager
    c = ConfigManager()
    dm = DataManager(c.get("data_path"))
    info = dm.get_storage_info()
    assert "total_size_human" in info
    assert len(info["by_dir"]) >= 8

test("数据管理器", test_data_manager)

def test_advanced_practice():
    from src.core.advanced_practice import AdvancedPracticeManager
    from src.core.safety import SafetyManager
    from src.core.config import ConfigManager
    c = ConfigManager()
    s = SafetyManager(c)
    apm = AdvancedPracticeManager(s, c)
    status = apm.get_authorization_status()
    assert "status" in status
    modes = apm.get_practice_modes()
    assert len(modes) == 4

test("高级练习管理器", test_advanced_practice)

# === 2. 功能模块测试 ===
print("\n【2/6】功能模块测试")

def test_teaching():
    from src.modules.teaching import get_teaching_system
    ts = get_teaching_system()
    modules = ts.get_all_modules()
    assert len(modules) >= 6
    first = modules[0]
    assert first.title
    assert len(first.steps) > 0

test("教学系统", test_teaching)

def test_handshake_sim():
    from src.modules.handshake_sim import get_handshake_simulator
    hs = get_handshake_simulator()
    lessons = hs.get_all_lessons()
    assert len(lessons) >= 6
    hs.start_simulation()
    r = hs.do_step()
    assert r["step"] == 1

test("握手模拟器", test_handshake_sim)

def test_attack_defense():
    from src.modules.attack_defense import get_attack_defense_simulator
    ad = get_attack_defense_simulator()
    scenarios = ad.get_all_scenarios()
    assert len(scenarios) >= 7
    cats = ad.get_categories()
    assert len(cats) >= 5

test("攻防场景", test_attack_defense)

def test_wep_practice():
    from src.modules.wep_practice import WEPPracticeSimulator
    w = WEPPracticeSimulator()
    w.start_practice("test123", "TestWEP")
    status = w.get_progress()
    assert "ivs_collected" in status
    w.capture_ivs(1000)
    assert w.get_progress()["ivs_collected"] >= 1000

test("WEP练习模拟器", test_wep_practice)

def test_visualization():
    from src.modules.visualization import WiFiDataVisualizer
    viz = WiFiDataVisualizer()
    chart = viz.get_signal_strength_chart()
    assert "title" in chart
    chart2 = viz.get_channel_distribution_chart()
    assert "title" in chart2

test("可视化模块", test_visualization)

def test_ai_prompts():
    from src.ai.prompts import PromptManager
    pm = PromptManager()
    scenarios = pm.list_scenarios()
    assert len(scenarios) >= 6
    sp = pm.get_system_prompt("teaching")
    assert len(sp) > 100

test("AI提示词管理", test_ai_prompts)

# === 3. Flask应用测试 ===
print("\n【3/6】Flask应用测试")

def test_flask_app():
    from src.web.app import create_app
    app = create_app()
    assert app is not None
    routes = list(app.url_map.iter_rules())
    assert len(routes) > 50  # 至少50个路由

test("Flask应用创建", test_flask_app)

# === 4. API端点测试 ===
print("\n【4/6】API端点分类测试")

def get_route_list():
    from src.web.app import create_app
    app = create_app()
    return [r.rule for r in app.url_map.iter_rules() if '/api/' in r.rule]

api_routes = get_route_list()
api_categories = {
    "WiFi扫描": [r for r in api_routes if '/wifi/' in r],
    "安全评估": [r for r in api_routes if '/security/' in r],
    "AI对话": [r for r in api_routes if '/ai/' in r],
    "双密码认证": [r for r in api_routes if '/auth/' in r],
    "可视化": [r for r in api_routes if '/visual/' in r],
    "教学系统": [r for r in api_routes if '/teaching/' in r],
    "握手模拟": [r for r in api_routes if '/handshake/' in r],
    "攻防场景": [r for r in api_routes if '/attack/' in r],
    "设置管理": [r for r in api_routes if '/settings/' in r or '/storage/' in r],
    "高级练习": [r for r in api_routes if '/practice/' in r],
    "WEP练习": [r for r in api_routes if 'wep-practice' in r],
}

for cat, routes in api_categories.items():
    status = "✅" if len(routes) > 0 else "❌"
    print(f"  {status} {cat}: {len(routes)}个端点")

print(f"\n  总计: {len(api_routes)}个API端点")

# === 5. 前端资源测试 ===
print("\n【5/6】前端资源测试")

import os

static_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'static')

def check_file(path):
    full = os.path.join(static_dir, path)
    return os.path.exists(full)

frontend_files = [
    ("CSS样式", "css/style.css"),
    ("图标CSS", "css/icons.css"),
    ("动画CSS", "css/animations.css"),
    ("握手样式", "css/handshake.css"),
    ("WEP练习样式", "css/wep_practice.css"),
    ("主脚本", "js/app.js"),
    ("背景动画", "js/background.js"),
    ("可视化", "js/visualization.js"),
    ("教学模式", "js/teaching.js"),
    ("握手模拟", "js/handshake.js"),
    ("攻防演练", "js/attack_defense.js"),
    ("设置管理", "js/settings.js"),
    ("AI对话", "js/ai_chat.js"),
    ("WEP练习", "js/wep_practice.js"),
]

for name, path in frontend_files:
    exists = check_file(path)
    status = "✅" if exists else "❌"
    print(f"  {status} {name}: {path}")

# === 6. 模板文件测试 ===
print("\n【6/6】模板文件测试")

template_dir = os.path.join(os.path.dirname(__file__), 'src', 'web', 'templates')

if os.path.exists(os.path.join(template_dir, 'index.html')):
    print("  ✅ 主页面: index.html")
else:
    print("  ❌ 主页面缺失")

# === 测试总结 ===
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70)

passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total = len(results)

print(f"\n核心功能测试: {passed}/{total} 通过")

if failed > 0:
    print("\n失败的测试:")
    for name, ok, err in results:
        if not ok:
            print(f"  ❌ {name}: {err}")

# 统计前端资源
frontend_passed = sum(1 for _, p in frontend_files if check_file(p))
print(f"\n前端资源: {frontend_passed}/{len(frontend_files)} 存在")

print(f"\nAPI端点总数: {len(api_routes)}个")
print(f"功能分类数: {len(api_categories)}类")

print("\n" + "=" * 70)
if failed == 0:
    print("🎉 所有核心测试通过！")
else:
    print(f"⚠️  有 {failed} 个测试失败，需要修复")
print("=" * 70)

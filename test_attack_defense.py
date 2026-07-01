"""攻防场景测试"""
import sys
sys.path.insert(0, '.')

from src.modules.attack_defense import get_attack_defense_simulator

ad = get_attack_defense_simulator()

print("=== 攻击场景分类 ===")
for cat in ad.get_categories():
    print(f"  {cat['name']}: {cat['count']}个场景")

print("\n=== 所有攻击场景 ===")
for s in ad.get_all_scenarios():
    print(f"  [{s['difficulty']}] {s['title']} - {s['description'][:40]}...")

print("\n=== 模拟: WEP IV重用攻击 ===")
result = ad.start_simulation("wep-iv-reuse")
print(f"开始: {result['title']}")
for i in range(5):
    step_result = ad.next_simulation_step(use_defense=False)
    print(f"  步骤{i+1}: {step_result.message}")
    if step_result.defense_triggered:
        print(f"    [防御触发]")

print("\n=== 防御方法汇总 ===")
for d in ad.get_all_defense_summary():
    print(f"  [{d['importance']}] {d['title']}: {d['description'][:50]}...")

print("\n攻防场景模块测试通过！")

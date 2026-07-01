"""握手模拟器测试"""
import sys
sys.path.insert(0, '.')

from src.modules.handshake_sim import get_handshake_simulator

hs = get_handshake_simulator()
hs.start_simulation()

print("=== WPA四次握手模拟 ===")
print(f"SSID: {hs._ssid}")
print(f"密码: {'*' * len(hs._password)}")
print(f"AP MAC: {hs._ap_mac}")
print(f"客户端 MAC: {hs._client_mac}")
print()

for i in range(4):
    result = hs.do_step()
    print(f"--- 步骤 {result['step']}: {result['title']} ---")
    print(f"方向: {result['packet']['direction']}")
    print(f"说明: {result['packet']['description']}")
    if 'derivation' in result and result['derivation']:
        print(f"密钥派生: {result['derivation']['step_name']}")
    if 'nonce' in result['packet']:
        print(f"Nonce: {result['packet']['nonce'][:32]}...")
    if 'mic' in result['packet']:
        print(f"MIC: {result['packet']['mic'][:16]}...")
    print()

print("=== 教学课程列表 ===")
lessons = hs.get_all_lessons()
for lesson in lessons:
    print(f"  - {lesson['title']}")

print(f"\n安全注意事项: {len(hs.get_security_notes())}条")
print("握手模拟器测试通过！")

# Test Agent - 测试开发Agent

## 职责范围
- 测试用例设计与编写
- TDD（测试驱动开发）流程执行
- 单元测试、集成测试、功能测试
- 测试报告生成
- 测试覆盖率分析
- Bug验证测试

## 工作流程

### 1. TDD流程（新功能开发）
```
Step 1: 分析需求 → 设计测试用例
Step 2: 编写测试文件（test_xxx.py）
Step 3: 运行测试 → 确认测试失败（功能未实现）
Step 4: 实现功能代码
Step 5: 运行测试 → 确认测试通过
Step 6: 重构优化
Step 7: 更新PROJECT_PROGRESS.md
```

### 2. Bug修复验证流程
```
Step 1: 分析bug → 编写复现测试
Step 2: 运行测试 → 确认复现成功
Step 3: 修复代码
Step 4: 运行测试 → 确认测试通过
Step 5: 检查相关测试是否受影响
```

### 3. 现有模块补充测试
```
Step 1: 分析模块功能
Step 2: 设计覆盖所有功能的测试用例
Step 3: 编写测试文件
Step 4: 运行测试 → 处理失败情况
Step 5: 补充边界条件测试
```

## 测试规范

### 测试文件命名
```
test_<模块名>.py
例如: test_wep_practice.py, test_handshake_sim.py
```

### 测试类命名
```python
class Test<功能名称>(unittest.TestCase):
    # 例如: TestWEPPractice, TestKeyDerivation
```

### 测试方法命名
```python
def test_<具体功能>_<场景>(self):
    # 例如: test_capture_ivs_success, test_pbkdf2_step_by_step
```

### 测试结构模板
```python
"""
<模块名>测试
"""
import sys
import unittest
sys.path.insert(0, '.')


class Test<ModuleName>(unittest.TestCase):
    """测试类描述"""

    def setUp(self):
        """测试前置"""
        from src.modules.<module> import <Class>
        self.obj = <Class>()

    def test_<功能>_基本场景(self):
        """测试描述"""
        # 执行
        result = self.obj.method()
        # 断言
        self.assertIn("success", result)
        self.assertTrue(result["success"])

    def test_<功能>_边界条件(self):
        """边界测试"""
        # 测试空输入、极限值等

    def test_<功能>_异常处理(self):
        """异常测试"""
        # 测试错误输入的处理


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## 断言规范

| 场景 | 断言方法 |
|------|----------|
| 检查返回结构 | `self.assertIn("key", result)` |
| 检查成功状态 | `self.assertTrue(result["success"])` |
| 检查数值范围 | `self.assertGreater(len(result["items"]), 0)` |
| 检查类型 | `self.assertIsInstance(result["data"], dict)` |
| 检查近似值 | `self.assertAlmostEqual(value, expected, places=2)` |
| 检查异常 | `self.assertRaises(Exception, func)` |

## 运行命令

```bash
# 运行单个测试文件
python test_xxx.py

# 运行所有测试
python -m unittest discover -s . -p "test_*.py"

# 详细输出
python test_xxx.py -v
```

## 测试覆盖要求

| 模块类型 | 最低覆盖率 |
|----------|------------|
| 核心算法 | 90% |
| API接口 | 80% |
| UI交互 | 70% |
| 辅助工具 | 60% |

## 当前测试文件

| 测试文件 | 测试模块 | 状态 |
|----------|----------|------|
| test_full.py | 全流程测试 | ✅ 通过 |
| test_wep_enhanced.py | WEP强化功能 | ✅ 7/7通过 |
| test_wpa2_handshake.py | WPA2握手分析 | ✅ 8/8通过 |
| test_password_strength.py | 密码强度测试 | ✅ 8/8通过 |
| test_key_derivation.py | 密钥推导演示 | ✅ 7/7通过 |

## 更新记录
- 2026-07-01: 创建Test Agent定义
# WiFi可视化安全学习工具 - 项目纲要

> **每次启动项目时请先阅读此文档了解项目状态**

## 项目概述

**项目名称**: WiFi可视化安全学习工具 v2.0  
**项目目标**: 提供具有科幻风格界面的WiFi安全可视化学习工具，帮助用户理解WiFi加密原理、安全机制和潜在风险  
**核心原则**: **温和模式** - 纯被动分析、本地计算、不主动攻击、不影响网络和其他使用者  

**GitHub仓库**: https://github.com/nameczh-spec/WIFI.git  
**项目路径**: `h:\IT\wifi密码温和解码\wifi密码温和解码_v2`

---

## 当前进度

### ✅ 已完成模块

| 模块 | 功能 | 测试状态 | 完成日期 |
|------|------|----------|----------|
| WiFi扫描 | 被动扫描周边网络、筛选排序、统计展示 | ✅ 通过 | 早期 + 2026-07-01增强 |
| 安全评估 | 网络安全评分、密码强度评估 | ✅ 8/8通过 | 2026-07-01 |
| 教学系统 | 多模块教学内容 | ✅ 通过 | 早期 |
| AI助手 | 智能问答、学习指导、DeepSeek支持 | ✅ 通过 | 早期 + 2026-07-01增强 |
| 攻防演练 | 模拟攻击与防御演示 | ✅ 通过 | 早期 |
| WEP破解练习 | IV收集、FMS攻击模拟、渐进式展示 | ✅ 7/7通过 | 2026-07-01 |
| WPA2握手分析 | EAPOL帧解析、时序图、密钥参数提取 | ✅ 8/8通过 | 2026-07-01 |
| 密码强度测试 | 强度评分、弱模式识别、破解时间估算 | ✅ 8/8通过 | 2026-07-01 |
| PMK/PTK推导演示 | PBKDF2逐步骤、PRF-X详解、PTK分解、密钥链可视化 | ✅ 7/7通过 | 2026-07-01 |
| Agent管理系统 | 5个专用Agent定义 | - | 2026-07-01 |
| 渐进式信息展示 | InfoPanelManager + TeachingPanelManager | - | 2026-07-01 |
| WEP/WPA2讲解面板 | 技术原理详解（FMS攻击、PBKDF2、PTK分解等） | - | 2026-07-01 |
| 前端界面优化 | 首页科幻风格增强、feature-card交互 | - | 2026-07-01 |
| **图标系统升级** | SVG图标库（20+图标）、替换emoji、发光效果 | - | 2026-07-01 |
| **DeepSeek API支持** | DeepSeek作为默认推荐AI提供商 | - | 2026-07-01 |
| **AI动态讲解** | /api/ai/explain接口，根据主题上下文动态生成讲解 | - | 2026-07-01 |
| **扫描功能增强** | 筛选、排序、统计、信号条、加密标签 | - | 2026-07-01 |

### 🔄 进行中

| 任务 | 状态 | 预计完成 |
|------|------|----------|
| 图标系统升级 | ✅ 已完成 | 2026-07-01 |
| DeepSeek API支持 | ✅ 已完成 | 2026-07-01 |
| AI动态讲解接口 | ✅ 已完成 | 2026-07-01 |
| 扫描功能增强 | ✅ 已完成 | 2026-07-01 |

### 📋 待办事项（按优先级）

| 优先级 | 任务 | 描述 |
|--------|------|------|
| MEDIUM | 讲解面板接入AI动态生成 | WEP/WPA2讲解面板添加AI生成按钮 |
| MEDIUM | 更多模块测试 | WiFi扫描、教学系统等模块的测试 |
| MEDIUM | 算法艺术可视化 | 添加动态视觉效果 |
| LOW | 防御加固场景开发 | 攻防演练中的防御场景 |
| LOW | 全面替换emoji图标 | 替换所有页面中的emoji为SVG图标 |

---

## 文件结构

```
wifi密码温和解码_v2/
│
├── PROJECT_PROGRESS.md          # 项目纲要（本文件）
│
├── agents_docs/                 # Agent管理系统
│   ├── AGENTS_INDEX.md          # Agent索引
│   ├── frontend_agent.md        # 前端开发Agent
│   ├── test_agent.md            # 测试Agent
│   ├── doc_agent.md             # 文档Agent
│   ├── review_agent.md          # 代码审查Agent
│   └── api_agent.md             # API开发Agent
│
├── src/
│   ├── core/                    # 核心模块
│   │   ├── config.py            # 配置管理
│   │   ├── safety.py            # 安全管理（温和模式）
│   │   ├── logger.py            # 日志系统
│   │   ├── data_manager.py      # 数据管理
│   │   └── advanced_practice.py # 高级练习管理
│   │
│   ├── modules/                 # 功能模块
│   │   ├── wifi_scanner.py      # WiFi被动扫描
│   │   ├── security_eval.py     # 安全评估
│   │   ├── visualization.py     # 数据可视化
│   │   ├── teaching.py          # 教学系统
│   │   ├── attack_defense.py    # 攻防演练模拟
│   │   ├── wep_practice.py      # WEP破解练习（模拟）
│   │   ├── wpa2_handshake_analyzer.py  # WPA2握手包分析
│   │   ├── password_strength.py # 密码强度测试
│   │   └── handshake_sim.py     # WPA握手模拟+密钥推导演示
│   │
│   ├── ai/                      # AI模块
│   │   ├── api_client.py        # AI API客户端
│   │   └ prompts.py             # Prompt管理
│   │
│   └── web/                     # Web界面
│       ├── app.py               # Flask应用+API路由
│       ├── templates/
│       │   └── index.html       # 主界面HTML
│       └── static/
│           ├── css/             # 样式文件
│           │   ├── style.css           # 通用样式
│           │   ├── animations.css      # 动画效果
│           │   ├── handshake.css       # 握手演示样式
│           │   ├── wep_practice.css    # WEP练习样式
│           │   └── attack_styles.css   # 攻防演练样式
│           └── js/              # JavaScript模块
│               ├── app.js               # 主应用逻辑
│               ├── background.js        # 动态背景
│               ├── handshake.js         # 握手演示交互
│               ├── wep_practice.js      # WEP练习交互
│               ├── visualization.js     # 图表可视化
│               ├── attack_defense.js    # 攻防演练交互
│               └── teaching.js          # 教学模块交互
│
├── test_*.py                    # 测试文件
│   ├── test_full.py             # 全流程测试
│   ├── test_wep_enhanced.py     # WEP强化功能测试
│   ├── test_wpa2_handshake.py   # WPA2握手分析测试
│   ├── test_password_strength.py # 密码强度测试
│   └ test_key_derivation.py     # 密钥推导演示测试
│
├── main.py                      # 主入口
├── requirements.txt             # Python依赖
└ run_server.py                  # 启动脚本
└ .gitignore                     # Git忽略配置
```

---

## 技术栈

| 类别 | 技术 | 版本/说明 |
|------|------|-----------|
| 后端 | Python | 3.13 |
| Web框架 | Flask | REST API |
| 前端 | HTML/CSS/JS | 纯原生，无框架 |
| 图表 | ECharts | 5.4.3 |
| 加密 | hashlib, hmac | Python内置 |
| AI | OpenAI/Claude | 可配置多种API |
| 测试 | unittest | Python内置 |

---

## 规范与约束

### ⚠️ 温和模式核心约束（必须遵守）

```
✅ 允许的操作:
- 被动WiFi扫描（仅监听，不发送）
- 本地离线计算和模拟
- 教学演示和可视化
- 密码强度评估（纯本地）
- 握手包分析（示例数据）

❌ 禁止的操作:
- 发送任何网络数据包
- 执行实际攻击行为
- 修改网络配置
- 干扰其他网络用户
- 破解真实网络密码
```

### 法律合规

```
⚠️ 所有功能仅用于学习研究目的
⚠️ 请遵守当地法律法规
⚠️ 仅在自己的网络上进行实验
⚠️ 禁止对未授权网络进行任何操作
```

### 代码规范

| 规范项 | 要求 |
|--------|------|
| 命名 | snake_case（函数/变量），PascalCase（类） |
| 类型注解 | 关键函数添加类型注解 |
| 异常处理 | 所有外部调用必须有try-except |
| 日志 | 使用src.core.logger，关键操作记录日志 |
| 注释 | 复杂逻辑添加中文注释 |
| 测试 | 新功能必须有测试用例 |

### Git提交规范

```
feat: 新功能
fix: bug修复
refactor: 重构
docs: 文档更新
test: 测试相关
chore: 构建/配置相关
```

---

## 问题记录

| 问题 | 解决方案 | 状态 |
|------|----------|------|
| WEP练习get_status方法名不匹配 | 修改为get_progress | ✅ 已解决 |
| GitHub推送连接重置 | 调整Git HTTP配置 | ✅ 已解决 |
| 密码强度测试断言失败 | 调整测试用例 | ✅ 已解决 |

---

## 模块功能详解

### WEP破解练习模块 (`wep_practice.py`)

**核心功能**:
- 分阶段IV收集（慢速/中速/快速）
- FMS攻击逐字节破解演示
- 弱IV可视化数据
- 成功率曲线数据
- 密钥长度对比演示
- 渐进式信息展示（basic/detailed/full）

**关键方法**:
- `capture_ivs_phase(phase, count)` - 分阶段IV收集
- `get_fms_attack_detail()` - FMS攻击详情
- `get_weak_iv_visualization()` - 弱IV可视化
- `get_progress(detail_level)` - 渐进式进度信息

### WPA2握手包分析模块 (`wpa2_handshake_analyzer.py`)

**核心功能**:
- 纯离线握手包解析（示例数据）
- EAPOL帧结构解析
- 握手时序图数据生成
- 密钥参数提取（ANonce/SNonce等）
- MIC验证演示

**关键方法**:
- `create_sample_handshake()` - 创建示例握手包
- `parse_eapol_frame()` - 解析EAPOL帧
- `get_handshake_timeline()` - 时序图数据
- `extract_key_params()` - 提取密钥参数

### 密码强度测试模块 (`password_strength.py`)

**核心功能**:
- 密码强度评分（0-100）
- 字符类型检测
- 弱密码模式识别（常见密码、键盘模式等）
- 破解时间估算（PBKDF2算法）
- 改进建议生成

**关键方法**:
- `evaluate_password()` - 评估密码强度
- `estimate_crack_time()` - 估算破解时间
- `check_weak_patterns()` - 检查弱模式

### 密钥推导演示模块 (`handshake_sim.py`)

**核心功能**:
- PBKDF2逐步骤计算演示
- PRF-X函数详细演示
- PTK分解为子密钥（KCK/KEK/TK）
- 密钥推导链可视化数据
- PBKDF2迭代动画数据
- 密钥安全原理解释（PMK/PTK/前向保密性）
- 渐进式信息展示接口

**关键方法**:
- `get_pbkdf2_detail()` - PBKDF2逐步骤演示
- `get_prf_detail()` - PRF-X函数演示
- `decompose_ptk()` - PTK分解
- `get_derivation_chain()` - 密钥链可视化
- `get_key_security_explanations()` - 安全原理解释

---

## 更新日志

### 2026-07-01（最新）
- **完成**: 图标系统升级 - SVG图标库（20+图标）、替换导航和首页emoji、发光效果
- **完成**: DeepSeek API支持 - 作为默认推荐AI提供商（deepseek-chat/deepseek-reasoner）
- **完成**: AI动态讲解接口 - `/api/ai/explain`，根据主题和上下文动态生成HTML格式讲解
- **完成**: WiFi扫描功能增强 - 筛选、排序、统计、信号强度条、加密方式彩色标签
- **完成**: GitHub推送成功（最新提交60906d0）
- **总计**: 38个测试用例全部通过
- **待办**: 讲解面板接入AI动态生成、更多模块测试、算法艺术可视化

### 2026-07-01
- **完成**: 前端界面优化（首页科幻风格增强、feature-card交互、标题动画、统计数据展示）
- **完成**: 安全评估模块测试（8个测试用例，全部通过）
- **完成**: WEP/WPA2技术讲解面板（FMS攻击原理、PBKDF2推导、PTK分解、安全分析）
- **完成**: 渐进式信息展示系统（InfoPanelManager + TeachingPanelManager）
- **完成**: Agent管理系统（5个专用Agent定义）
- **完成**: PMK/PTK推导演示强化（7个测试通过）
- **完成**: GitHub推送成功（提交b1de952）

### 之前
- **完成**: WEP破解练习强化（7个测试通过）
- **完成**: WPA2握手包分析模块（8个测试通过）
- **完成**: 密码强度测试模块（8个测试通过）
- **完成**: 修复WEP练习模拟器bug
- **完成**: GitHub仓库初始化和首次推送

---

## 下次启动检查清单

```
1. 阅读此文档了解项目状态
2. 查看待办事项列表
3. 选择要进行的任务
4. 根据任务类型调用对应Agent
5. 任务完成后更新此文档
6. 提交并推送到GitHub
```

---

*最后更新: 2026-07-01*
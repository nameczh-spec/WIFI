# WiFi安全学习工具 - Agent 管理系统

## 概述

本文件夹包含项目开发中使用的专用Agent定义。每个Agent负责特定领域的开发任务，确保开发流程规范化、高效化。

## Agent 列表

| Agent名称 | 文件 | 负责领域 | 调用时机 |
|-----------|------|----------|----------|
| frontend-agent | [frontend_agent.md](frontend_agent.md) | 前端界面开发、UI优化、交互设计 | 界面开发、样式调整、用户体验优化 |
| test-agent | [test_agent.md](test_agent.md) | 测试用例编写、TDD流程、测试报告 | 新功能开发前/后、bug修复验证 |
| doc-agent | [doc_agent.md](doc_agent.md) | 文档编写、API文档、用户指南 | 文档更新、新模块说明 |
| review-agent | [review_agent.md](review_agent.md) | 代码审查、安全检查、性能分析 | 代码提交前、安全审计 |
| api-agent | [api_agent.md](api_agent.md) | API设计、路由开发、数据接口 | 后端接口开发、数据交互 |

## 使用方式

### 自动调用
当任务匹配Agent职责时，系统会自动调用对应Agent。

### 手动调用
在任务描述中明确指定使用某个Agent：
```
使用 frontend-agent 优化握手演示界面
使用 test-agent 为WEP模块编写测试
```

### Agent迭代
Agent定义文件可随时更新扩展，添加新的工作流程或规范。

## Agent工作流程

```
1. 识别任务类型 → 选择对应Agent
2. Agent读取项目纲要(PROJECT_PROGRESS.md)了解上下文
3. Agent按定义流程执行任务
4. 任务完成后更新项目纲要
5. 代码提交并推送
```

## 文件结构

```
agents_docs/
├── AGENTS_INDEX.md          # Agent索引和概览（本文件）
├── frontend_agent.md        # 前端开发Agent
├── test_agent.md            # 测试Agent
├── doc_agent.md             # 文档Agent
├── review_agent.md          # 代码审查Agent
├── api_agent.md             # API开发Agent
└── templates/               # Agent输出模板
    ├── test_template.py     # 测试文件模板
    ├── api_template.py      # API路由模板
    └── doc_template.md      # 文档模板
```

## 更新记录

- 2026-07-01: 创建Agent管理系统，定义5个核心Agent
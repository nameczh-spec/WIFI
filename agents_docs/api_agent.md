# API Agent - 后端API开发Agent

## 职责范围
- Flask路由设计与开发
- REST API接口实现
- 数据序列化与响应格式
- 错误处理与异常响应
- API文档编写
- 接口性能优化

## 工作流程

### 1. API设计
```
Step 1: 确定API路径和功能
Step 2: 定义请求参数（GET/POST）
Step 3: 设计响应数据结构
Step 4: 规划错误处理逻辑
```

### 2. 实现开发
```
Step 1: 在app.py中添加路由函数
Step 2: 获取必要的管理器实例
Step 3: 实现业务逻辑
Step 4: 构建响应JSON
Step 5: 添加异常处理
```

### 3. 测试验证
```
Step 1: 编写API测试用例（可选）
Step 2: 启动服务器测试接口
Step 3: 验证响应格式正确
Step 4: 测试异常情况处理
```

## API设计规范

### 路径命名
```
/api/<模块>/<动作>
例如:
  /api/wep-practice/status
  /api/handshake/next
  /api/security/analyze
```

### 响应格式（统一）
```json
{
  "success": true/false,
  "data": { ... },          // 成功时返回
  "error": "错误信息",       // 失败时返回
  "message": "提示信息"      // 可选
}
```

### 错误响应
```json
{
  "success": false,
  "error": "具体错误描述",
  "code": 400/404/500
}
```

### HTTP状态码使用
| 状态码 | 场景 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 路由模板

```python
@app.route('/api/<module>/<action>', methods=['GET'])
def <module>_<action>():
    """API功能描述"""
    try:
        # 获取管理器
        manager = app.config['<MANAGER_KEY>']

        # 执行操作
        result = manager.method()

        # 返回响应
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"操作失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/<module>/<action>', methods=['POST'])
def <module>_<action>_post():
    """POST接口描述"""
    try:
        data = request.get_json() or {}
        param1 = data.get('param1', 'default')

        # 业务逻辑
        manager = app.config['<MANAGER_KEY>']
        result = manager.method(param1)

        return jsonify({"success": True, "result": result})

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(f"操作失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
```

## 已有API模块

| 路径前缀 | 功能模块 | 主要接口 |
|----------|----------|----------|
| /api/wifi/ | WiFi扫描 | scan, networks, network/<bssid> |
| /api/security/ | 安全评估 | eval, analyze |
| /api/ai/ | AI助手 | chat, clear, config |
| /api/visual/ | 可视化 | signal-strength, channel-distribution |
| /api/teaching/ | 教学系统 | modules, modules/<id>, quiz |
| /api/handshake/ | 握手模拟 | lessons, start, next, reset, status |
| /api/attack/ | 攻防演练 | categories, scenarios, simulate |
| /api/wep-practice/ | WEP练习 | status, start, capture, crack, lesson |
| /api/practice/ | 高级练习 | status, modes, verify-password, start |
| /api/settings/ | 设置管理 | general, data, ai |
| /api/storage/ | 存储管理 | info, cleanup |

## 安全约束（温和模式）

所有API必须遵守：
```
1. 不执行任何实际网络攻击
2. 不发送干扰数据包
3. 不修改网络配置
4. 仅进行被动分析和本地计算
5. 需要授权的功能必须验证密码
```

## 更新记录
- 2026-07-01: 创建API Agent定义
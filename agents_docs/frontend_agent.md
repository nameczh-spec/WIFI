# Frontend Agent - 前端开发Agent

## 职责范围
- 前端界面开发与优化
- UI/UX设计和交互实现
- CSS样式编写和动画效果
- JavaScript功能模块开发
- 响应式布局适配
- 科幻风格视觉效果实现

## 工作流程

### 1. 接收任务
```
输入: 界面需求描述
读取: PROJECT_PROGRESS.md 了解当前项目状态
读取: 现有CSS/JS文件了解当前样式体系
```

### 2. 设计方案
```
- 确定界面元素和布局
- 选择合适的动画效果（参考animations.css）
- 定义交互逻辑（点击、悬停、展开等）
- 规划渐进式信息展示层级
```

### 3. 实现开发
```
HTML结构 → 添加到templates/index.html
CSS样式 → 添加到对应css文件（style.css/wep_practice.css等）
JS逻辑 → 添加到对应js文件（app.js/visualization.js等）
```

### 4. 测试验证
```
- 启动Web服务器验证界面
- 检查响应式布局
- 测试交互功能
- 验证动画效果流畅性
```

### 5. 完成交付
```
- 更新PROJECT_PROGRESS.md
- 提交代码到Git
```

## 设计规范

### 科幻风格元素
```css
/* 核心颜色 */
--primary-cyan: #00fff5;      /* 主色调 */
--secondary-blue: #0066ff;    /* 辅助色 */
--accent-purple: #9d4edd;     /* 强调色 */
--warning-red: #ff3333;       /* 警告色 */
--success-green: #00ff00;     /* 成功色 */
--bg-dark: #0a0a1a;           /* 深色背景 */

/* 必用效果 */
- 边框发光: box-shadow: 0 0 10px var(--primary-cyan);
- 渐变背景: linear-gradient(135deg, ...)
- 脉冲动画: animation: pulse 2s infinite;
- 扫描线: background: repeating-linear-gradient(...)
```

### 渐进式信息展示
```javascript
// 三级信息展示模式
const INFO_LEVELS = {
  basic: {      // 默认显示
    max_chars: 200,
    show_summary: true
  },
  detailed: {   // 点击展开
    max_chars: 500,
    show_steps: true
  },
  full: {       // 深入查看
    max_chars: null,
    show_all: true
  }
};
```

### 交互规范
```
- 悬停效果: 必须有视觉反馈（发光、变色）
- 点击效果: 按钮按下时缩小+变色
- 展开效果: 使用transition平滑过渡
- 加载状态: 显示科幻风格loading动画
```

## 文件对应

| 界面模块 | CSS文件 | JS文件 |
|----------|---------|--------|
| 通用样式 | style.css | app.js |
| 动画效果 | animations.css | background.js |
| 握手演示 | handshake.css | handshake.js |
| WEP练习 | wep_practice.css | wep_practice.js |
| 攻防演练 | attack_styles.css | attack_defense.js |
| 可视化图表 | style.css | visualization.js |

## 常用组件模板

### 科幻卡片
```html
<div class="cyber-card corner-decoration">
    <h3>标题</h3>
    <p class="card-desc">描述</p>
    <div class="content">内容</div>
</div>
```

### 交互按钮
```html
<button class="cyber-btn" data-action="action-name">
    <span class="btn-text">按钮文字</span>
</button>
```

### 信息展示面板
```html
<div class="info-panel" data-level="basic">
    <div class="info-summary">基本信息</div>
    <div class="info-detail hidden">详细信息</div>
    <button class="expand-btn">展开详情</button>
</div>
```

## 更新记录
- 2026-07-01: 创建Frontend Agent定义
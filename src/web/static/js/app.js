/**
 * WiFi可视化安全学习工具 v2 - 主应用脚本
 */

class WiFiLearningApp {
    constructor() {
        this.apiBase = '/api';
        this.aiConfigured = false;
        this.signalChart = null;
        this.securityChart = null;
        this.wifiData = [];
        this.wifiFilter = '';
        this.wifiSort = 'signal-desc';

        this.init();
    }

    init() {
        this.bindNavigation();
        this.bindEvents();
        this.initCharts();
        this.checkStatus();
    }

    // 导航切换
    bindNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.showPage(page);
            });
        });

        // 首页feature-card点击导航
        document.querySelectorAll('.feature-card[data-page]').forEach(card => {
            card.addEventListener('click', () => {
                const page = card.dataset.page;
                this.showPage(page);
            });

            // hover展开详情
            card.addEventListener('mouseenter', () => {
                const detail = card.querySelector('.feature-detail');
                if (detail) detail.classList.remove('hidden');
            });

            card.addEventListener('mouseleave', () => {
                const detail = card.querySelector('.feature-detail');
                if (detail) detail.classList.add('hidden');
            });
        });
    }

    showPage(pageName) {
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === pageName) {
                item.classList.add('active');
            }
        });

        // 更新页面显示
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`page-${pageName}`).classList.add('active');
    }

    // 事件绑定
    bindEvents() {
        // WiFi扫描
        document.getElementById('btn-scan')?.addEventListener('click', () => this.scanWiFi());
        document.getElementById('scan-filter-enc')?.addEventListener('change', (e) => {
            this.wifiFilter = e.target.value;
            this.renderFilteredNetworks();
        });
        document.getElementById('scan-sort')?.addEventListener('change', (e) => {
            this.wifiSort = e.target.value;
            this.renderFilteredNetworks();
        });

        // 安全评估
        document.getElementById('btn-evaluate')?.addEventListener('click', () => this.evaluateSecurity());

        // AI聊天
        document.getElementById('btn-send')?.addEventListener('click', () => this.sendMessage());
        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // AI配置
        document.getElementById('btn-test-ai')?.addEventListener('click', () => this.testAIConnection());
        document.getElementById('btn-save-ai')?.addEventListener('click', () => this.saveAIConfig());

        // 双密码设置
        document.getElementById('btn-set-password')?.addEventListener('click', () => this.setDualPassword());

        // 清理
        document.getElementById('btn-cleanup')?.addEventListener('click', () => this.cleanup());
    }

    // 检查状态
    async checkStatus() {
        try {
            const res = await fetch(`${this.apiBase}/status`);
            const data = await res.json();

            if (data.ai_configured) {
                this.aiConfigured = true;
                document.getElementById('ai-status').innerHTML = '<span style="color: #00ff00;">✓ AI已配置</span>';
            }
        } catch (e) {
            console.error('状态检查失败:', e);
        }
    }

    // 初始化图表
    initCharts() {
        // 信号强度图表
        const signalChartEl = document.getElementById('chart-signal');
        if (signalChartEl) {
            this.signalChart = echarts.init(signalChartEl);
            this.signalChart.setOption({
                title: { text: 'WiFi信号强度', textStyle: { color: '#00fff5' } },
                tooltip: { trigger: 'axis' },
                radar: {
                    indicator: [
                        { name: '信号', max: 100 },
                        { name: '稳定性', max: 100 },
                        { name: '安全性', max: 100 }
                    ]
                },
                series: [{
                    type: 'radar',
                    data: [{ value: [0, 0, 0], name: '当前网络' }]
                }]
            });
        }

        // 安全评估图表
        const securityChartEl = document.getElementById('chart-security');
        if (securityChartEl) {
            this.securityChart = echarts.init(securityChartEl);
            this.securityChart.setOption({
                title: { text: '安全评分', textStyle: { color: '#00fff5' } },
                series: [{
                    type: 'gauge',
                    startAngle: 180,
                    endAngle: 0,
                    min: 0,
                    max: 100,
                    splitNumber: 10,
                    axisLine: {
                        lineStyle: {
                            color: [[0.4, '#ff3333'], [0.7, '#ffcc00'], [1, '#00ff00']]
                        }
                    },
                    pointer: { itemStyle: { color: '#00fff5' } },
                    axisTick: { lineStyle: { color: '#00fff5' } },
                    splitLine: { lineStyle: { color: '#00fff5' } },
                    axisLabel: { color: '#00fff5' },
                    detail: { color: '#00fff5', formatter: '{value}分' },
                    data: [{ value: 0 }]
                }]
            });
        }
    }

    // WiFi扫描
    async scanWiFi() {
        const btn = document.getElementById('btn-scan');
        btn.disabled = true;
        btn.innerHTML = '<span class="icon icon-refresh"></span> 扫描中...';

        try {
            const res = await fetch(`${this.apiBase}/wifi/scan`);
            const data = await res.json();

            if (data.networks) {
                this.wifiData = data.networks;
                this.updateScanStats();
                this.renderFilteredNetworks();
                this.updateSignalChart(data.networks);
            } else if (data.error) {
                alert(data.error);
            }
        } catch (e) {
            console.error('扫描失败:', e);
            alert('扫描失败');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span class="icon icon-radar"></span> 开始扫描';
        }
    }

    updateScanStats() {
        const networks = this.wifiData;
        const total = networks.length;
        const secure = networks.filter(n => n.encryption && n.encryption !== 'Open').length;
        const open = total - secure;

        document.getElementById('stat-total').textContent = total;
        document.getElementById('stat-secure').textContent = secure;
        document.getElementById('stat-open').textContent = open;
    }

    getFilteredSortedNetworks() {
        let result = [...this.wifiData];

        if (this.wifiFilter) {
            result = result.filter(n => n.encryption.includes(this.wifiFilter));
        }

        switch (this.wifiSort) {
            case 'signal-desc':
                result.sort((a, b) => b.signal - a.signal);
                break;
            case 'signal-asc':
                result.sort((a, b) => a.signal - b.signal);
                break;
            case 'name':
                result.sort((a, b) => (a.ssid || '').localeCompare(b.ssid || ''));
                break;
            case 'channel':
                result.sort((a, b) => a.channel - b.channel);
                break;
        }

        return result;
    }

    renderFilteredNetworks() {
        const networks = this.getFilteredSortedNetworks();
        this.displayNetworks(networks);
    }

    displayNetworks(networks) {
        const tbody = document.getElementById('wifi-list');
        tbody.innerHTML = '';

        if (networks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty">未发现WiFi网络</td></tr>';
            return;
        }

        networks.forEach(net => {
            const tr = document.createElement('tr');
            const band = net.channel > 14 ? '5GHz' : '2.4GHz';
            const encClass = net.encryption.includes('WPA2') || net.encryption.includes('WPA3')
                ? 'secure'
                : (net.encryption === 'Open' ? 'danger' : 'warning');
            tr.innerHTML = `
                <td>${net.ssid || '(隐藏)'}</td>
                <td style="font-family: monospace; font-size: 12px;">${net.bssid}</td>
                <td>
                    <div class="signal-bar">
                        <div class="signal-bar-fill" style="width: ${net.signal}%"></div>
                    </div>
                    <span>${net.signal}%</span>
                </td>
                <td><span class="enc-tag ${encClass}">${net.encryption}</span></td>
                <td>${net.channel}</td>
                <td>${band}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    updateSignalChart(networks) {
        if (!this.signalChart || networks.length === 0) return;

        const maxSignal = Math.max(...networks.map(n => n.signal));
        const avgSignal = networks.reduce((a, b) => a + b.signal, 0) / networks.length;

        this.signalChart.setOption({
            series: [{
                type: 'radar',
                data: [{
                    value: [maxSignal, avgSignal, 50],
                    name: '信号质量'
                }]
            }]
        });
    }

    // 安全评估
    async evaluateSecurity() {
        const ssid = document.getElementById('eval-ssid').value;
        const password = document.getElementById('eval-password').value;
        const encryption = document.getElementById('eval-encryption').value;

        if (!password) {
            alert('请输入密码');
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/security/evaluate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ssid, password, encryption })
            });

            const data = await res.json();

            if (data.overall_score !== undefined) {
                this.displayEvalResult(data);
                this.updateSecurityChart(data.overall_score);
            }
        } catch (e) {
            console.error('评估失败:', e);
        }
    }

    displayEvalResult(data) {
        const report = document.getElementById('eval-report');
        report.innerHTML = `
            <h4>评估报告</h4>
            <p>综合评分: <strong>${data.overall_score}/100</strong> (${data.overall_level})</p>
            <p>密码强度: ${data.password_strength.score}/100 (${data.password_strength.level})</p>
            <p>加密评级: ${data.encryption_rating.score}/100 (${data.encryption_rating.level})</p>
            <p>加密建议: ${data.encryption_rating.advice}</p>
            ${data.risks.length > 0 ? `<p style="color: #ff3333;">风险点: ${data.risks.join(', ')}</p>` : ''}
            <p>建议: ${data.suggestions.join('; ')}</p>
        `;
    }

    updateSecurityChart(score) {
        if (!this.securityChart) return;

        this.securityChart.setOption({
            series: [{
                data: [{ value: score }]
            }]
        });
    }

    // AI聊天
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        if (!this.aiConfigured) {
            alert('请先在设置中配置AI API密钥');
            return;
        }

        // 添加用户消息
        this.addChatMessage(message, 'user');

        // 发送请求
        try {
            const scenario = document.getElementById('ai-scenario').value;
            const res = await fetch(`${this.apiBase}/ai/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, scenario })
            });

            const data = await res.json();

            if (data.response) {
                this.addChatMessage(data.response, 'ai');
            } else if (data.error) {
                this.addChatMessage(`错误: ${data.error}`, 'ai');
            }
        } catch (e) {
            console.error('AI请求失败:', e);
            this.addChatMessage('抱歉，AI暂时无法回复', 'ai');
        }

        input.value = '';
    }

    addChatMessage(content, type) {
        const container = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = `message ${type === 'ai' ? 'ai-message' : 'user-message'}`;
        div.innerHTML = `
            <span class="avatar">${type === 'ai' ? '🤖' : '👤'}</span>
            <span class="content">${content}</span>
        `;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    // AI配置
    async testAIConnection() {
        const apiKey = document.getElementById('ai-api-key').value;
        const provider = document.getElementById('ai-provider').value;
        const model = document.getElementById('ai-model').value;

        if (!apiKey) {
            alert('请输入API密钥');
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/ai/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey, provider, model })
            });

            const data = await res.json();

            if (data.status === 'ok') {
                this.aiConfigured = true;
                document.getElementById('ai-status').innerHTML = '<span style="color: #00ff00;">✓ AI配置成功</span>';
                alert('AI连接测试成功！');
            } else {
                alert(data.message || '连接失败');
            }
        } catch (e) {
            console.error('测试失败:', e);
            alert('连接测试失败');
        }
    }

    async saveAIConfig() {
        await this.testAIConnection();
    }

    // 双密码设置
    async setDualPassword() {
        const pwd1 = document.getElementById('pwd1').value;
        const pwd2 = document.getElementById('pwd2').value;

        if (!pwd1 || !pwd2) {
            alert('请输入两段密码');
            return;
        }

        if (pwd1 !== pwd2) {
            alert('两次密码不一致');
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/auth/setup-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password1: pwd1, password2: pwd2 })
            });

            if (res.ok) {
                alert('双密码设置成功！');
                document.getElementById('pwd1').value = '';
                document.getElementById('pwd2').value = '';
            }
        } catch (e) {
            console.error('设置失败:', e);
            alert('设置失败');
        }
    }

    // 清理
    async cleanup() {
        if (confirm('确定要清理临时文件吗？')) {
            this.showNotification('清理功能开发中...', 'info');
        }
    }

    // 通知系统
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    // 显示加载状态
    showLoading(message = '加载中...') {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p style="color: var(--accent-cyan);">${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.remove();
    }

    // 数字动画
    animateNumber(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const diff = end - start;

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + diff * easeProgress);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    // 平滑滚动
    smoothScroll(element, duration = 300) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // 复制到剪贴板
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('已复制到剪贴板', 'success');
        }).catch(() => {
            this.showNotification('复制失败', 'error');
        });
    }

    // 格式化字节
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 格式化时间
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN');
    }

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
}

// 添加fadeOut动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100px); }
    }
`;
document.head.appendChild(style);

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WiFiLearningApp();

    // 初始化可视化模块
    if (typeof DataVisualization !== 'undefined') {
        window.visualizer = new DataVisualization('/api');
        window.visualizer.init();
    }

    // 初始化渐进式信息展示
    window.infoPanelManager = new InfoPanelManager();

    // 初始化统一讲解面板
    window.teachingPanelManager = new TeachingPanelManager();
});


/**
 * 渐进式信息展示管理器
 * 实现basic/detailed/full三级信息展示
 */
class InfoPanelManager {
    constructor() {
        this.panels = new Map();
        this.init();
    }

    init() {
        // 绑定所有info-panel的点击事件
        document.querySelectorAll('.info-panel').forEach(panel => {
            this.bindPanel(panel);
        });

        // 绑定collapsible-teaching
        document.querySelectorAll('.collapsible-teaching').forEach(item => {
            this.bindCollapsible(item);
        });
    }

    bindPanel(panel) {
        const id = panel.id || `panel-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        panel.id = id;

        const summary = panel.querySelector('.info-summary');
        if (summary) {
            summary.addEventListener('click', () => this.togglePanel(id));
        }

        // 存储面板状态
        this.panels.set(id, {
            level: panel.dataset.level || 'basic',
            expanded: false
        });
    }

    bindCollapsible(item) {
        const header = item.querySelector('.collapsible-header');
        if (header) {
            header.addEventListener('click', () => {
                item.classList.toggle('expanded');
            });
        }
    }

    togglePanel(id) {
        const panel = document.getElementById(id);
        if (!panel) return;

        const state = this.panels.get(id);
        if (!state) return;

        state.expanded = !state.expanded;
        panel.classList.toggle('expanded', state.expanded);

        // 更新展开指示器
        const indicator = panel.querySelector('.expand-indicator');
        if (indicator) {
            const text = indicator.querySelector('.text');
            if (text) {
                text.textContent = state.expanded ? '收起' : '展开详情';
            }
        }

        // 如果展开到detailed，可以异步加载更多数据
        if (state.expanded && state.level === 'basic') {
            this.loadDetailedData(id);
        }
    }

    async loadDetailedData(id) {
        const panel = document.getElementById(id);
        const dataType = panel.dataset.type;
        const dataId = panel.dataset.dataId;

        if (!dataType) return;

        try {
            const res = await fetch(`/api/${dataType}/detail?id=${dataId}`);
            const data = await res.json();

            if (data.success) {
                this.updatePanelContent(id, data.data);
            }
        } catch (e) {
            console.error('加载详细数据失败:', e);
        }
    }

    updatePanelContent(id, data) {
        const panel = document.getElementById(id);
        const detailContent = panel.querySelector('.info-detail-content');

        if (!detailContent) return;

        // 根据数据类型更新内容
        if (data.steps) {
            detailContent.innerHTML = this.renderSteps(data.steps);
        } else if (data.content) {
            detailContent.innerHTML = data.content;
        }
    }

    renderSteps(steps) {
        let html = '<div class="info-steps">';
        steps.forEach((step, i) => {
            html += `
                <div class="info-step">
                    <div class="info-step-num">${i + 1}</div>
                    <div class="info-step-content">
                        <div class="info-step-title">${step.title}</div>
                        <div class="info-step-desc">${step.description}</div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    setLevel(id, level) {
        const panel = document.getElementById(id);
        if (!panel) return;

        panel.dataset.level = level;
        const state = this.panels.get(id);
        if (state) {
            state.level = level;
        }
    }

    // 创建新的信息面板
    createPanel(config) {
        const panel = document.createElement('div');
        panel.className = 'info-panel';
        panel.id = config.id || `panel-${Date.now()}`;
        panel.dataset.level = config.level || 'basic';
        panel.dataset.type = config.type || '';
        panel.dataset.dataId = config.dataId || '';

        panel.innerHTML = `
            <div class="info-summary">
                <div class="info-summary-text">${config.summary || ''}</div>
                <div class="expand-indicator">
                    <span class="text">展开详情</span>
                    <span class="icon">▼</span>
                </div>
            </div>
            <div class="info-detail">
                <div class="info-detail-content">
                    ${config.detail || '<p>加载中...</p>'}
                </div>
                ${config.showControls ? `
                    <div class="info-controls">
                        <button class="cyber-btn small" data-action="full">查看完整详情</button>
                        <button class="cyber-btn small" data-action="reset">返回摘要</button>
                    </div>
                ` : ''}
            </div>
        `;

        this.bindPanel(panel);
        return panel;
    }
}


/**
 * 统一讲解面板管理器
 * 提供技术原理讲解、交互式教学等功能
 */
class TeachingPanelManager {
    constructor() {
        this.activePanel = null;
        this.sections = new Map();
        this.init();
    }

    init() {
        // 绑定所有teaching-panel
        document.querySelectorAll('.teaching-panel').forEach(panel => {
            this.bindPanel(panel);
        });

        // 绑定tab切换
        document.querySelectorAll('.teaching-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const panelId = e.target.closest('.teaching-panel').id;
                const sectionId = tab.dataset.section;
                this.switchSection(panelId, sectionId);
            });
        });
    }

    bindPanel(panel) {
        const id = panel.id || `teaching-${Date.now()}`;
        panel.id = id;

        // 存储sections
        panel.querySelectorAll('.teaching-section').forEach(section => {
            const sectionId = section.dataset.sectionId || `section-${Date.now()}`;
            section.dataset.sectionId = sectionId;
            this.sections.set(`${id}-${sectionId}`, section);
        });
    }

    switchSection(panelId, sectionId) {
        const panel = document.getElementById(panelId);
        if (!panel) return;

        // 更新tabs
        panel.querySelectorAll('.teaching-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.section === sectionId);
        });

        // 更新sections
        panel.querySelectorAll('.teaching-section').forEach(section => {
            section.classList.toggle('active', section.dataset.sectionId === sectionId);
        });
    }

    // 创建讲解面板
    createPanel(config) {
        const panel = document.createElement('div');
        panel.className = 'teaching-panel';
        panel.id = config.id || `teaching-${Date.now()}`;

        let tabsHtml = '';
        let sectionsHtml = '';

        if (config.sections) {
            config.sections.forEach((section, i) => {
                const sectionId = `section-${i}`;
                tabsHtml += `
                    <div class="teaching-tab ${i === 0 ? 'active' : ''}" data-section="${sectionId}">
                        ${section.title}
                    </div>
                `;
                sectionsHtml += `
                    <div class="teaching-section ${i === 0 ? 'active' : ''}" data-section-id="${sectionId}">
                        ${this.renderSectionContent(section)}
                    </div>
                `;
            });
        }

        panel.innerHTML = `
            <div class="teaching-panel-header">
                <div class="teaching-panel-title">
                    <span class="icon">${config.icon || '📚'}</span>
                    <h4>${config.title || '技术讲解'}</h4>
                </div>
                <div class="teaching-panel-tabs">
                    ${tabsHtml}
                </div>
            </div>
            <div class="teaching-panel-content">
                ${sectionsHtml}
            </div>
            ${config.showNav ? `
                <div class="teaching-nav-btns">
                    <button class="cyber-btn" data-action="prev">◀ 上一节</button>
                    <button class="cyber-btn" data-action="next">下一节 ▶</button>
                </div>
            ` : ''}
        `;

        this.bindPanel(panel);

        // 绑定导航按钮
        if (config.showNav) {
            panel.querySelectorAll('[data-action]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const action = e.target.dataset.action;
                    this.navigate(panel.id, action);
                });
            });
        }

        return panel;
    }

    renderSectionContent(section) {
        let html = '';

        if (section.intro) {
            html += `
                <div class="teaching-content-block">
                    <p>${section.intro}</p>
                </div>
            `;
        }

        if (section.formula) {
            html += `
                <div class="teaching-content-block">
                    <h5>核心公式</h5>
                    <div class="formula">${section.formula}</div>
                </div>
            `;
        }

        if (section.steps) {
            html += `
                <div class="teaching-content-block">
                    <h5>步骤解析</h5>
                    <div class="info-steps">
                        ${section.steps.map((step, i) => `
                            <div class="info-step">
                                <div class="info-step-num">${i + 1}</div>
                                <div class="info-step-content">
                                    <div class="info-step-title">${step.title}</div>
                                    <div class="info-step-desc">${step.desc}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        if (section.warning) {
            html += `
                <div class="teaching-warning-box">
                    <h5>⚠️ 安全警告</h5>
                    <p>${section.warning}</p>
                </div>
            `;
        }

        if (section.tip) {
            html += `
                <div class="teaching-tip-box">
                    <h5>💡 小提示</h5>
                    <p>${section.tip}</p>
                </div>
            `;
        }

        return html;
    }

    navigate(panelId, action) {
        const panel = document.getElementById(panelId);
        if (!panel) return;

        const tabs = Array.from(panel.querySelectorAll('.teaching-tab'));
        const activeTab = tabs.find(t => t.classList.contains('active'));
        if (!activeTab) return;

        const currentIndex = tabs.indexOf(activeTab);
        let newIndex;

        if (action === 'prev') {
            newIndex = Math.max(0, currentIndex - 1);
        } else if (action === 'next') {
            newIndex = Math.min(tabs.length - 1, currentIndex + 1);
        }

        if (newIndex !== currentIndex) {
            const newSectionId = tabs[newIndex].dataset.section;
            this.switchSection(panelId, newSectionId);
        }
    }

    // 加载远程讲解内容
    async loadContent(panelId, type, params = {}) {
        try {
            const query = new URLSearchParams(params).toString();
            const res = await fetch(`/api/teaching/${type}?${query}`);
            const data = await res.json();

            if (data.success) {
                this.updateContent(panelId, data.content);
            }
        } catch (e) {
            console.error('加载讲解内容失败:', e);
        }
    }

    updateContent(panelId, content) {
        const panel = document.getElementById(panelId);
        if (!panel) return;

        const contentArea = panel.querySelector('.teaching-panel-content');
        if (contentArea) {
            contentArea.innerHTML = content;
        }
    }
}


// 导出模块
window.InfoPanelManager = InfoPanelManager;
window.TeachingPanelManager = TeachingPanelManager;

/**
 * WiFi可视化安全学习工具 v2 - 主应用脚本
 */

class WiFiLearningApp {
    constructor() {
        this.apiBase = '/api';
        this.aiConfigured = false;
        this.signalChart = null;
        this.securityChart = null;

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
        btn.textContent = '扫描中...';

        try {
            const res = await fetch(`${this.apiBase}/wifi/scan`);
            const data = await res.json();

            if (data.networks) {
                this.displayNetworks(data.networks);
                this.updateSignalChart(data.networks);
            } else if (data.error) {
                alert(data.error);
            }
        } catch (e) {
            console.error('扫描失败:', e);
            alert('扫描失败');
        } finally {
            btn.disabled = false;
            btn.textContent = '开始扫描';
        }
    }

    displayNetworks(networks) {
        const tbody = document.getElementById('wifi-list');
        tbody.innerHTML = '';

        if (networks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty">未发现WiFi网络</td></tr>';
            return;
        }

        networks.forEach(net => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${net.ssid || '(隐藏)'}</td>
                <td>${net.bssid}</td>
                <td>${net.signal}%</td>
                <td>${net.encryption}</td>
                <td>${net.channel}</td>
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
});

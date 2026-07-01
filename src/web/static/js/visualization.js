/**
 * 数据可视化模块
 * 处理各类图表的初始化、数据加载和交互
 */

class DataVisualization {
    constructor(apiBase = '/api') {
        this.apiBase = apiBase;
        this.charts = {};
        this.trafficTimer = null;
        this.handshakeAutoTimer = null;
        this.isTrafficRunning = false;
        this.isAttackMode = false;
    }

    init() {
        this._bindTabs();
        this._bindHandshakeControls();
        this._bindTrafficControls();
        this._bindPasswordControls();
        this._initCharts();
        this._loadDefaultCharts();
    }

    _bindTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const chartName = btn.dataset.chart;
                this._switchChart(chartName, btn);
            });
        });
    }

    _switchChart(chartName, activeBtn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        activeBtn.classList.add('active');

        document.querySelectorAll('.chart-panel').forEach(p => p.classList.remove('active'));
        const panel = document.getElementById(`chart-${chartName}`);
        if (panel) {
            panel.classList.add('active');
            setTimeout(() => {
                this._resizeChart(chartName);
            }, 100);
        }
    }

    _resizeChart(chartName) {
        const chartId = `echart-${chartName}`;
        if (this.charts[chartName]) {
            this.charts[chartName].resize();
        }
    }

    _initCharts() {
        const chartTypes = ['encryption', 'channel', 'handshake', 'traffic', 'password'];
        chartTypes.forEach(type => {
            const el = document.getElementById(`echart-${type}`);
            if (el && typeof echarts !== 'undefined') {
                this.charts[type] = echarts.init(el);
            }
        });

        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => {
                if (chart && chart.resize) chart.resize();
            });
        });
    }

    _loadDefaultCharts() {
        this.loadEncryptionChart();
        this.loadChannelChart();
        this.loadHandshakeChart();
        this.loadPasswordChart('password123');
    }

    async loadEncryptionChart() {
        try {
            const res = await fetch(`${this.apiBase}/visual/encryption-chart`);
            const data = await res.json();
            if (this.charts.encryption && !data.error) {
                this.charts.encryption.setOption(data);
            }
        } catch (e) {
            console.error('加载加密分布图失败:', e);
            this._showMockEncryptionChart();
        }
    }

    _showMockEncryptionChart() {
        if (!this.charts.encryption) return;
        const mockData = {
            title: { text: '周边网络加密方式分布 (模拟数据)', textStyle: { color: '#ff00ff' }, left: 'center' },
            tooltip: { trigger: 'item', formatter: '{b}: {c}个 ({d}%)' },
            legend: { orient: 'vertical', left: 'left', textStyle: { color: '#c0c0e0' }, top: 'middle' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['60%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 10, borderColor: '#0a0a1a', borderWidth: 2 },
                label: { color: '#c0c0e0' },
                data: [
                    { value: 8, name: 'WPA3', itemStyle: { color: '#00ff00' } },
                    { value: 15, name: 'WPA2', itemStyle: { color: '#00fff5' } },
                    { value: 5, name: 'WPA', itemStyle: { color: '#ffcc00' } },
                    { value: 2, name: 'WEP', itemStyle: { color: '#ff3333' } },
                    { value: 1, name: 'Open', itemStyle: { color: '#ff00ff' } }
                ]
            }]
        };
        this.charts.encryption.setOption(mockData);
    }

    async loadChannelChart() {
        try {
            const res = await fetch(`${this.apiBase}/visual/channel-chart`);
            const data = await res.json();
            if (this.charts.channel && !data.error) {
                this.charts.channel.setOption(data);
            }
        } catch (e) {
            console.error('加载信道图失败:', e);
            this._showMockChannelChart();
        }
    }

    _showMockChannelChart() {
        if (!this.charts.channel) return;
        const channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 36, 40, 44, 48, 52, 56, 60, 64];
        const values = [5, 2, 3, 1, 4, 6, 3, 2, 4, 1, 5, 2, 3, 4, 2, 3, 2, 1, 2];
        const colors = channels.map(ch =>
            [1, 6, 11, 36, 44, 52, 60].includes(ch) ? '#00ff00' : '#00fff5'
        );

        this.charts.channel.setOption({
            title: { text: 'WiFi信道分布分析 (模拟数据)', textStyle: { color: '#ff00ff' } },
            tooltip: { trigger: 'axis' },
            grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                data: channels.map(c => `信道${c}`),
                axisLabel: { color: '#8080a0', rotate: 45 },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            yAxis: {
                type: 'value',
                name: '网络数量',
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } },
                splitLine: { lineStyle: { color: 'rgba(22, 33, 62, 0.5)' } }
            },
            series: [{
                type: 'bar',
                data: values.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
                barWidth: '60%'
            }]
        });
    }

    _bindHandshakeControls() {
        document.getElementById('btn-handshake-reset')?.addEventListener('click', () => this.resetHandshake());
        document.getElementById('btn-handshake-next')?.addEventListener('click', () => this.nextHandshakeStep());
        document.getElementById('btn-handshake-auto')?.addEventListener('click', () => this.toggleAutoHandshake());
    }

    async loadHandshakeChart() {
        try {
            const res = await fetch(`${this.apiBase}/visual/handshake-timeline`);
            const data = await res.json();
            if (this.charts.handshake && !data.error) {
                this.charts.handshake.setOption(data.chart);
                this._updateHandshakeDetail(data.steps, data.current_step);
            }
        } catch (e) {
            console.error('加载握手图失败:', e);
            this._showMockHandshakeChart();
        }
    }

    _showMockHandshakeChart() {
        if (!this.charts.handshake) return;
        const steps = [
            { step: 1, name: 'ANonce发送', direction: 'AP->Client', status: 'pending' },
            { step: 2, name: 'SNonce响应', direction: 'Client->AP', status: 'pending' },
            { step: 3, name: 'GTK发送', direction: 'AP->Client', status: 'pending' },
            { step: 4, name: '确认完成', direction: 'Client->AP', status: 'pending' }
        ];

        this._renderHandshakeChart(steps);
    }

    _renderHandshakeChart(steps) {
        if (!this.charts.handshake) return;

        const categories = steps.map(s => `步骤${s.step}: ${s.name}`);
        const apData = steps.map(s => s.direction === 'AP->Client' ? {
            value: s.step,
            itemStyle: { color: this._getStatusColor(s.status) }
        } : null);
        const clientData = steps.map(s => s.direction === 'Client->AP' ? {
            value: s.step,
            itemStyle: { color: this._getStatusColor(s.status) }
        } : null);

        this.charts.handshake.setOption({
            title: { text: 'WPA四次握手过程', textStyle: { color: '#ff00ff' } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['AP → 客户端', '客户端 → AP'], textStyle: { color: '#c0c0e0' } },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'category',
                data: categories,
                axisLabel: { color: '#8080a0', interval: 0, rotate: 20 },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 5,
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            series: [
                { name: 'AP → 客户端', type: 'bar', data: apData, barWidth: '30%' },
                { name: '客户端 → AP', type: 'bar', data: clientData, barWidth: '30%' }
            ]
        });
    }

    _getStatusColor(status) {
        const colors = {
            success: '#00ff00',
            failed: '#ff3333',
            pending: '#8080a0'
        };
        return colors[status] || colors.pending;
    }

    async resetHandshake() {
        this._stopAutoHandshake();
        try {
            await fetch(`${this.apiBase}/visual/handshake/reset`, { method: 'POST' });
            await this.loadHandshakeChart();
            this._updateHandshakeDetail([], 0);
        } catch (e) {
            console.error('重置握手失败:', e);
        }
    }

    async nextHandshakeStep() {
        try {
            const res = await fetch(`${this.apiBase}/visual/handshake/next`, { method: 'POST' });
            const data = await res.json();
            if (!data.error) {
                await this.loadHandshakeChart();
                if (data.step) {
                    this._showStepDetail(data.step);
                }
            }
        } catch (e) {
            console.error('下一步失败:', e);
        }
    }

    toggleAutoHandshake() {
        const btn = document.getElementById('btn-handshake-auto');
        if (this.handshakeAutoTimer) {
            this._stopAutoHandshake();
            btn.textContent = '自动播放';
            btn.classList.remove('primary');
        } else {
            this._startAutoHandshake();
            btn.textContent = '暂停';
            btn.classList.add('primary');
        }
    }

    _startAutoHandshake() {
        if (this.handshakeAutoTimer) return;
        this.handshakeAutoTimer = setInterval(() => {
            this.nextHandshakeStep().then(() => {
                // 检查是否完成
                fetch(`${this.apiBase}/visual/handshake-timeline`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.is_complete) {
                            this._stopAutoHandshake();
                            const btn = document.getElementById('btn-handshake-auto');
                            if (btn) {
                                btn.textContent = '重新播放';
                                btn.classList.remove('primary');
                            }
                        }
                    });
            });
        }, 1500);
    }

    _stopAutoHandshake() {
        if (this.handshakeAutoTimer) {
            clearInterval(this.handshakeAutoTimer);
            this.handshakeAutoTimer = null;
        }
    }

    _updateHandshakeDetail(steps, currentStep) {
        const detailEl = document.getElementById('handshake-detail');
        if (!detailEl) return;

        if (currentStep === 0) {
            detailEl.innerHTML = '<p>点击"下一步"开始模拟WPA四次握手过程</p>';
            return;
        }

        let html = '<h4>握手进度</h4>';
        steps.forEach(s => {
            const statusIcon = s.status === 'success' ? '✅' : (s.status === 'pending' ? '⏳' : '❌');
            const statusClass = s.status === 'success' ? 'step-info' : '';
            html += `<div class="${statusClass}">
                ${statusIcon} <strong>步骤${s.step}: ${s.name}</strong><br>
                <span style="color:#8080a0;font-size:12px;">${s.direction} - ${s.description}</span>
            </div>`;
        });
        detailEl.innerHTML = html;
    }

    _showStepDetail(step) {
        const detailEl = document.getElementById('handshake-detail');
        if (!detailEl) return;

        const statusIcon = step.status === 'success' ? '✅' : '❌';
        detailEl.innerHTML = `
            <h4>${statusIcon} 步骤 ${step.step}: ${step.name}</h4>
            <div class="step-info">
                <strong>方向:</strong> ${step.direction}<br>
                <strong>描述:</strong> ${step.description}<br>
                <strong>帧类型:</strong> ${step.details?.frame || 'N/A'}<br>
                <strong>关键字段:</strong> ${step.details?.key_info || 'N/A'}
            </div>
            <p style="margin-top:15px;color:#ffcc00;font-size:12px;">
                💡 ${this._getStepTip(step.step)}
            </p>
        `;
    }

    _getStepTip(step) {
        const tips = {
            1: 'AP生成随机数ANonce，用于后续密钥派生。此消息不加密。',
            2: '客户端生成SNonce，结合ANonce和密码计算PTK（临时密钥）。',
            3: 'AP验证客户端身份，发送GTK（组临时密钥）用于广播加密。',
            4: '客户端确认收到GTK，握手完成，双方可以开始加密通信。'
        };
        return tips[step] || '';
    }

    _bindTrafficControls() {
        document.getElementById('btn-traffic-start')?.addEventListener('click', () => this.startTraffic());
        document.getElementById('btn-traffic-stop')?.addEventListener('click', () => this.stopTraffic());
        document.getElementById('btn-traffic-attack')?.addEventListener('click', () => this.toggleAttack());
    }

    startTraffic() {
        if (this.isTrafficRunning) return;
        this.isTrafficRunning = true;
        this._updateTrafficBtnStates();

        this.trafficTimer = setInterval(() => {
            this._updateTrafficChart();
        }, 1000);
    }

    stopTraffic() {
        this.isTrafficRunning = false;
        this.isAttackMode = false;
        if (this.trafficTimer) {
            clearInterval(this.trafficTimer);
            this.trafficTimer = null;
        }
        this._updateTrafficBtnStates();
    }

    async toggleAttack() {
        if (!this.isTrafficRunning) {
            alert('请先开始流量采集');
            return;
        }

        this.isAttackMode = !this.isAttackMode;

        try {
            const endpoint = this.isAttackMode ? 'attack-start' : 'attack-stop';
            await fetch(`${this.apiBase}/visual/traffic/${endpoint}`, { method: 'POST' });
        } catch (e) {
            console.error('切换攻击模式失败:', e);
        }

        this._updateTrafficBtnStates();
    }

    _updateTrafficBtnStates() {
        const startBtn = document.getElementById('btn-traffic-start');
        const stopBtn = document.getElementById('btn-traffic-stop');
        const attackBtn = document.getElementById('btn-traffic-attack');

        if (startBtn) startBtn.disabled = this.isTrafficRunning;
        if (stopBtn) stopBtn.disabled = !this.isTrafficRunning;
        if (attackBtn) {
            attackBtn.disabled = !this.isTrafficRunning;
            if (this.isAttackMode) {
                attackBtn.textContent = '停止攻击';
                attackBtn.classList.add('danger');
            } else {
                attackBtn.textContent = '模拟攻击';
                attackBtn.classList.remove('danger');
            }
        }
    }

    async _updateTrafficChart() {
        try {
            const res = await fetch(`${this.apiBase}/visual/traffic-chart`);
            const data = await res.json();
            if (this.charts.traffic && !data.error) {
                this.charts.traffic.setOption(data);
            }
        } catch (e) {
            console.error('更新流量图失败:', e);
            this._mockTrafficUpdate();
        }
    }

    _mockTrafficUpdate() {
        if (!this.charts.traffic) return;

        if (!this._mockTrafficData) {
            this._mockTrafficData = { normal: [], attack: [], times: [] };
        }

        const now = Date.now();
        const normal = 50 + 30 * Math.abs(Math.sin(now / 30000)) + Math.random() * 10 - 5;
        const attack = this.isAttackMode ? (200 + Math.random() * 100) : 0;

        this._mockTrafficData.times.push(now);
        this._mockTrafficData.normal.push(normal);
        this._mockTrafficData.attack.push(attack);

        if (this._mockTrafficData.times.length > 60) {
            this._mockTrafficData.times.shift();
            this._mockTrafficData.normal.shift();
            this._mockTrafficData.attack.shift();
        }

        const normalData = this._mockTrafficData.times.map((t, i) => [t, this._mockTrafficData.normal[i]]);
        const attackData = this._mockTrafficData.times.map((t, i) => [t, this._mockTrafficData.attack[i]]);

        this.charts.traffic.setOption({
            title: { text: '网络流量监控 (正常 vs 攻击) - 模拟数据', textStyle: { color: '#ff00ff' } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['正常流量', '攻击流量'], textStyle: { color: '#c0c0e0' } },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            yAxis: {
                type: 'value',
                name: '流量 (KB/s)',
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } },
                splitLine: { lineStyle: { color: 'rgba(22, 33, 62, 0.5)' } }
            },
            series: [
                {
                    name: '正常流量',
                    type: 'line',
                    smooth: true,
                    data: normalData,
                    lineStyle: { color: '#00ff00', width: 2 },
                    areaStyle: { color: 'rgba(0, 255, 0, 0.1)' },
                    symbol: 'none'
                },
                {
                    name: '攻击流量',
                    type: 'line',
                    smooth: true,
                    data: attackData,
                    lineStyle: { color: '#ff3333', width: 2 },
                    areaStyle: { color: 'rgba(255, 51, 51, 0.1)' },
                    symbol: 'none'
                }
            ]
        });
    }

    _bindPasswordControls() {
        document.getElementById('btn-analyze-pwd')?.addEventListener('click', () => {
            const input = document.getElementById('pwd-analyze-input');
            if (input && input.value) {
                this.analyzePassword(input.value);
            }
        });
    }

    async analyzePassword(password) {
        try {
            const strengthData = this._calculatePasswordStrength(password);
            const res = await fetch(`${this.apiBase}/visual/password-strength`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strength_data: strengthData })
            });
            const data = await res.json();
            if (this.charts.password && !data.error) {
                this.charts.password.setOption(data);
            }
        } catch (e) {
            console.error('分析密码失败:', e);
            this._showPasswordChart(this._calculatePasswordStrength(password));
        }
    }

    loadPasswordChart(defaultPwd = '') {
        if (defaultPwd) {
            this.analyzePassword(defaultPwd);
        } else {
            this._showPasswordChart(this._calculatePasswordStrength(''));
        }
    }

    _calculatePasswordStrength(password) {
        const details = [];

        const lengthScore = Math.min(password.length * 5, 25);
        details.push({
            name: '密码长度',
            score: lengthScore,
            pass: password.length >= 12,
            description: password.length >= 12 ? '长度充足' : `建议至少12位 (当前${password.length}位)`
        });

        const hasUpper = /[A-Z]/.test(password);
        details.push({
            name: '大写字母',
            score: hasUpper ? 15 : 0,
            pass: hasUpper,
            description: hasUpper ? '包含大写字母' : '建议添加大写字母'
        });

        const hasLower = /[a-z]/.test(password);
        details.push({
            name: '小写字母',
            score: hasLower ? 15 : 0,
            pass: hasLower,
            description: hasLower ? '包含小写字母' : '建议添加小写字母'
        });

        const hasDigit = /[0-9]/.test(password);
        details.push({
            name: '数字',
            score: hasDigit ? 15 : 0,
            pass: hasDigit,
            description: hasDigit ? '包含数字' : '建议添加数字'
        });

        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        details.push({
            name: '特殊字符',
            score: hasSpecial ? 15 : 0,
            pass: hasSpecial,
            description: hasSpecial ? '包含特殊字符' : '建议添加特殊字符(!@#$%等)'
        });

        const commonPwds = ['password', '123456', 'qwerty', 'admin', 'letmein'];
        const isCommon = commonPwds.some(p => password.toLowerCase().includes(p));
        details.push({
            name: '常见密码检测',
            score: isCommon ? 0 : 15,
            pass: !isCommon,
            description: isCommon ? '包含常见密码词汇，易被破解' : '未检测到常见密码'
        });

        const totalScore = details.reduce((sum, d) => sum + d.score, 0);

        return {
            total_score: Math.min(totalScore, 100),
            details: details
        };
    }

    _showPasswordChart(strengthData) {
        if (!this.charts.password) return;

        const details = strengthData.details || [];
        const categories = details.map(d => d.name);
        const values = details.map(d => d.score);
        const colors = details.map(d => d.pass ? '#00ff00' : '#ff3333');

        this.charts.password.setOption({
            title: { text: '密码强度分项分析', textStyle: { color: '#ff00ff' } },
            tooltip: { trigger: 'axis' },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'value',
                max: 25,
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            yAxis: {
                type: 'category',
                data: categories,
                axisLabel: { color: '#8080a0' },
                axisLine: { lineStyle: { color: '#16213e' } }
            },
            series: [{
                type: 'bar',
                data: values.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
                barWidth: '60%',
                label: {
                    show: true,
                    position: 'right',
                    color: '#c0c0e0',
                    formatter: '{c}分'
                }
            }]
        });
    }
}

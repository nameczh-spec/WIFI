/**
 * WiFi可视化安全学习工具 v2 - 握手模拟脚本
 * 仅供学习研究使用
 */

class HandshakeSimulator {
    constructor(apiBase) {
        this.apiBase = apiBase || '/api';
        this.lessons = [];
        this.currentLessonId = null;
        this.currentStep = 0;
        this.isAutoPlaying = false;
        this.autoPlayTimer = null;
        this.isStarted = false;

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadLessons();
        this.initTabSwitching();
    }

    initTabSwitching() {
        document.querySelectorAll('.practice-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    switchTab(tabName) {
        document.querySelectorAll('.practice-tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });

        document.querySelectorAll('.practice-tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        const targetPanel = document.getElementById(`practice-tab-${tabName}`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }

        if (tabName === 'handshake') {
            if (this.lessons.length === 0) {
                this.loadLessons();
            }
        }
    }

    bindEvents() {
        document.getElementById('btn-handshake-start')?.addEventListener('click', () => this.startSimulation());
        document.getElementById('btn-handshake-next')?.addEventListener('click', () => this.nextStep());
        document.getElementById('btn-handshake-reset')?.addEventListener('click', () => this.resetSimulation());
        document.getElementById('btn-handshake-auto')?.addEventListener('click', () => this.toggleAutoPlay());
    }

    async loadLessons() {
        try {
            const res = await fetch(`${this.apiBase}/handshake/lessons`);
            const data = await res.json();

            if (data.lessons) {
                this.lessons = data.lessons;
                this.renderLessonList();
            }
        } catch (e) {
            console.error('加载课程列表失败:', e);
            this.showLessonListError('加载失败，请稍后重试');
        }
    }

    renderLessonList() {
        const container = document.getElementById('handshake-lesson-list');
        if (!container) return;

        if (this.lessons.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无课程</div>';
            return;
        }

        container.innerHTML = '';
        this.lessons.forEach((lesson, index) => {
            const item = document.createElement('div');
            item.className = 'handshake-lesson-item';
            item.dataset.lessonId = lesson.id;

            const stepNum = lesson.step !== undefined && lesson.step !== null ? lesson.step : (index < 4 ? index + 1 : null);

            item.innerHTML = `
                <div class="lesson-item-header">
                    <span class="lesson-item-title">${lesson.title}</span>
                    ${stepNum ? `<span class="lesson-step-badge">步骤 ${stepNum}</span>` : ''}
                </div>
                <div class="lesson-item-desc">${lesson.description || ''}</div>
            `;

            item.addEventListener('click', () => this.loadLesson(lesson.id));
            container.appendChild(item);
        });
    }

    showLessonListError(message) {
        const container = document.getElementById('handshake-lesson-list');
        if (container) {
            container.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    async loadLesson(lessonId) {
        try {
            const res = await fetch(`${this.apiBase}/handshake/lessons/${lessonId}`);
            const data = await res.json();

            if (data.lesson) {
                this.currentLessonId = lessonId;
                this.highlightActiveLesson(lessonId);
                this.showLessonDetail(data.lesson);
            }
        } catch (e) {
            console.error('加载课程详情失败:', e);
        }
    }

    highlightActiveLesson(lessonId) {
        document.querySelectorAll('.handshake-lesson-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.lessonId === lessonId) {
                item.classList.add('active');
            }
        });
    }

    showLessonDetail(lesson) {
        const panel = document.getElementById('handshake-detail-panel');
        if (!panel) return;

        let keyPointsHtml = '';
        if (lesson.key_points && lesson.key_points.length > 0) {
            keyPointsHtml = `
                <div class="detail-section">
                    <h4>🔑 关键点</h4>
                    <ul class="key-points-list">
                        ${lesson.key_points.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        panel.innerHTML = `
            <div class="detail-header">
                <h4>${lesson.title}</h4>
            </div>
            <div class="detail-content">
                ${lesson.content || ''}
            </div>
            ${keyPointsHtml}
            <div class="detail-warning">
                ⚠ ${lesson.warning || '仅供学习研究使用'}
            </div>
        `;
    }

    async startSimulation() {
        if (this.isStarted) return;

        try {
            const res = await fetch(`${this.apiBase}/handshake/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ssid: 'TestNetwork', password: 'password123' })
            });
            const data = await res.json();

            if (data.success) {
                this.isStarted = true;
                this.currentStep = 0;
                this.updateStepIndicator();
                this.resetVisualState();
                document.getElementById('btn-handshake-start').disabled = true;
            }
        } catch (e) {
            console.error('启动握手模拟失败:', e);
        }
    }

    async nextStep() {
        if (!this.isStarted) {
            await this.startSimulation();
        }

        if (this.currentStep >= 4) return;

        try {
            const res = await fetch(`${this.apiBase}/handshake/next`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();

            if (data.success && data.step) {
                this.currentStep = data.step.step || this.currentStep + 1;
                this.updateStepIndicator();
                this.animateStep(this.currentStep);
                this.showStepDetail(data.step);
                this.updateKeyDerivation(data.step);

                if (data.step.packet) {
                    this.showPacketStructure(data.step.packet);
                }

                if (data.step.completed || this.currentStep >= 4) {
                    this.onSimulationComplete();
                }
            }
        } catch (e) {
            console.error('执行下一步失败:', e);
        }
    }

    async resetSimulation() {
        try {
            const res = await fetch(`${this.apiBase}/handshake/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();

            if (data.success) {
                this.isStarted = false;
                this.currentStep = 0;
                this.isAutoPlaying = false;
                if (this.autoPlayTimer) {
                    clearInterval(this.autoPlayTimer);
                    this.autoPlayTimer = null;
                }
                this.updateStepIndicator();
                this.resetVisualState();
                this.resetKeyDerivation();
                this.resetDetailPanel();
                this.hidePacketStructure();

                const startBtn = document.getElementById('btn-handshake-start');
                if (startBtn) startBtn.disabled = false;

                const autoBtn = document.getElementById('btn-handshake-auto');
                if (autoBtn) autoBtn.textContent = '自动播放';
            }
        } catch (e) {
            console.error('重置握手模拟失败:', e);
        }
    }

    toggleAutoPlay() {
        const btn = document.getElementById('btn-handshake-auto');
        if (!btn) return;

        if (this.isAutoPlaying) {
            this.isAutoPlaying = false;
            if (this.autoPlayTimer) {
                clearInterval(this.autoPlayTimer);
                this.autoPlayTimer = null;
            }
            btn.textContent = '自动播放';
        } else {
            this.isAutoPlaying = true;
            btn.textContent = '暂停';
            this.autoPlayTimer = setInterval(() => {
                if (this.currentStep >= 4) {
                    this.toggleAutoPlay();
                    return;
                }
                this.nextStep();
            }, 2000);
        }
    }

    updateStepIndicator() {
        const indicator = document.getElementById('handshake-step-indicator');
        if (indicator) {
            indicator.textContent = `${this.currentStep} / 4`;
        }
    }

    resetVisualState() {
        document.querySelectorAll('.handshake-msg').forEach(msg => {
            msg.classList.remove('active', 'completed');
        });
    }

    animateStep(stepNum) {
        for (let i = 1; i <= stepNum; i++) {
            const msgEl = document.querySelector(`.handshake-msg.msg-${i}`);
            if (msgEl) {
                if (i === stepNum) {
                    msgEl.classList.add('active');
                    msgEl.classList.remove('completed');
                } else {
                    msgEl.classList.add('completed');
                    msgEl.classList.remove('active');
                }
            }
        }
    }

    showStepDetail(stepData) {
        const panel = document.getElementById('handshake-detail-panel');
        if (!panel) return;

        const packet = stepData.packet || {};
        const direction = packet.direction || '未知';
        const description = packet.description || stepData.description || '';

        let nonceHtml = '';
        if (packet.nonce) {
            nonceHtml = `
                <div class="data-row">
                    <span class="data-label">Nonce:</span>
                    <span class="data-value mono">${packet.nonce.substring(0, 32)}...</span>
                </div>
            `;
        }

        let micHtml = '';
        if (packet.mic) {
            micHtml = `
                <div class="data-row">
                    <span class="data-label">MIC:</span>
                    <span class="data-value mono">${packet.mic}</span>
                </div>
            `;
        }

        let keyPointsHtml = '';
        if (stepData.key_points && stepData.key_points.length > 0) {
            keyPointsHtml = `
                <div class="detail-section">
                    <h4>🔑 关键点</h4>
                    <ul class="key-points-list">
                        ${stepData.key_points.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        panel.innerHTML = `
            <div class="detail-header">
                <h4>${stepData.title || `消息 ${this.currentStep}`}</h4>
                <span class="cyber-tag tag-info">${direction}</span>
            </div>
            <div class="detail-desc">${description}</div>
            <div class="detail-data-panel">
                <div class="data-row">
                    <span class="data-label">步骤:</span>
                    <span class="data-value">第 ${this.currentStep} 步 / 共 4 步</span>
                </div>
                ${nonceHtml}
                ${micHtml}
            </div>
            ${stepData.content ? `<div class="detail-content">${stepData.content}</div>` : ''}
            ${keyPointsHtml}
            <div class="detail-warning">
                ⚠ ${stepData.warning || '仅供学习研究使用'}
            </div>
        `;
    }

    updateKeyDerivation(stepData) {
        const step = this.currentStep;

        const pskStatus = document.getElementById('key-status-psk');
        const pmkStatus = document.getElementById('key-status-pmk');
        const ptkStatus = document.getElementById('key-status-ptk');
        const gtkStatus = document.getElementById('key-status-gtk');

        const pmkAlgo = document.getElementById('key-algo-pmk');
        const ptkAlgo = document.getElementById('key-algo-ptk');
        const gtkAlgo = document.getElementById('key-algo-gtk');
        const ptkParts = document.getElementById('key-parts-ptk');

        this.setKeyStatus(pskStatus, 'active');

        if (step >= 1) {
            this.setKeyStatus(pmkStatus, 'active');
            if (pmkAlgo) pmkAlgo.style.display = 'block';
        }

        if (step >= 2) {
            this.setKeyStatus(ptkStatus, 'active');
            if (ptkAlgo) ptkAlgo.style.display = 'block';
            if (ptkParts) ptkParts.style.display = 'flex';
        }

        if (step >= 3) {
            this.setKeyStatus(gtkStatus, 'active');
            if (gtkAlgo) gtkAlgo.style.display = 'block';
        }
    }

    setKeyStatus(element, status) {
        if (!element) return;
        element.classList.remove('key-status-wait', 'key-status-active', 'key-status-done');
        if (status === 'active') {
            element.classList.add('key-status-active');
            element.textContent = '生成中';
        } else if (status === 'done') {
            element.classList.add('key-status-done');
            element.textContent = '已生成';
        } else {
            element.classList.add('key-status-wait');
            element.textContent = '等待中';
        }
    }

    resetKeyDerivation() {
        const keys = ['psk', 'pmk', 'ptk', 'gtk'];
        keys.forEach(key => {
            const statusEl = document.getElementById(`key-status-${key}`);
            const algoEl = document.getElementById(`key-algo-${key}`);
            if (statusEl) {
                statusEl.classList.remove('key-status-active', 'key-status-done');
                statusEl.classList.add('key-status-wait');
                statusEl.textContent = '等待中';
            }
            if (algoEl) algoEl.style.display = 'none';
        });

        const ptkParts = document.getElementById('key-parts-ptk');
        if (ptkParts) ptkParts.style.display = 'none';
    }

    resetDetailPanel() {
        const panel = document.getElementById('handshake-detail-panel');
        if (panel) {
            panel.innerHTML = `
                <div class="empty-state">
                    <p>点击"开始"按钮启动握手模拟</p>
                    <p style="margin-top: 10px; color: var(--text-secondary);">系统将逐步展示WPA四次握手的完整过程</p>
                </div>
            `;
        }
    }

    showPacketStructure(packet) {
        const card = document.getElementById('packet-structure-card');
        const panel = document.getElementById('packet-structure-panel');
        if (!card || !panel) return;

        card.style.display = 'block';

        const keyInfo = packet.key_info || '0x0000';
        const keyLength = packet.key_length || 16;
        const replayCounter = packet.replay_counter || 1;

        panel.innerHTML = `
            <div class="packet-field">
                <span class="field-name">EAPOL-Key</span>
                <span class="field-desc">密钥信息帧</span>
            </div>
            <div class="packet-field">
                <span class="field-name">Key Information</span>
                <span class="field-value mono">${keyInfo}</span>
            </div>
            <div class="packet-field">
                <span class="field-name">Key Length</span>
                <span class="field-value">${keyLength} bytes</span>
            </div>
            <div class="packet-field">
                <span class="field-name">Replay Counter</span>
                <span class="field-value">${replayCounter}</span>
            </div>
            ${packet.nonce ? `
            <div class="packet-field">
                <span class="field-name">Nonce</span>
                <span class="field-value mono small">${packet.nonce.substring(0, 24)}...</span>
            </div>
            ` : ''}
            ${packet.mic ? `
            <div class="packet-field">
                <span class="field-name">MIC</span>
                <span class="field-value mono small">${packet.mic}</span>
            </div>
            ` : ''}
            ${packet.key_data_length ? `
            <div class="packet-field">
                <span class="field-name">Key Data Length</span>
                <span class="field-value">${packet.key_data_length} bytes</span>
            </div>
            ` : ''}
        `;
    }

    hidePacketStructure() {
        const card = document.getElementById('packet-structure-card');
        if (card) card.style.display = 'none';
    }

    onSimulationComplete() {
        if (this.isAutoPlaying) {
            this.toggleAutoPlay();
        }

        const indicator = document.getElementById('handshake-step-indicator');
        if (indicator) {
            indicator.classList.remove('tag-info');
            indicator.classList.add('tag-safe');
            indicator.textContent = '完成 ✓';
        }

        for (let i = 1; i <= 4; i++) {
            const msgEl = document.querySelector(`.handshake-msg.msg-${i}`);
            if (msgEl) {
                msgEl.classList.add('completed');
                msgEl.classList.remove('active');
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.handshakeSimulator = new HandshakeSimulator('/api');
});

/**
 * WiFi可视化安全学习工具 v2 - 攻防演练脚本
 * 仅供学习研究使用
 */

class AttackDefense {
    constructor(apiBase) {
        this.apiBase = apiBase || '/api';
        this.categories = [];
        this.scenarios = [];
        this.currentCategory = 'all';
        this.currentScenario = null;
        this.simulationState = {
            active: false,
            currentStep: 0,
            totalSteps: 0,
            log: []
        };

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCategories();
        this.loadScenarios();
    }

    bindEvents() {
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.switchCategory(category);
            });
        });

        document.getElementById('btn-sim-start')?.addEventListener('click', () => this.startSimulation());
        document.getElementById('btn-sim-next')?.addEventListener('click', () => this.nextSimulationStep());
        document.getElementById('btn-sim-reset')?.addEventListener('click', () => this.resetSimulation());
    }

    async loadCategories() {
        try {
            const res = await fetch(`${this.apiBase}/attack/categories`);
            const data = await res.json();
            if (data.categories) {
                this.categories = data.categories;
            }
        } catch (e) {
            console.error('加载分类失败:', e);
        }
    }

    async loadScenarios(category = 'all') {
        try {
            const url = category === 'all'
                ? `${this.apiBase}/attack/scenarios`
                : `${this.apiBase}/attack/scenarios?category=${category}`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.scenarios) {
                this.scenarios = data.scenarios;
                this.renderScenarioList();
            } else if (data.error) {
                this.showScenarioListError(data.error);
            }
        } catch (e) {
            console.error('加载场景列表失败:', e);
            this.showScenarioListError('加载失败，请稍后重试');
        }
    }

    switchCategory(category) {
        this.currentCategory = category;

        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.category === category) {
                tab.classList.add('active');
            }
        });

        this.loadScenarios(category);
    }

    renderScenarioList() {
        const container = document.getElementById('scenario-list');
        if (!container) return;

        if (this.scenarios.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无攻击场景</div>';
            return;
        }

        container.innerHTML = '';
        this.scenarios.forEach(scenario => {
            const card = document.createElement('div');
            card.className = 'scenario-list-item';
            card.dataset.scenarioId = scenario.id;

            const difficultyClass = this.getDifficultyClass(scenario.difficulty);
            const categoryClass = this.getCategoryClass(scenario.category);

            card.innerHTML = `
                <div class="scenario-item-header">
                    <span class="scenario-item-title">${scenario.name}</span>
                    <span class="cyber-tag ${difficultyClass}">${scenario.difficulty || '未知'}</span>
                </div>
                <div class="scenario-item-desc">${scenario.description || ''}</div>
                <div class="scenario-item-footer">
                    <span class="cyber-tag ${categoryClass}">${this.getCategoryLabel(scenario.category)}</span>
                </div>
            `;

            card.addEventListener('click', () => this.loadScenario(scenario.id));
            container.appendChild(card);
        });
    }

    getDifficultyClass(difficulty) {
        const map = {
            '入门': 'tag-safe',
            '简单': 'tag-safe',
            '中等': 'tag-warning',
            '困难': 'tag-danger',
            '专家': 'tag-danger'
        };
        return map[difficulty] || 'tag-info';
    }

    getCategoryClass(category) {
        const map = {
            'wep': 'tag-danger',
            'wpa': 'tag-warning',
            'dos': 'tag-danger',
            'evil_twin': 'tag-warning',
            'krack': 'tag-danger'
        };
        return map[category] || 'tag-info';
    }

    getCategoryLabel(category) {
        const map = {
            'wep': 'WEP攻击',
            'wpa': 'WPA攻击',
            'dos': 'DoS攻击',
            'evil_twin': '邪恶双生子',
            'krack': 'KRACK'
        };
        return map[category] || category;
    }

    showScenarioListError(message) {
        const container = document.getElementById('scenario-list');
        if (container) {
            container.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    async loadScenario(scenarioId) {
        try {
            const res = await fetch(`${this.apiBase}/attack/scenarios/${scenarioId}`);
            const data = await res.json();

            if (data.scenario) {
                this.currentScenario = data.scenario;
                this.renderScenarioDetail();
                this.loadDefenseSummary(scenarioId);
                this.resetSimulation();
                this.highlightActiveScenario(scenarioId);
            } else if (data.error) {
                this.showScenarioDetailError(data.error);
            }
        } catch (e) {
            console.error('加载场景详情失败:', e);
            this.showScenarioDetailError('加载失败，请稍后重试');
        }
    }

    highlightActiveScenario(scenarioId) {
        document.querySelectorAll('.scenario-list-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.scenarioId == scenarioId) {
                item.classList.add('active');
            }
        });
    }

    renderScenarioDetail() {
        const titleEl = document.getElementById('scenario-title');
        const categoryEl = document.getElementById('scenario-category');
        const difficultyEl = document.getElementById('scenario-difficulty');
        const detailEl = document.getElementById('scenario-detail');

        if (!this.currentScenario) return;

        if (titleEl) titleEl.textContent = this.currentScenario.name || '未命名场景';

        if (categoryEl) {
            categoryEl.textContent = this.getCategoryLabel(this.currentScenario.category);
            categoryEl.className = `cyber-tag ${this.getCategoryClass(this.currentScenario.category)}`;
        }

        if (difficultyEl) {
            difficultyEl.textContent = `难度: ${this.currentScenario.difficulty || '未知'}`;
            difficultyEl.className = `cyber-tag ${this.getDifficultyClass(this.currentScenario.difficulty)}`;
        }

        if (!detailEl) return;

        let html = '';

        if (this.currentScenario.principle) {
            html += `
                <div class="detail-section">
                    <h4 class="detail-section-title">📖 攻击原理</h4>
                    <div class="detail-content">${this.currentScenario.principle}</div>
                </div>
            `;
        }

        if (this.currentScenario.attack_steps && this.currentScenario.attack_steps.length > 0) {
            html += `
                <div class="detail-section">
                    <h4 class="detail-section-title">⚔️ 攻击步骤</h4>
                    <ol class="step-list">
                        ${this.currentScenario.attack_steps.map((step, i) => `
                            <li class="step-item">
                                <span class="step-number">${i + 1}</span>
                                <span class="step-text">${step}</span>
                            </li>
                        `).join('')}
                    </ol>
                </div>
            `;
        }

        if (this.currentScenario.impact) {
            html += `
                <div class="detail-section">
                    <h4 class="detail-section-title">⚠️ 攻击影响</h4>
                    <div class="impact-box">
                        ${this.currentScenario.impact}
                    </div>
                </div>
            `;
        }

        if (this.currentScenario.defense_methods && this.currentScenario.defense_methods.length > 0) {
            html += `
                <div class="detail-section">
                    <h4 class="detail-section-title">🛡️ 防御方法</h4>
                    <ul class="defense-list">
                        ${this.currentScenario.defense_methods.map(method => `
                            <li class="defense-item">
                                <span class="defense-icon">✓</span>
                                <span class="defense-text">${method}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        detailEl.innerHTML = html;
    }

    showScenarioDetailError(message) {
        const detailEl = document.getElementById('scenario-detail');
        if (detailEl) {
            detailEl.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    async loadDefenseSummary(scenarioId) {
        try {
            const res = await fetch(`${this.apiBase}/attack/defense-summary?scenario_id=${scenarioId}`);
            const data = await res.json();

            if (data.summary) {
                this.renderDefenseSummary(data.summary);
            }
        } catch (e) {
            console.error('加载防御汇总失败:', e);
        }
    }

    renderDefenseSummary(summary) {
        const container = document.getElementById('defense-summary');
        if (!container) return;

        let html = '';

        if (summary.basic && summary.basic.length > 0) {
            html += `
                <div class="defense-category">
                    <h5 class="defense-category-title">🔒 基础防御</h5>
                    <ul class="defense-method-list">
                        ${summary.basic.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (summary.advanced && summary.advanced.length > 0) {
            html += `
                <div class="defense-category">
                    <h5 class="defense-category-title">🔐 高级防御</h5>
                    <ul class="defense-method-list">
                        ${summary.advanced.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (summary.monitoring && summary.monitoring.length > 0) {
            html += `
                <div class="defense-category">
                    <h5 class="defense-category-title">📡 监控检测</h5>
                    <ul class="defense-method-list">
                        ${summary.monitoring.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (summary.response && summary.response.length > 0) {
            html += `
                <div class="defense-category">
                    <h5 class="defense-category-title">🚨 应急响应</h5>
                    <ul class="defense-method-list">
                        ${summary.response.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (!html) {
            html = '<div class="empty-state">暂无防御汇总信息</div>';
        }

        container.innerHTML = html;
    }

    async startSimulation() {
        if (!this.currentScenario) {
            alert('请先选择一个攻击场景');
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/attack/simulate/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario_id: this.currentScenario.id
                })
            });

            const data = await res.json();

            if (data.success) {
                this.simulationState.active = true;
                this.simulationState.currentStep = 0;
                this.simulationState.totalSteps = data.total_steps || 0;
                this.simulationState.log = [];

                this.addLogEntry('info', `[系统] 开始模拟: ${this.currentScenario.name}`);
                if (data.message) {
                    this.addLogEntry('info', `[系统] ${data.message}`);
                }

                this.updateSimulationUI();
                this.updateSimulationButtons(true, false, true);
            } else if (data.error) {
                alert(data.error);
            }
        } catch (e) {
            console.error('开始模拟失败:', e);
            alert('开始模拟失败，请稍后重试');
        }
    }

    async nextSimulationStep() {
        if (!this.simulationState.active) return;

        try {
            const res = await fetch(`${this.apiBase}/attack/simulate/next`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario_id: this.currentScenario?.id
                })
            });

            const data = await res.json();

            if (data.step !== undefined) {
                this.simulationState.currentStep = data.step;

                if (data.log) {
                    this.addLogEntry(data.log_type || 'info', data.log);
                }

                if (data.defense_tip) {
                    this.showDefenseTip(data.defense_tip);
                }

                if (data.completed) {
                    this.simulationState.active = false;
                    this.addLogEntry('success', '[系统] 模拟演练完成！');
                    this.updateSimulationButtons(false, false, true);
                }

                this.updateSimulationUI();
            } else if (data.error) {
                this.addLogEntry('error', `[错误] ${data.error}`);
            }
        } catch (e) {
            console.error('执行下一步失败:', e);
            this.addLogEntry('error', '[错误] 执行下一步失败');
        }
    }

    async resetSimulation() {
        try {
            await fetch(`${this.apiBase}/attack/simulate/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario_id: this.currentScenario?.id
                })
            });
        } catch (e) {
            console.error('重置模拟失败:', e);
        }

        this.simulationState.active = false;
        this.simulationState.currentStep = 0;
        this.simulationState.totalSteps = 0;
        this.simulationState.log = [];

        const logContainer = document.getElementById('simulation-log');
        if (logContainer) {
            logContainer.innerHTML = '<div class="log-entry info">[系统] 等待开始模拟演练...</div>';
        }

        const defenseTip = document.getElementById('defense-tip');
        if (defenseTip) {
            defenseTip.style.display = 'none';
        }

        this.updateSimulationUI();
        this.updateSimulationButtons(true, false, false);
    }

    addLogEntry(type, message) {
        this.simulationState.log.push({ type, message, time: new Date() });

        const logContainer = document.getElementById('simulation-log');
        if (!logContainer) return;

        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = message;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    showDefenseTip(tip) {
        const tipEl = document.getElementById('defense-tip');
        const tipContent = document.getElementById('defense-tip-content');

        if (tipEl && tipContent) {
            tipContent.textContent = tip;
            tipEl.style.display = 'block';
        }
    }

    updateSimulationUI() {
        const stepIndicator = document.getElementById('sim-step-indicator');
        const progressBar = document.getElementById('sim-progress-bar');

        if (stepIndicator) {
            if (this.simulationState.totalSteps > 0) {
                stepIndicator.innerHTML = `
                    <span class="sim-step">步骤 ${this.simulationState.currentStep} / ${this.simulationState.totalSteps}</span>
                `;
            } else if (this.simulationState.active) {
                stepIndicator.innerHTML = `<span class="sim-step">进行中...</span>`;
            } else {
                stepIndicator.innerHTML = `<span class="sim-step">未开始</span>`;
            }
        }

        if (progressBar && this.simulationState.totalSteps > 0) {
            const progress = (this.simulationState.currentStep / this.simulationState.totalSteps) * 100;
            progressBar.style.width = `${Math.min(progress, 100)}%`;
        } else if (progressBar) {
            progressBar.style.width = '0%';
        }
    }

    updateSimulationButtons(startEnabled, nextEnabled, resetEnabled) {
        const startBtn = document.getElementById('btn-sim-start');
        const nextBtn = document.getElementById('btn-sim-next');
        const resetBtn = document.getElementById('btn-sim-reset');

        if (startBtn) startBtn.disabled = !startEnabled;
        if (nextBtn) nextBtn.disabled = !nextEnabled;
        if (resetBtn) resetBtn.disabled = !resetEnabled;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.attackDefense = new AttackDefense('/api');
});

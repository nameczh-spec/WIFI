/**
 * WiFi安全学习平台 - AI聊天模块
 */

class AIChat {
    constructor(apiBase = '/api') {
        this.apiBase = apiBase;
        this.currentScenario = 'default';
        this.scenarios = [];
        this.isSending = false;
        this.typewriterTimer = null;
        this.selectedLevel = 'beginner';
        this.storageKey = 'wifi_ai_chat_history';

        this.scenarioIcons = {
            'default': '🤖',
            'teaching': '👨‍🏫',
            'attack_defense': '⚔️',
            'ctf': '🏆',
            'practice': '🎯',
            'wifi_basic': '📡'
        };

        this.scenarioDescriptions = {
            'default': '有问必答的WiFi安全助手',
            'teaching': '循循善诱的课程导师，由浅入深讲解',
            'attack_defense': '攻防演练教练，模拟真实安全场景',
            'ctf': 'CTF解题助手，提供分级提示',
            'practice': '智能陪练伙伴，通过对话巩固知识',
            'wifi_basic': 'WiFi基础知识专家，通俗易懂'
        };

        this.init();
    }

    init() {
        this.loadScenarios();
        this.bindEvents();
        this.loadHistory();
    }

    async loadScenarios() {
        try {
            const res = await fetch(`${this.apiBase}/ai/scenarios`);
            const data = await res.json();

            if (data.success && data.scenarios) {
                this.scenarios = data.scenarios;
                this.renderScenarioList();
            } else {
                this.useFallbackScenarios();
            }
        } catch (e) {
            console.error('加载场景列表失败:', e);
            this.useFallbackScenarios();
        }
    }

    useFallbackScenarios() {
        this.scenarios = [
            { id: 'default', name: '通用问答', description: '有问必答的WiFi安全助手' },
            { id: 'teaching', name: '教学导师', description: '循循善诱的课程导师' },
            { id: 'attack_defense', name: '攻防演练', description: '模拟真实安全攻防场景' },
            { id: 'ctf', name: 'CTF助手', description: 'CTF解题辅助与提示' },
            { id: 'practice', name: '智能陪练', description: '通过对话巩固知识' },
            { id: 'wifi_basic', name: 'WiFi基础', description: 'WiFi基础知识问答' }
        ];
        this.renderScenarioList();
    }

    renderScenarioList() {
        const listEl = document.getElementById('scenario-list');
        if (!listEl) return;

        if (this.scenarios.length === 0) {
            listEl.innerHTML = '<div class="empty-state">暂无场景</div>';
            return;
        }

        listEl.innerHTML = '';
        this.scenarios.forEach(scenario => {
            const item = document.createElement('div');
            item.className = `scenario-item ${scenario.id === this.currentScenario ? 'active' : ''}`;
            item.dataset.scenario = scenario.id;

            const icon = this.scenarioIcons[scenario.id] || '🤖';
            const desc = scenario.description || this.scenarioDescriptions[scenario.id] || '';

            item.innerHTML = `
                <div class="scenario-item-icon">${icon}</div>
                <div class="scenario-item-content">
                    <div class="scenario-item-name">${scenario.name}</div>
                    <div class="scenario-item-desc">${desc}</div>
                </div>
            `;

            item.addEventListener('click', () => this.switchScenario(scenario.id));
            listEl.appendChild(item);
        });
    }

    switchScenario(scenarioId) {
        if (scenarioId === this.currentScenario) return;

        this.currentScenario = scenarioId;

        document.querySelectorAll('.scenario-item').forEach(item => {
            item.classList.toggle('active', item.dataset.scenario === scenarioId);
        });

        const scenario = this.scenarios.find(s => s.id === scenarioId);
        if (scenario) {
            const iconEl = document.getElementById('current-scenario-icon');
            const nameEl = document.getElementById('current-scenario-name');
            const descEl = document.getElementById('current-scenario-desc');

            if (iconEl) iconEl.textContent = this.scenarioIcons[scenarioId] || '🤖';
            if (nameEl) nameEl.textContent = scenario.name;
            if (descEl) descEl.textContent = scenario.description || this.scenarioDescriptions[scenarioId] || '';
        }

        const savedHistory = this.getScenarioHistory(scenarioId);
        if (savedHistory && savedHistory.length > 0) {
            this.renderMessages(savedHistory);
        } else {
            this.clearMessages(false);
            this.addWelcomeMessage(scenarioId);
        }
    }

    addWelcomeMessage(scenarioId) {
        const welcomes = {
            'default': '你好！我是你的WiFi安全学习助手。有什么问题都可以问我哦！',
            'teaching': '你好！我是你的专属WiFi安全导师。让我们一起开始学习之旅吧！你目前对WiFi安全了解多少呢？',
            'attack_defense': '欢迎来到攻防演练模式！我会带你模拟各种安全场景，学习攻击原理和防御方法。想从哪个场景开始？',
            'ctf': '嗨，CTF挑战者！遇到难题了吗？我会给你分级提示，帮助你靠自己的能力解决问题。说说看题目吧！',
            'practice': '你好！我是你的智能陪练伙伴。通过问答和场景练习，我们一起巩固WiFi安全知识。准备好了吗？',
            'wifi_basic': '欢迎！我来帮你打牢WiFi基础知识。有什么不懂的尽管问，我会用通俗易懂的方式为你解答！'
        };

        const message = welcomes[scenarioId] || welcomes['default'];
        this.addMessage(message, 'ai', false);
    }

    bindEvents() {
        const sendBtn = document.getElementById('btn-send');
        const inputEl = document.getElementById('chat-input');
        const clearBtn = document.getElementById('btn-clear-history');
        const learningPathBtn = document.getElementById('btn-learning-path');
        const closeModalBtn = document.getElementById('btn-close-modal');
        const generatePathBtn = document.getElementById('btn-generate-path');
        const modalOverlay = document.getElementById('learning-path-modal');

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (inputEl) {
            inputEl.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearHistory());
        }

        if (learningPathBtn) {
            learningPathBtn.addEventListener('click', () => this.openLearningPathModal());
        }

        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => this.closeLearningPathModal());
        }

        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    this.closeLearningPathModal();
                }
            });
        }

        if (generatePathBtn) {
            generatePathBtn.addEventListener('click', () => this.generateLearningPath());
        }

        document.querySelectorAll('.level-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.selectedLevel = btn.dataset.level;
            });
        });
    }

    async sendMessage() {
        const inputEl = document.getElementById('chat-input');
        const message = inputEl.value.trim();

        if (!message || this.isSending) return;

        if (!window.app || !window.app.aiConfigured) {
            this.showError('请先在设置中配置AI API密钥');
            return;
        }

        this.isSending = true;
        this.setSendingState(true);

        this.addMessage(message, 'user');
        inputEl.value = '';

        const aiMessageEl = this.addMessage('', 'ai', true);

        try {
            const res = await fetch(`${this.apiBase}/ai/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, scenario: this.currentScenario })
            });

            const data = await res.json();

            if (data.success && data.content) {
                this.typewriterEffect(aiMessageEl, data.content);
                this.saveMessage(message, 'user');
                this.saveMessage(data.content, 'ai');
            } else {
                const errorMsg = data.error || 'AI响应失败，请稍后重试';
                this.typewriterEffect(aiMessageEl, `⚠️ ${errorMsg}`);
            }
        } catch (e) {
            console.error('AI请求失败:', e);
            this.typewriterEffect(aiMessageEl, '⚠️ 网络错误，请检查网络连接后重试');
        } finally {
            this.isSending = false;
            this.setSendingState(false);
        }
    }

    addMessage(content, type, isPlaceholder = false) {
        const container = document.getElementById('chat-messages');
        if (!container) return null;

        const div = document.createElement('div');
        div.className = `message ${type === 'ai' ? 'ai-message' : 'user-message'}`;

        const avatar = type === 'ai' ? '🤖' : '👤';

        div.innerHTML = `
            <span class="avatar">${avatar}</span>
            <div class="message-content ${isPlaceholder ? 'typing-placeholder' : ''}">
                ${isPlaceholder ? '<span class="typing-cursor"></span>' : this.formatMessage(content)}
            </div>
        `;

        container.appendChild(div);
        this.scrollToBottom();

        return div.querySelector('.message-content');
    }

    formatMessage(text) {
        if (!text) return '';

        let html = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');
        html = html.replace(/\n/g, '<br>');

        html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
        html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');

        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
        html = html.replace(/<\/ul>\n<ul>/g, '');

        return html;
    }

    typewriterEffect(element, text, speed = 20) {
        if (this.typewriterTimer) {
            clearInterval(this.typewriterTimer);
        }

        element.classList.remove('typing-placeholder');
        element.innerHTML = '<span class="typing-cursor"></span>';

        let index = 0;
        const cursor = element.querySelector('.typing-cursor');

        this.typewriterTimer = setInterval(() => {
            if (index < text.length) {
                const char = text[index];
                const textNode = document.createTextNode(char);
                element.insertBefore(textNode, cursor);
                index++;
                this.scrollToBottom();
            } else {
                clearInterval(this.typewriterTimer);
                this.typewriterTimer = null;
                cursor.remove();
                element.innerHTML = this.formatMessage(text);
                this.scrollToBottom();
            }
        }, speed);
    }

    setSendingState(sending) {
        const btn = document.getElementById('btn-send');
        const btnText = btn?.querySelector('.btn-text');
        const btnLoading = btn?.querySelector('.btn-loading');
        const input = document.getElementById('chat-input');

        if (btn) btn.disabled = sending;
        if (btnText) btnText.style.display = sending ? 'none' : 'inline';
        if (btnLoading) btnLoading.style.display = sending ? 'inline' : 'none';
        if (input) input.disabled = sending;
    }

    scrollToBottom() {
        const container = document.getElementById('chat-messages');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    renderMessages(messages) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        container.innerHTML = '';
        messages.forEach(msg => {
            this.addMessage(msg.content, msg.role);
        });
    }

    clearMessages(showWelcome = true) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        container.innerHTML = '';

        if (showWelcome) {
            this.addWelcomeMessage(this.currentScenario);
        }
    }

    async clearHistory() {
        if (!confirm('确定要清空当前对话历史吗？')) return;

        try {
            await fetch(`${this.apiBase}/ai/clear`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (e) {
            console.error('清除历史失败:', e);
        }

        this.clearScenarioHistory(this.currentScenario);
        this.clearMessages(true);

        if (window.app) {
            window.app.showNotification('对话历史已清空', 'success');
        }
    }

    saveMessage(content, role) {
        const allHistory = this.getAllHistory();
        if (!allHistory[this.currentScenario]) {
            allHistory[this.currentScenario] = [];
        }
        allHistory[this.currentScenario].push({
            role,
            content,
            timestamp: Date.now()
        });

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(allHistory));
        } catch (e) {
            console.error('保存历史失败:', e);
        }
    }

    getAllHistory() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : {};
        } catch (e) {
            return {};
        }
    }

    getScenarioHistory(scenarioId) {
        const allHistory = this.getAllHistory();
        return allHistory[scenarioId] || [];
    }

    clearScenarioHistory(scenarioId) {
        const allHistory = this.getAllHistory();
        delete allHistory[scenarioId];
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(allHistory));
        } catch (e) {
            console.error('清除场景历史失败:', e);
        }
    }

    loadHistory() {
        const savedHistory = this.getScenarioHistory(this.currentScenario);
        if (savedHistory && savedHistory.length > 0) {
            this.renderMessages(savedHistory);
        }
    }

    showError(message) {
        if (window.app) {
            window.app.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }

    openLearningPathModal() {
        const modal = document.getElementById('learning-path-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    closeLearningPathModal() {
        const modal = document.getElementById('learning-path-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async generateLearningPath() {
        if (!window.app || !window.app.aiConfigured) {
            this.showError('请先在设置中配置AI API密钥');
            return;
        }

        const contentEl = document.getElementById('learning-path-content');
        const btn = document.getElementById('btn-generate-path');

        if (contentEl) {
            contentEl.innerHTML = `
                <div class="loading-path">
                    <div class="loading-spinner"></div>
                    <p>正在生成个性化学习路径...</p>
                </div>
            `;
        }

        if (btn) {
            btn.disabled = true;
            btn.textContent = '生成中...';
        }

        try {
            const res = await fetch(`${this.apiBase}/ai/learning-path`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level: this.selectedLevel })
            });

            const data = await res.json();

            if (data.success && data.content) {
                if (contentEl) {
                    contentEl.innerHTML = `
                        <div class="path-result">
                            ${this.formatMessage(data.content)}
                        </div>
                    `;
                }
            } else {
                const errorMsg = data.error || '生成失败，请稍后重试';
                if (contentEl) {
                    contentEl.innerHTML = `<div class="error-message">⚠️ ${errorMsg}</div>`;
                }
            }
        } catch (e) {
            console.error('生成学习路径失败:', e);
            if (contentEl) {
                contentEl.innerHTML = '<div class="error-message">⚠️ 网络错误，请检查网络连接</div>';
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '生成学习路径';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.aiChat = new AIChat('/api');
});

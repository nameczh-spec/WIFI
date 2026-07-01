/**
 * WiFi可视化安全学习工具 v2 - 教学模式脚本
 * 仅供学习研究使用
 */

class TeachingMode {
    constructor(apiBase) {
        this.apiBase = apiBase || '/api';
        this.modules = [];
        this.currentModule = null;
        this.currentStepIndex = 0;
        this.currentQuiz = null;
        this.selectedQuizOption = null;

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadModules();
    }

    bindEvents() {
        document.getElementById('btn-prev-step')?.addEventListener('click', () => this.prevStep());
        document.getElementById('btn-next-step')?.addEventListener('click', () => this.nextStep());
        document.getElementById('btn-submit-quiz')?.addEventListener('click', () => this.submitQuiz());
        document.getElementById('btn-next-after-quiz')?.addEventListener('click', () => this.continueAfterQuiz());
    }

    async loadModules() {
        try {
            const res = await fetch(`${this.apiBase}/teaching/modules`);
            const data = await res.json();

            if (data.modules) {
                this.modules = data.modules;
                this.renderModuleList();
            } else if (data.error) {
                this.showModuleListError(data.error);
            }
        } catch (e) {
            console.error('加载模块列表失败:', e);
            this.showModuleListError('加载失败，请稍后重试');
        }
    }

    renderModuleList() {
        const container = document.getElementById('module-list');
        if (!container) return;

        if (this.modules.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无学习模块</div>';
            return;
        }

        container.innerHTML = '';
        this.modules.forEach(module => {
            const card = document.createElement('div');
            card.className = 'module-list-item';
            card.dataset.moduleId = module.id;

            const progress = module.progress !== undefined ? module.progress : 0;
            const difficultyClass = this.getDifficultyClass(module.difficulty);

            card.innerHTML = `
                <div class="module-item-header">
                    <span class="module-item-title">${module.name}</span>
                    <span class="cyber-tag ${difficultyClass}">${module.difficulty || '未知'}</span>
                </div>
                <div class="module-item-desc">${module.description || ''}</div>
                <div class="module-item-progress">
                    <div class="cyber-progress small">
                        <div class="progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${progress}%</span>
                </div>
            `;

            card.addEventListener('click', () => this.loadModule(module.id));
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

    showModuleListError(message) {
        const container = document.getElementById('module-list');
        if (container) {
            container.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    async loadModule(moduleId) {
        const module = this.modules.find(m => m.id === moduleId);
        if (!module) return;

        try {
            const res = await fetch(`${this.apiBase}/teaching/modules/${moduleId}`);
            const data = await res.json();

            if (data.module) {
                this.currentModule = data.module;
                this.currentStepIndex = 0;
                this.selectedQuizOption = null;
                this.updateModuleHeader();
                this.renderCurrentStep();
                this.updateNavigationButtons();
                this.highlightActiveModule(moduleId);
            } else if (data.error) {
                this.showStepContentError(data.error);
            }
        } catch (e) {
            console.error('加载模块详情失败:', e);
            this.showStepContentError('加载模块失败，请稍后重试');
        }
    }

    highlightActiveModule(moduleId) {
        document.querySelectorAll('.module-list-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.moduleId == moduleId) {
                item.classList.add('active');
            }
        });
    }

    updateModuleHeader() {
        if (!this.currentModule) return;

        const titleEl = document.getElementById('current-module-title');
        const difficultyEl = document.getElementById('current-module-difficulty');
        const progressBar = document.getElementById('teaching-progress-bar');
        const progressText = document.getElementById('progress-text');

        if (titleEl) titleEl.textContent = this.currentModule.name || '未命名模块';

        if (difficultyEl) {
            difficultyEl.textContent = this.currentModule.difficulty || '未知';
            difficultyEl.className = `cyber-tag ${this.getDifficultyClass(this.currentModule.difficulty)}`;
        }

        const progress = this.currentModule.progress !== undefined ? this.currentModule.progress : 0;
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${progress}%`;
    }

    renderCurrentStep() {
        const contentEl = document.getElementById('step-content');
        const quizSection = document.getElementById('quiz-section');
        if (!contentEl || !this.currentModule) return;

        const steps = this.currentModule.steps || [];
        if (steps.length === 0) {
            contentEl.innerHTML = '<div class="empty-state">该模块暂无学习内容</div>';
            return;
        }

        if (this.currentStepIndex >= steps.length) {
            this.showModuleComplete();
            return;
        }

        const step = steps[this.currentStepIndex];

        if (step.type === 'quiz') {
            this.renderQuiz(step);
            return;
        }

        quizSection.style.display = 'none';

        let html = '';

        html += `<div class="step-title">${step.title || `第 ${this.currentStepIndex + 1} 步`}</div>`;

        if (step.content) {
            html += `<div class="step-body">${step.content}</div>`;
        }

        if (step.key_points && step.key_points.length > 0) {
            html += `
                <div class="step-section">
                    <h4 class="section-title">🔑 关键点</h4>
                    <ul class="key-points-list">
                        ${step.key_points.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (step.code_example) {
            html += `
                <div class="step-section">
                    <h4 class="section-title">💻 代码示例</h4>
                    <div class="code-block">
                        <pre><code>${this.escapeHtml(step.code_example)}</code></pre>
                    </div>
                </div>
            `;
        }

        if (step.warning) {
            html += `
                <div class="step-section">
                    <div class="warning-box">
                        <strong>⚠ 注意：</strong>${step.warning}
                    </div>
                </div>
            `;
        }

        contentEl.innerHTML = html;
        contentEl.scrollTop = 0;
    }

    renderQuiz(quizStep) {
        const contentEl = document.getElementById('step-content');
        const quizSection = document.getElementById('quiz-section');
        const quizQuestion = document.getElementById('quiz-question');
        const quizOptions = document.getElementById('quiz-options');
        const quizResult = document.getElementById('quiz-result');
        const submitBtn = document.getElementById('btn-submit-quiz');
        const nextBtn = document.getElementById('btn-next-after-quiz');

        if (!contentEl || !quizSection) return;

        contentEl.innerHTML = `
            <div class="step-title">📝 章节测验</div>
            <div class="step-body">
                <p>完成本章节学习后，来测试一下你的掌握程度吧！</p>
            </div>
        `;

        this.currentQuiz = quizStep;
        this.selectedQuizOption = null;

        quizQuestion.textContent = quizStep.question || '';
        quizOptions.innerHTML = '';
        quizResult.style.display = 'none';
        submitBtn.style.display = 'inline-block';
        nextBtn.style.display = 'none';
        quizSection.style.display = 'block';

        if (quizStep.options && quizStep.options.length > 0) {
            quizStep.options.forEach((option, index) => {
                const optionEl = document.createElement('div');
                optionEl.className = 'quiz-option';
                optionEl.dataset.optionIndex = index;
                optionEl.innerHTML = `
                    <span class="option-letter">${String.fromCharCode(65 + index)}</span>
                    <span class="option-text">${option}</span>
                `;

                optionEl.addEventListener('click', () => this.selectQuizOption(index));
                quizOptions.appendChild(optionEl);
            });
        }
    }

    selectQuizOption(index) {
        this.selectedQuizOption = index;

        document.querySelectorAll('.quiz-option').forEach((el, i) => {
            el.classList.remove('selected');
            if (i === index) {
                el.classList.add('selected');
            }
        });
    }

    async submitQuiz() {
        if (!this.currentModule || !this.currentQuiz) return;
        if (this.selectedQuizOption === null) {
            alert('请选择一个答案');
            return;
        }

        const submitBtn = document.getElementById('btn-submit-quiz');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '提交中...';
        }

        try {
            const res = await fetch(`${this.apiBase}/teaching/modules/${this.currentModule.id}/quiz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    step_index: this.currentStepIndex,
                    answer: this.selectedQuizOption
                })
            });

            const data = await res.json();

            this.showQuizResult(data);

            if (data.progress !== undefined && this.currentModule) {
                this.currentModule.progress = data.progress;
                this.updateModuleHeader();
            }

        } catch (e) {
            console.error('提交测验失败:', e);
            alert('提交失败，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.display = 'none';
            }
        }
    }

    showQuizResult(data) {
        const quizResult = document.getElementById('quiz-result');
        const nextBtn = document.getElementById('btn-next-after-quiz');
        const quizOptions = document.getElementById('quiz-options');

        if (!quizResult || !quizOptions) return;

        const isCorrect = data.correct;
        const correctAnswer = data.correct_answer;
        const explanation = data.explanation;

        document.querySelectorAll('.quiz-option').forEach((el, i) => {
            if (i === correctAnswer) {
                el.classList.add('correct');
            } else if (i === this.selectedQuizOption && !isCorrect) {
                el.classList.add('wrong');
            }
            el.style.pointerEvents = 'none';
        });

        quizResult.style.display = 'block';
        quizResult.className = `quiz-result ${isCorrect ? 'correct' : 'wrong'}`;

        let resultHtml = '';
        if (isCorrect) {
            resultHtml += `<div class="result-title">✅ 回答正确！</div>`;
        } else {
            resultHtml += `<div class="result-title">❌ 回答错误</div>`;
            resultHtml += `<div class="result-correct">正确答案: ${String.fromCharCode(65 + correctAnswer)}</div>`;
        }

        if (explanation) {
            resultHtml += `<div class="result-explanation">${explanation}</div>`;
        }

        quizResult.innerHTML = resultHtml;
        nextBtn.style.display = 'inline-block';
    }

    continueAfterQuiz() {
        this.nextStep();
    }

    showModuleComplete() {
        const contentEl = document.getElementById('step-content');
        const quizSection = document.getElementById('quiz-section');
        if (!contentEl) return;

        if (quizSection) quizSection.style.display = 'none';

        contentEl.innerHTML = `
            <div class="module-complete">
                <div class="complete-icon">🎉</div>
                <h3>恭喜完成本模块学习！</h3>
                <p style="margin-top: 15px; color: var(--text-secondary);">
                    你已完成 <strong>${this.currentModule.name || '该模块'}</strong> 的全部学习内容
                </p>
                <p style="margin-top: 10px; color: var(--success);">
                    学习进度: ${this.currentModule.progress || 100}%
                </p>
                <div style="margin-top: 20px;">
                    <button class="cyber-btn small primary" onclick="teaching.loadModules()">返回模块列表</button>
                </div>
            </div>
        `;
    }

    showStepContentError(message) {
        const contentEl = document.getElementById('step-content');
        if (contentEl) {
            contentEl.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('btn-prev-step');
        const nextBtn = document.getElementById('btn-next-step');
        const indicator = document.getElementById('step-indicator');

        if (!this.currentModule) {
            if (prevBtn) prevBtn.disabled = true;
            if (nextBtn) nextBtn.disabled = true;
            if (indicator) indicator.textContent = '-- / --';
            return;
        }

        const steps = this.currentModule.steps || [];
        const totalSteps = steps.length;
        const current = this.currentStepIndex + 1;

        if (prevBtn) prevBtn.disabled = this.currentStepIndex === 0;
        if (nextBtn) nextBtn.disabled = this.currentStepIndex >= totalSteps - 1;
        if (indicator) indicator.textContent = `${Math.min(current, totalSteps)} / ${totalSteps}`;
    }

    prevStep() {
        if (!this.currentModule || this.currentStepIndex === 0) return;

        this.currentStepIndex--;
        this.selectedQuizOption = null;
        this.renderCurrentStep();
        this.updateNavigationButtons();
        this.saveProgress();
    }

    nextStep() {
        if (!this.currentModule) return;

        const steps = this.currentModule.steps || [];
        if (this.currentStepIndex >= steps.length - 1) return;

        this.currentStepIndex++;
        this.selectedQuizOption = null;
        this.renderCurrentStep();
        this.updateNavigationButtons();
        this.saveProgress();
    }

    async saveProgress() {
        if (!this.currentModule) return;

        const steps = this.currentModule.steps || [];
        const totalSteps = steps.length;
        const progress = Math.round(((this.currentStepIndex + 1) / Math.max(totalSteps, 1)) * 100);

        if (progress > (this.currentModule.progress || 0)) {
            this.currentModule.progress = progress;
            this.updateModuleHeader();
        }

        try {
            await fetch(`${this.apiBase}/teaching/modules/${this.currentModule.id}/progress`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    step_index: this.currentStepIndex,
                    progress: progress
                })
            });
        } catch (e) {
            console.error('保存进度失败:', e);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.teaching = new TeachingMode('/api');
});

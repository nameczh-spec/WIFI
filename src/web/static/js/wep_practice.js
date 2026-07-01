/**
 * WiFi可视化安全学习工具 v2 - WEP破解练习脚本
 * 仅供学习研究使用
 */

class WEPPractice {
    constructor(apiBase) {
        this.apiBase = apiBase || '/api';
        this.lessons = [];
        this.currentLessonIndex = 0;
        this.isStarted = false;
        this.isCapturing = false;
        this.ivChart = null;
        this.autoCaptureTimer = null;

        this.init();
    }

    init() {
        this.bindEvents();
        this.initChart();
        this.loadLessons();
        this.initTabSwitching();
    }

    initTabSwitching() {
        document.querySelectorAll('.practice-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                if (tab === 'wep') {
                    setTimeout(() => {
                        if (!this.ivChart) {
                            this.initChart();
                        } else {
                            this.ivChart.resize();
                        }
                    }, 100);
                }
            });
        });
    }

    bindEvents() {
        document.getElementById('btn-wep-start')?.addEventListener('click', () => this.startPractice());
        document.getElementById('btn-wep-capture')?.addEventListener('click', () => this.captureIVs(1000));
        document.getElementById('btn-wep-capture-fast')?.addEventListener('click', () => this.captureIVs(10000));
        document.getElementById('btn-wep-crack')?.addEventListener('click', () => this.attemptCrack());
        document.getElementById('btn-wep-reset')?.addEventListener('click', () => this.resetPractice());

        document.getElementById('btn-wep-lesson-prev')?.addEventListener('click', () => this.prevLesson());
        document.getElementById('btn-wep-lesson-next')?.addEventListener('click', () => this.nextLesson());
    }

    initChart() {
        const chartDom = document.getElementById('wep-iv-chart');
        if (!chartDom || typeof echarts === 'undefined') return;

        this.ivChart = echarts.init(chartDom);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(0, 20, 40, 0.9)',
                borderColor: '#00fff5',
                textStyle: { color: '#fff' }
            },
            legend: {
                data: ['总IV数', '弱IV数'],
                textStyle: { color: '#a0aec0' },
                top: 0
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: [],
                axisLine: { lineStyle: { color: '#2d3748' } },
                axisLabel: { color: '#718096' }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#2d3748' } },
                axisLabel: { color: '#718096' },
                splitLine: { lineStyle: { color: '#1a202c' } }
            },
            series: [
                {
                    name: '总IV数',
                    type: 'line',
                    smooth: true,
                    data: [],
                    lineStyle: { color: '#00fff5', width: 2 },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(0, 255, 245, 0.3)' },
                                { offset: 1, color: 'rgba(0, 255, 245, 0)' }
                            ]
                        }
                    },
                    itemStyle: { color: '#00fff5' }
                },
                {
                    name: '弱IV数',
                    type: 'line',
                    smooth: true,
                    data: [],
                    lineStyle: { color: '#ff6b6b', width: 2 },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(255, 107, 107, 0.3)' },
                                { offset: 1, color: 'rgba(255, 107, 107, 0)' }
                            ]
                        }
                    },
                    itemStyle: { color: '#ff6b6b' }
                }
            ]
        };

        this.ivChart.setOption(option);
    }

    updateChart(ivHistory, weakIvHistory) {
        if (!this.ivChart) return;

        const labels = ivHistory.map((_, i) => i);
        
        this.ivChart.setOption({
            xAxis: { data: labels },
            series: [
                { data: ivHistory },
                { data: weakIvHistory }
            ]
        });
    }

    async loadLessons() {
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/lessons`);
            const data = await res.json();

            if (data.lessons) {
                this.lessons = data.lessons;
                this.renderLessonList();
                if (this.lessons.length > 0) {
                    this.loadLesson(this.lessons[0].id);
                }
            }
        } catch (e) {
            console.error('加载WEP课程列表失败:', e);
            this.showLessonListError('加载失败，请稍后重试');
        }
    }

    renderLessonList() {
        const container = document.getElementById('wep-lesson-list');
        if (!container) return;

        if (this.lessons.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无课程</div>';
            return;
        }

        container.innerHTML = '';
        this.lessons.forEach((lesson, index) => {
            const item = document.createElement('div');
            item.className = 'wep-lesson-item';
            item.dataset.lessonId = lesson.id;

            item.innerHTML = `
                <div class="lesson-item-header">
                    <span class="lesson-item-title">${lesson.title}</span>
                    <span class="lesson-step-badge">${index + 1}</span>
                </div>
                <div class="lesson-item-desc">${lesson.description || ''}</div>
            `;

            item.addEventListener('click', () => this.loadLesson(lesson.id));
            container.appendChild(item);
        });
    }

    showLessonListError(message) {
        const container = document.getElementById('wep-lesson-list');
        if (container) {
            container.innerHTML = `<div class="empty-state error">${message}</div>`;
        }
    }

    async loadLesson(lessonId) {
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/lesson?lesson_id=${encodeURIComponent(lessonId)}`);
            const data = await res.json();

            if (data.lesson) {
                this.currentLessonIndex = data.current_index || 0;
                this.highlightActiveLesson(lessonId);
                this.showLessonDetail(data.lesson);
                this.updateLessonIndicator();
            }
        } catch (e) {
            console.error('加载课程详情失败:', e);
        }
    }

    highlightActiveLesson(lessonId) {
        document.querySelectorAll('.wep-lesson-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.lessonId === lessonId) {
                item.classList.add('active');
            }
        });
    }

    showLessonDetail(lesson) {
        const contentPanel = document.getElementById('wep-lesson-content');
        const keyPointsSection = document.getElementById('wep-key-points');
        const keyPointsList = document.getElementById('wep-key-points-list');

        if (contentPanel) {
            contentPanel.innerHTML = `
                <div class="detail-header">
                    <h4>${lesson.title}</h4>
                </div>
                <div class="detail-content">
                    ${lesson.content || ''}
                </div>
                <div class="detail-warning">
                    ⚠ ${lesson.warning || '仅供学习研究使用'}
                </div>
            `;
        }

        if (keyPointsSection && keyPointsList && lesson.key_points && lesson.key_points.length > 0) {
            keyPointsSection.style.display = 'block';
            keyPointsList.innerHTML = lesson.key_points.map(p => `<li>${p}</li>`).join('');
        } else if (keyPointsSection) {
            keyPointsSection.style.display = 'none';
        }
    }

    updateLessonIndicator() {
        const indicator = document.getElementById('wep-lesson-indicator');
        if (indicator) {
            indicator.textContent = `${this.currentLessonIndex + 1} / ${this.lessons.length}`;
        }

        const prevBtn = document.getElementById('btn-wep-lesson-prev');
        const nextBtn = document.getElementById('btn-wep-lesson-next');
        if (prevBtn) prevBtn.disabled = this.currentLessonIndex <= 0;
        if (nextBtn) nextBtn.disabled = this.currentLessonIndex >= this.lessons.length - 1;
    }

    async prevLesson() {
        if (this.currentLessonIndex <= 0) return;
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/lesson/prev`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if (data.lesson) {
                this.currentLessonIndex = data.current_index;
                this.highlightActiveLesson(data.lesson.id);
                this.showLessonDetail(data.lesson);
                this.updateLessonIndicator();
            }
        } catch (e) {
            console.error('上一课失败:', e);
        }
    }

    async nextLesson() {
        if (this.currentLessonIndex >= this.lessons.length - 1) return;
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/lesson/next`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if (data.lesson) {
                this.currentLessonIndex = data.current_index;
                this.highlightActiveLesson(data.lesson.id);
                this.showLessonDetail(data.lesson);
                this.updateLessonIndicator();
            }
        } catch (e) {
            console.error('下一课失败:', e);
        }
    }

    async startPractice() {
        if (this.isStarted) return;

        const wepKeyInput = document.getElementById('wep-key-input');
        const wepKey = wepKeyInput ? wepKeyInput.value.trim() : 'abc123';

        if (!wepKey || (wepKey.length !== 5 && wepKey.length !== 13)) {
            alert('WEP密钥长度应为5个字符（64位）或13个字符（128位）');
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/wep-practice/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wep_key: wepKey, ssid: 'WEP-Learning-Net' })
            });
            const data = await res.json();

            if (data.success) {
                this.isStarted = true;
                this.updateNetworkInfo(data.network);
                this.updateKeyBytesDisplay(wepKey.length);
                this.enableControls();
                document.getElementById('btn-wep-start').disabled = true;
                this.refreshStatus();
            }
        } catch (e) {
            console.error('启动WEP练习失败:', e);
        }
    }

    updateNetworkInfo(network) {
        const infoPanel = document.getElementById('wep-network-info');
        if (!infoPanel) return;

        infoPanel.style.display = 'block';
        document.getElementById('wep-ssid').textContent = network.ssid || '--';
        document.getElementById('wep-bssid').textContent = network.bssid || '--';
    }

    updateKeyBytesDisplay(keyLength) {
        const keyBytesEl = document.getElementById('wep-key-bytes');
        if (!keyBytesEl) return;

        keyBytesEl.innerHTML = '';
        for (let i = 0; i < keyLength; i++) {
            const byteSpan = document.createElement('span');
            byteSpan.className = 'key-byte unknown';
            byteSpan.textContent = '?';
            byteSpan.dataset.index = i;
            keyBytesEl.appendChild(byteSpan);
        }
    }

    enableControls() {
        document.getElementById('btn-wep-capture').disabled = false;
        document.getElementById('btn-wep-capture-fast').disabled = false;
    }

    async captureIVs(count) {
        if (!this.isStarted || this.isCapturing) return;

        this.isCapturing = true;
        const captureBtn = document.getElementById('btn-wep-capture');
        const fastBtn = document.getElementById('btn-wep-capture-fast');
        const crackBtn = document.getElementById('btn-wep-crack');

        if (captureBtn) captureBtn.disabled = true;
        if (fastBtn) fastBtn.disabled = true;

        try {
            const res = await fetch(`${this.apiBase}/wep-practice/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count: count })
            });
            const data = await res.json();

            if (data.success) {
                await this.animateNumber('wep-total-ivs', data.total_ivs);
                await this.animateNumber('wep-weak-ivs', data.total_weak_ivs);
                this.updateProgressBar('wep-iv-progress-bar', data.progress_percent);
                this.updateIvCountBadge(data.total_ivs);
                this.refreshStatus();

                if (data.can_crack && crackBtn) {
                    crackBtn.disabled = false;
                }
            } else {
                console.error('捕获IV失败:', data.error);
            }
        } catch (e) {
            console.error('捕获IV失败:', e);
        } finally {
            this.isCapturing = false;
            if (captureBtn) captureBtn.disabled = false;
            if (fastBtn) fastBtn.disabled = false;
        }
    }

    async animateNumber(elementId, targetValue) {
        const el = document.getElementById(elementId);
        if (!el) return;

        const startValue = parseInt(el.textContent.replace(/,/g, '')) || 0;
        const duration = 500;
        const startTime = performance.now();

        const formatNumber = (num) => {
            return num.toLocaleString();
        };

        return new Promise(resolve => {
            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeProgress = 1 - Math.pow(1 - progress, 3);
                const currentValue = Math.floor(startValue + (targetValue - startValue) * easeProgress);
                el.textContent = formatNumber(currentValue);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    el.textContent = formatNumber(targetValue);
                    resolve();
                }
            };
            requestAnimationFrame(animate);
        });
    }

    updateProgressBar(barId, percent) {
        const bar = document.getElementById(barId);
        if (bar) {
            bar.style.width = `${Math.min(100, percent)}%`;
        }
    }

    updateIvCountBadge(total) {
        const badge = document.getElementById('wep-iv-count-badge');
        if (badge) {
            badge.textContent = `${total.toLocaleString()} / 50,000`;
        }
    }

    async refreshStatus() {
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/status`);
            const data = await res.json();

            if (data.success && data.status) {
                const status = data.status;
                
                if (status.iv_history && status.iv_history.length > 0) {
                    this.updateChart(status.iv_history, status.weak_iv_history);
                }

                if (status.cracked_key_bytes && status.cracked_key_bytes.length > 0) {
                    this.updateCrackedKeyBytes(status.cracked_key_bytes);
                }

                const crackAttemptsEl = document.getElementById('wep-crack-attempts');
                if (crackAttemptsEl) {
                    crackAttemptsEl.textContent = status.crack_attempts || 0;
                }
            }
        } catch (e) {
            console.error('刷新状态失败:', e);
        }
    }

    updateCrackedKeyBytes(crackedBytes) {
        const keyBytesEl = document.getElementById('wep-key-bytes');
        if (!keyBytesEl) return;

        const byteSpans = keyBytesEl.querySelectorAll('.key-byte');
        byteSpans.forEach((span, index) => {
            const byte = crackedBytes[index];
            if (byte !== null && byte !== undefined) {
                span.textContent = byte;
                span.classList.remove('unknown');
                span.classList.add('cracked');
            } else {
                span.textContent = '?';
                span.classList.remove('cracked');
                span.classList.add('unknown');
            }
        });
    }

    async attemptCrack() {
        if (!this.isStarted) return;

        const crackBtn = document.getElementById('btn-wep-crack');
        if (crackBtn) {
            crackBtn.disabled = true;
            crackBtn.textContent = '破解中...';
        }

        try {
            const res = await fetch(`${this.apiBase}/wep-practice/crack`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();

            if (data.success) {
                this.renderCrackSteps(data.crack_steps || []);
                this.updateCrackStatus(data);

                if (data.cracked) {
                    this.showCrackResult(data);
                    this.updateProgressBar('wep-crack-progress-bar', 100);
                } else {
                    this.updateProgressBar('wep-crack-progress-bar', data.crack_progress_percent || 0);
                    if (data.cracked_key_bytes) {
                        this.updateCrackedKeyBytes(data.cracked_key_bytes);
                    }
                }

                const crackAttemptsEl = document.getElementById('wep-crack-attempts');
                if (crackAttemptsEl) {
                    crackAttemptsEl.textContent = data.crack_attempts || 0;
                }
            } else {
                console.error('破解失败:', data.error);
                if (data.error) {
                    alert(data.error);
                }
            }
        } catch (e) {
            console.error('破解失败:', e);
        } finally {
            if (crackBtn) {
                crackBtn.disabled = false;
                crackBtn.textContent = '尝试破解';
            }
        }
    }

    renderCrackSteps(steps) {
        const container = document.getElementById('wep-crack-steps');
        if (!container) return;

        container.innerHTML = '';
        steps.forEach(step => {
            const stepEl = document.createElement('div');
            stepEl.className = `crack-step ${step.status}`;

            let statusIcon = '';
            if (step.status === 'completed') statusIcon = '✓';
            else if (step.status === 'active') statusIcon = '⟳';
            else statusIcon = '○';

            stepEl.innerHTML = `
                <span class="step-icon">${statusIcon}</span>
                <span class="step-name">步骤 ${step.step}: ${step.name}</span>
                <span class="step-desc">${step.description}</span>
            `;
            container.appendChild(stepEl);
        });
    }

    updateCrackStatus(data) {
        const statusEl = document.getElementById('wep-crack-status');
        if (!statusEl) return;

        statusEl.classList.remove('tag-info', 'tag-warning', 'tag-safe', 'tag-danger');

        if (data.cracked) {
            statusEl.textContent = '破解成功';
            statusEl.classList.add('tag-safe');
        } else if (data.crack_progress_percent > 0) {
            statusEl.textContent = `破解中 ${data.crack_progress_percent}%`;
            statusEl.classList.add('tag-warning');
        } else {
            statusEl.textContent = '未开始';
            statusEl.classList.add('tag-info');
        }
    }

    showCrackResult(data) {
        const resultCard = document.getElementById('wep-result-card');
        if (!resultCard) return;

        resultCard.style.display = 'block';
        document.getElementById('wep-cracked-key').textContent = data.wep_key || '--';
        document.getElementById('wep-ivs-used').textContent = (data.ivs_used || 0).toLocaleString();
        document.getElementById('wep-crack-count').textContent = data.crack_attempts || 0;

        this.updateCrackedKeyBytes(data.wep_key ? data.wep_key.split('') : []);
        
        const crackBtn = document.getElementById('btn-wep-crack');
        if (crackBtn) {
            crackBtn.disabled = true;
            crackBtn.textContent = '已破解';
        }
        
        const captureBtn = document.getElementById('btn-wep-capture');
        const fastBtn = document.getElementById('btn-wep-capture-fast');
        if (captureBtn) captureBtn.disabled = true;
        if (fastBtn) fastBtn.disabled = true;
    }

    async resetPractice() {
        try {
            const res = await fetch(`${this.apiBase}/wep-practice/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();

            if (data.success) {
                this.isStarted = false;
                this.isCapturing = false;

                if (this.autoCaptureTimer) {
                    clearInterval(this.autoCaptureTimer);
                    this.autoCaptureTimer = null;
                }

                document.getElementById('wep-network-info').style.display = 'none';
                document.getElementById('wep-result-card').style.display = 'none';

                document.getElementById('btn-wep-start').disabled = false;
                document.getElementById('btn-wep-capture').disabled = true;
                document.getElementById('btn-wep-capture-fast').disabled = true;
                document.getElementById('btn-wep-crack').disabled = true;
                document.getElementById('btn-wep-crack').textContent = '尝试破解';

                document.getElementById('wep-total-ivs').textContent = '0';
                document.getElementById('wep-weak-ivs').textContent = '0';
                document.getElementById('wep-crack-attempts').textContent = '0';
                document.getElementById('wep-iv-count-badge').textContent = '0 / 50000';

                this.updateProgressBar('wep-iv-progress-bar', 0);
                this.updateProgressBar('wep-crack-progress-bar', 0);

                const keyBytesEl = document.getElementById('wep-key-bytes');
                if (keyBytesEl) {
                    keyBytesEl.innerHTML = `
                        <span class="key-byte unknown">?</span>
                        <span class="key-byte unknown">?</span>
                        <span class="key-byte unknown">?</span>
                        <span class="key-byte unknown">?</span>
                        <span class="key-byte unknown">?</span>
                    `;
                }

                const crackStatus = document.getElementById('wep-crack-status');
                if (crackStatus) {
                    crackStatus.textContent = '未开始';
                    crackStatus.classList.remove('tag-warning', 'tag-safe', 'tag-danger');
                    crackStatus.classList.add('tag-info');
                }

                const crackSteps = document.getElementById('wep-crack-steps');
                if (crackSteps) {
                    crackSteps.innerHTML = '';
                }

                if (this.ivChart) {
                    this.ivChart.setOption({
                        xAxis: { data: [] },
                        series: [
                            { data: [] },
                            { data: [] }
                        ]
                    });
                }

                this.refreshStatus();
            }
        } catch (e) {
            console.error('重置WEP练习失败:', e);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.wepPractice = new WEPPractice('/api');
});

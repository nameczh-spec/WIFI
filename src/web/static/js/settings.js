// WiFi安全学习平台 - 设置页面功能
(function() {
    'use strict';

    // ========== 动态注入CSS样式 ==========
    function injectSettingsStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* 设置页面Tabs样式 */
            .settings-tabs {
                display: flex;
                gap: 8px;
                margin-bottom: 25px;
                flex-wrap: wrap;
                border-bottom: 1px solid rgba(0, 255, 245, 0.2);
                padding-bottom: 0;
            }

            .settings-tab-btn {
                padding: 12px 20px;
                background: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                color: var(--text-secondary);
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: -1px;
            }

            .settings-tab-btn:hover {
                color: var(--accent-cyan);
                background: rgba(0, 255, 245, 0.05);
            }

            .settings-tab-btn.active {
                color: var(--accent-cyan);
                border-bottom-color: var(--accent-cyan);
                background: rgba(0, 255, 245, 0.1);
            }

            .settings-tab-btn .tab-icon {
                font-size: 16px;
            }

            .settings-tab-content {
                min-height: 500px;
            }

            .settings-tab-panel {
                display: none;
                animation: fadeIn 0.3s ease-out;
            }

            .settings-tab-panel.active {
                display: block;
            }

            /* 表单行布局 */
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }

            @media (max-width: 768px) {
                .form-row {
                    grid-template-columns: 1fr;
                }
            }

            /* 开关行布局 */
            .setting-switch-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 0;
                border-bottom: 1px solid rgba(0, 255, 245, 0.1);
            }

            .setting-switch-row:last-of-type {
                border-bottom: none;
            }

            .setting-switch-info h4 {
                color: var(--accent-cyan);
                margin-bottom: 5px;
                font-size: 15px;
            }

            .setting-switch-info p {
                color: var(--text-secondary);
                font-size: 13px;
                margin: 0;
            }

            /* 密码输入行 */
            .password-input-row {
                display: flex;
                gap: 10px;
            }

            .password-input-row .cyber-input {
                flex: 1;
            }

            /* 存储区域标题 */
            .storage-section-title {
                color: var(--accent-magenta);
                font-size: 16px;
                margin-bottom: 15px;
            }

            /* 存储统计 */
            .storage-stats {
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: 30px;
                align-items: center;
                margin-bottom: 20px;
            }

            @media (max-width: 768px) {
                .storage-stats {
                    grid-template-columns: 1fr;
                }
            }

            .storage-chart-container {
                display: flex;
                justify-content: center;
            }

            .storage-chart {
                width: 180px;
                height: 180px;
            }

            .storage-info-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .storage-info-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 12px;
                background: rgba(22, 33, 62, 0.5);
                border-radius: 6px;
            }

            .storage-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                flex-shrink: 0;
            }

            .storage-label {
                flex: 1;
                color: var(--text-secondary);
                font-size: 14px;
            }

            .storage-value {
                color: var(--accent-cyan);
                font-weight: bold;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }

            /* 清理按钮 */
            .cleanup-buttons {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }

            /* 操作按钮组 */
            .action-buttons {
                display: flex;
                gap: 15px;
            }

            /* 测试结果 */
            .test-result {
                padding: 12px 15px;
                border-radius: 6px;
                margin: 15px 0;
                font-size: 14px;
            }

            .test-result.success {
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid rgba(0, 255, 0, 0.4);
                color: var(--success);
            }

            .test-result.error {
                background: rgba(255, 51, 51, 0.1);
                border: 1px solid rgba(255, 51, 51, 0.4);
                color: var(--danger);
            }

            .test-result.info {
                background: rgba(0, 255, 245, 0.1);
                border: 1px solid rgba(0, 255, 245, 0.4);
                color: var(--accent-cyan);
            }

            /* 认证状态卡片 */
            .auth-status-card {
                display: flex;
                align-items: center;
                gap: 20px;
                padding: 20px;
                background: rgba(22, 33, 62, 0.5);
                border: 1px solid rgba(0, 255, 245, 0.2);
                border-radius: 10px;
                margin-bottom: 20px;
            }

            .auth-status-icon {
                font-size: 48px;
                flex-shrink: 0;
            }

            .auth-status-info {
                flex: 1;
            }

            .auth-status-info h4 {
                color: var(--accent-cyan);
                font-size: 18px;
                margin-bottom: 5px;
            }

            .auth-status-info p {
                color: var(--text-secondary);
                font-size: 14px;
                margin: 0;
            }

            .auth-status-badge {
                flex-shrink: 0;
            }

            /* 认证信息框 */
            .auth-info-box {
                background: rgba(0, 255, 245, 0.05);
                border: 1px solid rgba(0, 255, 245, 0.2);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }

            .auth-info-box.warning {
                background: rgba(255, 204, 0, 0.05);
                border-color: rgba(255, 204, 0, 0.3);
            }

            .auth-info-box h4 {
                color: var(--accent-cyan);
                margin-bottom: 10px;
                font-size: 15px;
            }

            .auth-info-box.warning h4 {
                color: var(--warning);
            }

            .auth-info-box p {
                color: #c0c0e0;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 10px;
            }

            .auth-feature-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }

            .auth-feature-list li {
                padding: 5px 0;
                color: #c0c0e0;
                font-size: 13px;
            }

            /* 练习模式列表 */
            .practice-modes-list {
                margin-bottom: 20px;
            }

            .practice-mode-item {
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 15px;
                background: rgba(22, 33, 62, 0.5);
                border: 1px solid rgba(0, 255, 245, 0.2);
                border-radius: 8px;
                margin-bottom: 10px;
                transition: all 0.3s;
            }

            .practice-mode-item:hover {
                border-color: rgba(0, 255, 245, 0.5);
                background: rgba(0, 255, 245, 0.05);
            }

            .practice-mode-item.locked {
                opacity: 0.6;
            }

            .practice-mode-icon {
                font-size: 28px;
                flex-shrink: 0;
            }

            .practice-mode-info {
                flex: 1;
            }

            .practice-mode-info h4 {
                color: var(--accent-cyan);
                margin-bottom: 3px;
                font-size: 15px;
            }

            .practice-mode-info p {
                color: var(--text-secondary);
                font-size: 13px;
                margin: 0;
            }

            .practice-mode-status {
                flex-shrink: 0;
            }

            /* 模态框 */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(10, 10, 26, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                animation: fadeIn 0.2s ease-out;
            }

            .modal-content {
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                animation: slideUp 0.3s ease-out;
            }

            .modal-actions {
                display: flex;
                justify-content: flex-end;
                gap: 15px;
            }

            .modal-error {
                background: rgba(255, 51, 51, 0.1);
                border: 1px solid rgba(255, 51, 51, 0.4);
                color: var(--danger);
                padding: 10px 15px;
                border-radius: 6px;
                font-size: 13px;
                margin-bottom: 15px;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* 路径输入行 */
            .path-input-row {
                display: flex;
                gap: 10px;
            }

            .path-input-row .cyber-input {
                flex: 1;
            }
        `;
        document.head.appendChild(style);
    }

    // ========== 工具函数 ==========
    async function apiRequest(url, method = 'GET', data = null) {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            if (data) {
                options.body = JSON.stringify(data);
            }
            const response = await fetch(url, options);
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            return { success: false, error: error.message };
        }
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function formatBytes(bytes) {
        if (bytes === 0 || !bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // ========== Tab切换功能 ==========
    function initTabs() {
        const tabBtns = document.querySelectorAll('.settings-tab-btn');
        const tabPanels = document.querySelectorAll('.settings-tab-panel');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;

                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanels.forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                const panel = document.getElementById(`settings-tab-${tabId}`);
                if (panel) {
                    panel.classList.add('active');
                }

                if (tabId === 'data') {
                    loadStorageInfo();
                } else if (tabId === 'ai') {
                    loadAIProviders();
                } else if (tabId === 'auth') {
                    loadAuthStatus();
                } else if (tabId === 'advanced') {
                    loadPracticeStatus();
                    loadPracticeModes();
                }
            });
        });
    }

    // ========== 通用设置 ==========
    async function loadGeneralSettings() {
        const result = await apiRequest('/api/settings');
        if (result.success && result.settings) {
            const settings = result.settings;

            if (settings.theme) {
                document.getElementById('setting-theme').value = settings.theme;
            }
            if (settings.language) {
                document.getElementById('setting-language').value = settings.language;
            }
            if (settings.log_level) {
                document.getElementById('setting-log-level').value = settings.log_level;
            }
            if (settings.gentle_mode !== undefined) {
                document.getElementById('setting-gentle-mode').checked = settings.gentle_mode;
            }
            if (settings.auto_cleanup !== undefined) {
                document.getElementById('setting-auto-cleanup').checked = settings.auto_cleanup;
            }
            if (settings.data_path) {
                document.getElementById('setting-data-path').value = settings.data_path;
            }
        }
    }

    async function saveGeneralSettings() {
        const data = {
            theme: document.getElementById('setting-theme').value,
            language: document.getElementById('setting-language').value,
            log_level: document.getElementById('setting-log-level').value,
            gentle_mode: document.getElementById('setting-gentle-mode').checked,
            auto_cleanup: document.getElementById('setting-auto-cleanup').checked
        };

        const result = await apiRequest('/api/settings/general', 'POST', data);
        if (result.success) {
            showNotification('通用设置已保存', 'success');
        } else {
            showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
        }
    }

    // ========== 数据管理 ==========
    let storageChart = null;

    async function loadStorageInfo() {
        const result = await apiRequest('/api/storage/info');
        if (result.success && result.storage) {
            const storage = result.storage;

            document.getElementById('storage-used').textContent = formatBytes(storage.used_size || 0);
            document.getElementById('storage-total').textContent = formatBytes(storage.total_size || 0);
            document.getElementById('storage-temp').textContent = formatBytes(storage.temp_size || 0);
            document.getElementById('storage-free').textContent = formatBytes(storage.free_size || 0);

            renderStorageChart(storage);
        }
    }

    function renderStorageChart(storage) {
        const chartDom = document.getElementById('storage-chart');
        if (!chartDom || !window.echarts) return;

        if (!storageChart) {
            storageChart = echarts.init(chartDom);
        }

        const used = storage.used_size || 0;
        const temp = storage.temp_size || 0;
        const free = storage.free_size || 0;
        const actualUsed = Math.max(0, used - temp);

        const option = {
            series: [{
                type: 'pie',
                radius: ['60%', '80%'],
                avoidLabelOverlap: false,
                label: {
                    show: false
                },
                data: [
                    { value: actualUsed, name: '已使用', itemStyle: { color: '#00fff5' } },
                    { value: temp, name: '临时文件', itemStyle: { color: '#ffcc00' } },
                    { value: free, name: '可用空间', itemStyle: { color: 'rgba(0, 255, 0, 0.3)' } }
                ]
            }]
        };

        storageChart.setOption(option);
    }

    async function saveDataSettings() {
        const data = {
            data_path: document.getElementById('setting-data-path').value,
            auto_cleanup: document.getElementById('setting-auto-cleanup').checked
        };

        const result = await apiRequest('/api/settings/data', 'POST', data);
        if (result.success) {
            showNotification('数据设置已保存', 'success');
            loadStorageInfo();
        } else {
            showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
        }
    }

    async function cleanupTempFiles() {
        if (!confirm('确定要清理所有临时文件吗？')) return;

        const result = await apiRequest('/api/storage/cleanup', 'POST', { type: 'temp' });
        if (result.success) {
            showNotification('临时文件清理成功', 'success');
            loadStorageInfo();
        } else {
            showNotification('清理失败: ' + (result.error || '未知错误'), 'error');
        }
    }

    // ========== AI设置 ==========
    let aiProviders = [];

    async function loadAIProviders() {
        const result = await apiRequest('/api/ai/providers');
        if (result.success && result.providers) {
            aiProviders = result.providers;
            updateModelSelect();
        }

        loadAISettings();
    }

    async function loadAISettings() {
        const result = await apiRequest('/api/settings');
        if (result.success && result.ai_status) {
            const ai = result.ai_status;

            if (ai.provider) {
                document.getElementById('setting-ai-provider').value = ai.provider;
                updateModelSelect();
            }
            if (ai.model) {
                const modelSelect = document.getElementById('setting-ai-model');
                const optionExists = Array.from(modelSelect.options).some(o => o.value === ai.model);
                if (!optionExists) {
                    const opt = document.createElement('option');
                    opt.value = ai.model;
                    opt.textContent = ai.model;
                    modelSelect.appendChild(opt);
                }
                modelSelect.value = ai.model;
            }
            if (ai.api_url) {
                document.getElementById('setting-ai-api-url').value = ai.api_url;
            }
            if (ai.api_key) {
                document.getElementById('setting-ai-api-key').value = ai.api_key;
            }
            if (ai.temperature !== undefined) {
                document.getElementById('setting-ai-temperature').value = ai.temperature;
            }
            if (ai.max_tokens !== undefined) {
                document.getElementById('setting-ai-max-tokens').value = ai.max_tokens;
            }
        }
    }

    function updateModelSelect() {
        const provider = document.getElementById('setting-ai-provider').value;
        const modelSelect = document.getElementById('setting-ai-model');
        const currentValue = modelSelect.value;

        modelSelect.innerHTML = '';

        const providerInfo = aiProviders.find(p => p.id === provider);
        if (providerInfo && providerInfo.models && providerInfo.models.length > 0) {
            providerInfo.models.forEach(model => {
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                modelSelect.appendChild(opt);
            });
        } else {
            const opt = document.createElement('option');
            opt.value = 'custom-model';
            opt.textContent = '自定义模型';
            modelSelect.appendChild(opt);
        }

        if (currentValue) {
            const optionExists = Array.from(modelSelect.options).some(o => o.value === currentValue);
            if (optionExists) {
                modelSelect.value = currentValue;
            }
        }
    }

    async function saveAISettings() {
        const data = {
            provider: document.getElementById('setting-ai-provider').value,
            model: document.getElementById('setting-ai-model').value,
            api_url: document.getElementById('setting-ai-api-url').value,
            api_key: document.getElementById('setting-ai-api-key').value,
            temperature: parseFloat(document.getElementById('setting-ai-temperature').value),
            max_tokens: parseInt(document.getElementById('setting-ai-max-tokens').value)
        };

        const result = await apiRequest('/api/settings/ai', 'POST', data);
        if (result.success) {
            showNotification('AI设置已保存', 'success');
        } else {
            showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
        }
    }

    async function testAIConnection() {
        const resultDiv = document.getElementById('ai-test-result');
        resultDiv.style.display = 'block';
        resultDiv.className = 'test-result info';
        resultDiv.textContent = '正在测试连接...';

        const data = {
            provider: document.getElementById('setting-ai-provider').value,
            model: document.getElementById('setting-ai-model').value,
            api_url: document.getElementById('setting-ai-api-url').value,
            api_key: document.getElementById('setting-ai-api-key').value
        };

        await apiRequest('/api/settings/ai', 'POST', data);

        const result = await apiRequest('/api/settings/ai/test', 'POST');

        if (result.success) {
            resultDiv.className = 'test-result success';
            resultDiv.textContent = '✓ 连接测试成功！';
        } else {
            resultDiv.className = 'test-result error';
            resultDiv.textContent = '✗ 连接失败: ' + (result.error || result.message || '未知错误');
        }
    }

    function toggleAPIKeyVisibility() {
        const input = document.getElementById('setting-ai-api-key');
        const btn = document.getElementById('btn-toggle-api-key');

        if (input.type === 'password') {
            input.type = 'text';
            btn.textContent = '隐藏';
        } else {
            input.type = 'password';
            btn.textContent = '显示';
        }
    }

    // ========== 双密码验证 ==========
    async function loadAuthStatus() {
        const result = await apiRequest('/api/auth/status');
        if (result.success) {
            const isSet = result.is_password_set;

            const icon = document.getElementById('auth-status-icon');
            const title = document.getElementById('auth-status-title');
            const desc = document.getElementById('auth-status-desc');
            const badge = document.getElementById('auth-status-badge');

            if (isSet) {
                icon.textContent = '🔐';
                title.textContent = '已设置';
                desc.textContent = '双密码验证已启用，高级功能受保护';
                badge.className = 'cyber-tag tag-safe';
                badge.textContent = '已启用';
            } else {
                icon.textContent = '🔒';
                title.textContent = '未设置';
                desc.textContent = '请设置双密码以启用高级功能保护';
                badge.className = 'cyber-tag tag-warning';
                badge.textContent = '未设置';
            }
        }
    }

    function openPasswordModal() {
        document.getElementById('password-modal').style.display = 'flex';
        document.getElementById('modal-error').style.display = 'none';

        document.getElementById('modal-password-1').value = '';
        document.getElementById('modal-password-1-confirm').value = '';
        document.getElementById('modal-password-2').value = '';
        document.getElementById('modal-password-2-confirm').value = '';
    }

    function closePasswordModal() {
        document.getElementById('password-modal').style.display = 'none';
    }

    async function confirmPasswordSetup() {
        const pwd1 = document.getElementById('modal-password-1').value;
        const pwd1Confirm = document.getElementById('modal-password-1-confirm').value;
        const pwd2 = document.getElementById('modal-password-2').value;
        const pwd2Confirm = document.getElementById('modal-password-2-confirm').value;

        const errorDiv = document.getElementById('modal-error');

        if (!pwd1 || !pwd2) {
            errorDiv.style.display = 'block';
            errorDiv.textContent = '两个密码都不能为空';
            return;
        }

        if (pwd1 !== pwd1Confirm) {
            errorDiv.style.display = 'block';
            errorDiv.textContent = '第一段密码两次输入不一致';
            return;
        }

        if (pwd2 !== pwd2Confirm) {
            errorDiv.style.display = 'block';
            errorDiv.textContent = '第二段密码两次输入不一致';
            return;
        }

        if (pwd1 === pwd2) {
            errorDiv.style.display = 'block';
            errorDiv.textContent = '两个密码不能相同';
            return;
        }

        const result = await apiRequest('/api/auth/setup-password', 'POST', {
            password1: pwd1,
            password2: pwd2
        });

        if (result.success) {
            showNotification('双密码设置成功', 'success');
            closePasswordModal();
            loadAuthStatus();
        } else {
            errorDiv.style.display = 'block';
            errorDiv.textContent = '设置失败: ' + (result.error || '未知错误');
        }
    }

    // ========== 高级授权 ==========
    async function loadPracticeStatus() {
        const result = await apiRequest('/api/practice/status');
        if (result.success && result.status) {
            const status = result.status;

            const icon = document.getElementById('practice-status-icon');
            const title = document.getElementById('practice-status-title');
            const desc = document.getElementById('practice-status-desc');
            const badge = document.getElementById('practice-status-badge');

            if (status.is_authorized) {
                icon.textContent = '✅';
                title.textContent = '已授权';
                desc.textContent = '您已获得高级练习功能的访问权限';
                badge.className = 'cyber-tag tag-safe';
                badge.textContent = '已授权';
            } else if (status.requires_password) {
                icon.textContent = '🔑';
                title.textContent = '需要验证';
                desc.textContent = '请先完成双密码验证';
                badge.className = 'cyber-tag tag-warning';
                badge.textContent = '需验证';
            } else {
                icon.textContent = '⚠️';
                title.textContent = '未授权';
                desc.textContent = '请先设置双密码并完成验证';
                badge.className = 'cyber-tag tag-danger';
                badge.textContent = '未授权';
            }
        }
    }

    async function loadPracticeModes() {
        const result = await apiRequest('/api/practice/modes');
        const container = document.getElementById('practice-modes-list');

        if (result.success && result.modes && result.modes.length > 0) {
            container.innerHTML = '';

            result.modes.forEach(mode => {
                const item = document.createElement('div');
                item.className = `practice-mode-item ${mode.locked ? 'locked' : ''}`;

                item.innerHTML = `
                    <div class="practice-mode-icon">${mode.icon || '⚡'}</div>
                    <div class="practice-mode-info">
                        <h4>${mode.name || mode.id}</h4>
                        <p>${mode.description || ''}</p>
                    </div>
                    <div class="practice-mode-status">
                        <span class="cyber-tag ${mode.locked ? 'tag-danger' : 'tag-safe'}">
                            ${mode.locked ? '锁定' : '可用'}
                        </span>
                    </div>
                `;

                container.appendChild(item);
            });
        } else {
            container.innerHTML = '<div class="empty-state">暂无可用的练习模式</div>';
        }
    }

    // ========== 事件绑定 ==========
    function bindEvents() {
        document.getElementById('btn-save-general').addEventListener('click', saveGeneralSettings);
        document.getElementById('btn-save-data').addEventListener('click', saveDataSettings);
        document.getElementById('btn-cleanup-temp').addEventListener('click', cleanupTempFiles);
        document.getElementById('btn-refresh-storage').addEventListener('click', loadStorageInfo);
        document.getElementById('btn-save-ai-settings').addEventListener('click', saveAISettings);
        document.getElementById('btn-test-ai-connection').addEventListener('click', testAIConnection);
        document.getElementById('btn-toggle-api-key').addEventListener('click', toggleAPIKeyVisibility);
        document.getElementById('btn-setup-password').addEventListener('click', openPasswordModal);
        document.getElementById('btn-modal-cancel').addEventListener('click', closePasswordModal);
        document.getElementById('btn-modal-confirm').addEventListener('click', confirmPasswordSetup);

        document.getElementById('setting-ai-provider').addEventListener('change', updateModelSelect);

        document.getElementById('password-modal').addEventListener('click', (e) => {
            if (e.target.id === 'password-modal') {
                closePasswordModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closePasswordModal();
            }
        });
    }

    // ========== 初始化 ==========
    function init() {
        injectSettingsStyles();
        initTabs();
        bindEvents();
        loadGeneralSettings();

        window.addEventListener('resize', () => {
            if (storageChart) {
                storageChart.resize();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

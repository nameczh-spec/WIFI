css_content = """

/* === 教学模式样式 === */

.teaching-security-warning {
    background: rgba(255, 51, 51, 0.15);
    border: 1px solid rgba(255, 51, 51, 0.5);
    color: #ff6666;
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
    font-size: 14px;
    line-height: 1.6;
}

.teaching-layout {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 20px;
    min-height: 600px;
}

.teaching-sidebar {
    display: flex;
    flex-direction: column;
}

.teaching-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.teaching-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
    flex-wrap: wrap;
    gap: 10px;
}

.teaching-module-title {
    display: flex;
    align-items: center;
    gap: 12px;
}

.teaching-module-title h3 {
    margin: 0;
}

.teaching-progress-info {
    color: var(--text-secondary);
    font-size: 14px;
}

.teaching-progress-info span {
    color: var(--accent-cyan);
    font-weight: bold;
}

.module-list {
    max-height: 500px;
    overflow-y: auto;
    margin-top: 10px;
}

.module-list-item {
    background: rgba(22, 33, 62, 0.5);
    border: 1px solid rgba(0, 255, 245, 0.2);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.3s;
}

.module-list-item:hover {
    border-color: rgba(0, 255, 245, 0.5);
    background: rgba(0, 255, 245, 0.08);
}

.module-list-item.active {
    border-color: var(--accent-cyan);
    background: rgba(0, 255, 245, 0.12);
    box-shadow: 0 0 15px rgba(0, 255, 245, 0.2);
}

.module-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.module-item-title {
    color: var(--accent-cyan);
    font-weight: bold;
    font-size: 14px;
}

.module-item-desc {
    color: var(--text-secondary);
    font-size: 12px;
    margin-bottom: 10px;
    line-height: 1.5;
}

.module-item-progress {
    display: flex;
    align-items: center;
    gap: 10px;
}

.module-item-progress .cyber-progress.small {
    flex: 1;
    height: 6px;
}

.module-item-progress .progress-text {
    font-size: 12px;
    color: var(--accent-cyan);
    min-width: 40px;
    text-align: right;
}

.empty-state {
    text-align: center;
    color: var(--text-secondary);
    padding: 40px 20px;
    font-size: 14px;
}

.empty-state.error {
    color: var(--danger);
}

.step-content {
    min-height: 300px;
    max-height: 500px;
    overflow-y: auto;
}

.step-title {
    font-size: 20px;
    font-weight: bold;
    color: var(--accent-magenta);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 0, 255, 0.3);
}

.step-body {
    color: #c0c0e0;
    line-height: 1.8;
    font-size: 15px;
}

.step-body p {
    margin-bottom: 12px;
}

.step-body strong {
    color: var(--accent-cyan);
}

.step-section {
    margin-top: 20px;
}

.section-title {
    color: var(--accent-cyan);
    font-size: 16px;
    margin-bottom: 12px;
}

.key-points-list {
    list-style: none;
    padding: 0;
}

.key-points-list li {
    position: relative;
    padding: 8px 0 8px 25px;
    color: #c0c0e0;
    border-bottom: 1px dashed rgba(0, 255, 245, 0.1);
}

.key-points-list li::before {
    content: '✦';
    position: absolute;
    left: 0;
    color: var(--accent-cyan);
}

.code-block {
    background: rgba(10, 10, 30, 0.9);
    border: 1px solid rgba(0, 255, 245, 0.3);
    border-radius: 8px;
    padding: 15px;
    overflow-x: auto;
}

.code-block pre {
    margin: 0;
}

.code-block code {
    color: #00ff00;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
}

.warning-box {
    background: rgba(255, 204, 0, 0.1);
    border: 1px solid rgba(255, 204, 0, 0.4);
    border-radius: 8px;
    padding: 15px;
    color: #ffcc00;
    font-size: 14px;
    line-height: 1.6;
}

.warning-box strong {
    color: #ffff99;
}

.step-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid rgba(0, 255, 245, 0.2);
}

.step-indicator {
    color: var(--accent-cyan);
    font-size: 14px;
    font-family: 'Consolas', monospace;
}

/* 测验样式 */

.quiz-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(0, 255, 245, 0.2);
}

.quiz-section h4 {
    color: var(--accent-magenta);
    margin-bottom: 15px;
    font-size: 18px;
}

.quiz-question {
    color: #c0c0e0;
    font-size: 15px;
    line-height: 1.6;
    margin-bottom: 20px;
    padding: 15px;
    background: rgba(22, 33, 62, 0.5);
    border-radius: 8px;
    border-left: 3px solid var(--accent-cyan);
}

.quiz-options {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

.quiz-option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 15px;
    background: rgba(22, 33, 62, 0.5);
    border: 1px solid rgba(0, 255, 245, 0.2);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.quiz-option:hover {
    border-color: rgba(0, 255, 245, 0.5);
    background: rgba(0, 255, 245, 0.08);
}

.quiz-option.selected {
    border-color: var(--accent-cyan);
    background: rgba(0, 255, 245, 0.15);
    box-shadow: 0 0 10px rgba(0, 255, 245, 0.2);
}

.quiz-option.correct {
    border-color: var(--success);
    background: rgba(0, 255, 0, 0.15);
}

.quiz-option.wrong {
    border-color: var(--danger);
    background: rgba(255, 51, 51, 0.15);
}

.option-letter {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 255, 245, 0.2);
    border-radius: 50%;
    color: var(--accent-cyan);
    font-weight: bold;
    font-size: 13px;
    flex-shrink: 0;
}

.quiz-option.selected .option-letter {
    background: var(--accent-cyan);
    color: var(--bg-dark);
}

.quiz-option.correct .option-letter {
    background: var(--success);
    color: var(--bg-dark);
}

.quiz-option.wrong .option-letter {
    background: var(--danger);
    color: white;
}

.option-text {
    color: #c0c0e0;
    font-size: 14px;
    line-height: 1.5;
}

.quiz-result {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.quiz-result.correct {
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.4);
}

.quiz-result.wrong {
    background: rgba(255, 51, 51, 0.1);
    border: 1px solid rgba(255, 51, 51, 0.4);
}

.result-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
}

.quiz-result.correct .result-title {
    color: var(--success);
}

.quiz-result.wrong .result-title {
    color: var(--danger);
}

.result-correct {
    color: var(--warning);
    margin-bottom: 10px;
    font-size: 14px;
}

.result-explanation {
    color: #c0c0e0;
    font-size: 14px;
    line-height: 1.6;
}

.module-complete {
    text-align: center;
    padding: 60px 20px;
}

.complete-icon {
    font-size: 64px;
    margin-bottom: 20px;
}

.module-complete h3 {
    color: var(--accent-cyan);
    font-size: 24px;
}

@media (max-width: 992px) {
    .teaching-layout {
        grid-template-columns: 1fr;
    }

    .module-list {
        max-height: 300px;
    }
}
"""

css_file = r"h:\IT\wifi密码温和解码\wifi密码温和解码_v2\src\web\static\css\style.css"

with open(css_file, 'a', encoding='utf-8') as f:
    f.write(css_content)

print("CSS样式已成功追加到文件末尾")

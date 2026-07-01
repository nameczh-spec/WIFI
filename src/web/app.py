"""
Flask Web应用 - WiFi可视化安全学习工具 v2
提供Web界面和REST API
"""

from flask import Flask, request, jsonify, render_template
from src.core.config import ConfigManager
from src.core.safety import SafetyManager
from src.core.logger import get_logger
from src.modules.wifi_scanner import get_wifi_scanner
from src.modules.security_eval import NetworkSecurityEvaluator
from src.ai.api_client import AIClient
from src.ai.prompts import PromptManager
from src.modules.visualization import (
    WiFiDataVisualizer,
    HandshakeSimulator,
    NetworkTrafficSimulator,
    WiFiNetworkData
)
from src.modules.teaching import get_teaching_system
from src.modules.handshake_sim import get_handshake_simulator
from src.modules.attack_defense import get_attack_defense_simulator
from src.modules.wep_practice import get_wep_practice_simulator
from src.core.data_manager import get_data_manager
from src.core.advanced_practice import get_advanced_practice_manager

logger = get_logger("web_app")


def create_app() -> Flask:
    """创建Flask应用"""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    config = ConfigManager()
    safety = SafetyManager(gentle_mode=config.get("gentle_mode", True))

    app.config['CONFIG'] = config
    app.config['SAFETY'] = safety
    app.config['AI_CLIENT'] = AIClient()
    app.config['PROMPT_MANAGER'] = PromptManager()
    app.config['WIFI_SCANNER'] = get_wifi_scanner(safety)
    app.config['SECURITY_EVAL'] = NetworkSecurityEvaluator(safety)
    app.config['VISUALIZER'] = WiFiDataVisualizer()
    app.config['HANDSHAKE_SIM'] = HandshakeSimulator()
    app.config['TRAFFIC_SIM'] = NetworkTrafficSimulator()
    app.config['DATA_MANAGER'] = get_data_manager(
        data_path=config.get("data_path", ""),
        auto_cleanup=config.get("auto_cleanup", True)
    )

    _register_routes(app)

    logger.info("Flask应用创建成功")
    return app


def _register_routes(app: Flask):
    """注册所有路由"""

    # ============== 首页 ==============
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"加载首页失败: {e}")
            return jsonify({"error": str(e)}), 500

    # ============== WiFi扫描 ==============
    @app.route('/api/wifi/scan', methods=['GET'])
    def wifi_scan():
        try:
            scanner = app.config['WIFI_SCANNER']
            networks = scanner.scan()
            result = []
            for net in networks:
                result.append({
                    "ssid": net.ssid,
                    "bssid": net.bssid,
                    "signal_strength": net.signal_strength,
                    "encryption": net.encryption,
                    "channel": net.channel,
                    "frequency": net.frequency
                })
                net_data = WiFiNetworkData(
                    ssid=net.ssid,
                    bssid=net.bssid,
                    signal_strength=net.signal_strength,
                    channel=net.channel,
                    encryption=net.encryption
                )
                app.config['VISUALIZER'].add_network(net_data)
            return jsonify({"success": True, "networks": result, "count": len(result)})
        except Exception as e:
            logger.error(f"WiFi扫描失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wifi/networks', methods=['GET'])
    def wifi_networks():
        try:
            visualizer = app.config['VISUALIZER']
            networks = []
            for net in visualizer.networks:
                networks.append({
                    "ssid": net.ssid,
                    "bssid": net.bssid,
                    "signal_strength": net.signal_strength,
                    "channel": net.channel,
                    "encryption": net.encryption
                })
            return jsonify({"success": True, "networks": networks, "count": len(networks)})
        except Exception as e:
            logger.error(f"获取网络列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wifi/network/<bssid>', methods=['GET'])
    def wifi_network_detail(bssid):
        try:
            visualizer = app.config['VISUALIZER']
            for net in visualizer.networks:
                if net.bssid == bssid:
                    return jsonify({
                        "success": True,
                        "network": {
                            "ssid": net.ssid,
                            "bssid": net.bssid,
                            "signal_strength": net.signal_strength,
                            "channel": net.channel,
                            "encryption": net.encryption,
                            "vendor": net.vendor,
                            "is_hidden": net.is_hidden
                        }
                    })
            return jsonify({"success": False, "error": "网络不存在"}), 404
        except Exception as e:
            logger.error(f"获取网络详情失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 安全评估 ==============
    @app.route('/api/security/eval', methods=['GET'])
    def security_eval():
        try:
            safety = app.config['SAFETY']
            status = safety.get_status()
            return jsonify({"success": True, "status": status})
        except Exception as e:
            logger.error(f"获取安全状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/security/analyze', methods=['POST'])
    def security_analyze():
        try:
            data = request.get_json() or {}
            ssid = data.get('ssid', '')
            password = data.get('password', '')
            encryption = data.get('encryption', 'WPA2')

            evaluator = app.config['SECURITY_EVAL']
            report = evaluator.evaluate_network(ssid, password, encryption)

            return jsonify({
                "success": True,
                "report": {
                    "overall_score": report.overall_score,
                    "overall_level": report.overall_level,
                    "password_strength": {
                        "total_score": report.password_strength.total_score,
                        "level": report.password_strength.level,
                        "length_score": report.password_strength.length_score,
                        "complexity_score": report.password_strength.complexity_score,
                        "weak_pattern_score": report.password_strength.weak_pattern_score,
                        "suggestions": report.password_strength.suggestions
                    },
                    "encryption_rating": {
                        "encryption_type": report.encryption_rating.encryption_type,
                        "score": report.encryption_rating.score,
                        "level": report.encryption_rating.level,
                        "advice": report.encryption_rating.advice
                    },
                    "risks": report.risks,
                    "suggestions": report.suggestions
                }
            })
        except Exception as e:
            logger.error(f"安全分析失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== AI对话 ==============
    @app.route('/api/ai/chat', methods=['POST'])
    def ai_chat():
        try:
            data = request.get_json() or {}
            message = data.get('message', '')
            scenario = data.get('scenario', 'default')

            ai_client = app.config['AI_CLIENT']
            prompt_manager = app.config['PROMPT_MANAGER']

            if not message:
                return jsonify({"success": False, "error": "消息不能为空"}), 400

            system_prompt = prompt_manager.get_system_prompt(scenario)
            response = ai_client.chat(message, system_prompt=system_prompt)

            if response:
                return jsonify({
                    "success": True,
                    "content": response.content,
                    "model": response.model,
                    "usage": response.usage
                })
            else:
                return jsonify({"success": False, "error": "AI响应失败，请检查API配置"}), 500
        except Exception as e:
            logger.error(f"AI对话失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/clear', methods=['POST'])
    def ai_clear():
        try:
            ai_client = app.config['AI_CLIENT']
            ai_client.clear_history()
            return jsonify({"success": True, "message": "对话历史已清除"})
        except Exception as e:
            logger.error(f"清除AI历史失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/config', methods=['GET'])
    def ai_get_config():
        try:
            ai_client = app.config['AI_CLIENT']
            status = ai_client.get_status()
            return jsonify({"success": True, "config": status})
        except Exception as e:
            logger.error(f"获取AI配置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/config', methods=['POST'])
    def ai_set_config():
        try:
            data = request.get_json() or {}
            ai_client = app.config['AI_CLIENT']

            provider = data.get('provider')
            model = data.get('model')
            api_key = data.get('api_key')
            api_url = data.get('api_url')

            if provider:
                ai_client.set_provider(provider, api_url or '')
            if model:
                ai_client.set_model(model)
            if api_key:
                ai_client.set_api_key(api_key)

            return jsonify({"success": True, "message": "配置已更新"})
        except Exception as e:
            logger.error(f"设置AI配置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 双密码认证 ==============
    @app.route('/api/auth/setup-password', methods=['POST'])
    def auth_setup_password():
        try:
            data = request.get_json() or {}
            password1 = data.get('password1', '')
            password2 = data.get('password2', '')

            if not password1 or not password2:
                return jsonify({"success": False, "error": "两个密码都不能为空"}), 400

            safety = app.config['SAFETY']
            safety.set_dual_password(password1, password2)

            return jsonify({"success": True, "message": "双密码设置成功"})
        except Exception as e:
            logger.error(f"设置双密码失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/auth/verify-password-1', methods=['POST'])
    def auth_verify_password_1():
        try:
            data = request.get_json() or {}
            password = data.get('password', '')

            safety = app.config['SAFETY']
            config = app.config['CONFIG']
            stored_pwd = config.get_secure("dual_password_1", "")

            if password == stored_pwd:
                safety._password_1_verified = True
                return jsonify({"success": True, "message": "第一密码验证成功"})
            else:
                return jsonify({"success": False, "error": "密码错误"}), 401
        except Exception as e:
            logger.error(f"验证第一密码失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/auth/verify-password-2', methods=['POST'])
    def auth_verify_password_2():
        try:
            data = request.get_json() or {}
            password = data.get('password', '')

            safety = app.config['SAFETY']
            config = app.config['CONFIG']
            stored_pwd = config.get_secure("dual_password_2", "")

            if password == stored_pwd:
                safety._password_2_verified = True
                if safety._password_1_verified and safety._password_2_verified:
                    safety._dual_password_verified = True
                return jsonify({"success": True, "message": "第二密码验证成功", "fully_verified": safety._dual_password_verified})
            else:
                return jsonify({"success": False, "error": "密码错误"}), 401
        except Exception as e:
            logger.error(f"验证第二密码失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/auth/reset', methods=['POST'])
    def auth_reset():
        try:
            safety = app.config['SAFETY']
            safety.clear_dual_password_verification()
            safety.clear_authorization()
            return jsonify({"success": True, "message": "认证状态已重置"})
        except Exception as e:
            logger.error(f"重置认证失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/auth/status', methods=['GET'])
    def auth_status():
        try:
            safety = app.config['SAFETY']
            status = safety.get_status()
            is_set = safety.is_dual_password_set()
            return jsonify({
                "success": True,
                "is_password_set": is_set,
                **status
            })
        except Exception as e:
            logger.error(f"获取认证状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 可视化 ==============
    @app.route('/api/visual/signal-strength', methods=['GET'])
    def visual_signal_strength():
        try:
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_signal_strength_chart()
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取信号强度图表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/channel-distribution', methods=['GET'])
    def visual_channel_distribution():
        try:
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_channel_distribution_chart()
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取信道分布图表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/encryption-distribution', methods=['GET'])
    def visual_encryption_distribution():
        try:
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_encryption_distribution_chart()
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取加密方式分布图表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/security-radar', methods=['POST'])
    def visual_security_radar():
        try:
            data = request.get_json() or {}
            score_data = data.get('scores', {})
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_security_radar_chart(score_data)
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取安全雷达图失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/handshake-timeline', methods=['GET'])
    def visual_handshake_timeline():
        try:
            handshake_sim = app.config['HANDSHAKE_SIM']
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_handshake_timeline(handshake_sim.steps)
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取握手时间线图失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/password-strength', methods=['POST'])
    def visual_password_strength():
        try:
            data = request.get_json() or {}
            strength_data = data.get('strength', {})
            visualizer = app.config['VISUALIZER']
            chart = visualizer.get_password_strength_chart(strength_data)
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取密码强度图表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/network-traffic', methods=['GET'])
    def visual_network_traffic():
        try:
            traffic_sim = app.config['TRAFFIC_SIM']
            traffic_sim.generate_sample()
            chart = traffic_sim.get_traffic_chart()
            return jsonify({"success": True, "chart": chart})
        except Exception as e:
            logger.error(f"获取网络流量图表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/traffic-sim/start', methods=['POST'])
    def visual_traffic_sim_start():
        try:
            data = request.get_json() or {}
            attack = data.get('attack', False)
            traffic_sim = app.config['TRAFFIC_SIM']
            if attack:
                traffic_sim.start_attack()
            return jsonify({"success": True, "message": "流量模拟已启动", "attack_mode": attack})
        except Exception as e:
            logger.error(f"启动流量模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/traffic-sim/stop', methods=['POST'])
    def visual_traffic_sim_stop():
        try:
            traffic_sim = app.config['TRAFFIC_SIM']
            traffic_sim.stop_attack()
            return jsonify({"success": True, "message": "攻击模拟已停止"})
        except Exception as e:
            logger.error(f"停止流量模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/handshake/next', methods=['POST'])
    def visual_handshake_next():
        try:
            handshake_sim = app.config['HANDSHAKE_SIM']
            step = handshake_sim.next_step()
            if step:
                return jsonify({
                    "success": True,
                    "step": {
                        "step": step.step,
                        "name": step.name,
                        "description": step.description,
                        "direction": step.direction,
                        "status": step.status
                    },
                    "is_complete": handshake_sim.is_complete()
                })
            return jsonify({"success": False, "error": "已完成所有步骤"})
        except Exception as e:
            logger.error(f"握手可视化下一步失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/handshake/reset', methods=['POST'])
    def visual_handshake_reset():
        try:
            handshake_sim = app.config['HANDSHAKE_SIM']
            handshake_sim.reset()
            return jsonify({"success": True, "message": "握手模拟已重置"})
        except Exception as e:
            logger.error(f"重置握手模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/attack-sim/start', methods=['POST'])
    def visual_attack_sim_start():
        try:
            traffic_sim = app.config['TRAFFIC_SIM']
            traffic_sim.start_attack()
            return jsonify({"success": True, "message": "攻击模拟已启动"})
        except Exception as e:
            logger.error(f"启动攻击模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/visual/attack-sim/stop', methods=['POST'])
    def visual_attack_sim_stop():
        try:
            traffic_sim = app.config['TRAFFIC_SIM']
            traffic_sim.stop_attack()
            return jsonify({"success": True, "message": "攻击模拟已停止"})
        except Exception as e:
            logger.error(f"停止攻击模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 教学系统 ==============
    @app.route('/api/teaching/modules', methods=['GET'])
    def teaching_modules():
        try:
            teaching = get_teaching_system()
            modules = []
            for m in teaching.get_all_modules():
                modules.append({
                    "id": m.module_id,
                    "category": m.category.value,
                    "title": m.title,
                    "description": m.description,
                    "difficulty": m.difficulty.value,
                    "estimated_time": m.estimated_time,
                    "is_practical": m.is_practical,
                    "steps_count": len(m.steps),
                    "quiz_count": len(m.quiz),
                    "progress": teaching.get_progress(m.module_id)
                })
            return jsonify({"success": True, "modules": modules})
        except Exception as e:
            logger.error(f"获取教学模块列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/teaching/modules/<module_id>', methods=['GET'])
    def teaching_module_detail(module_id):
        try:
            teaching = get_teaching_system()
            module = teaching.get_module(module_id)
            if not module:
                return jsonify({"success": False, "error": "模块不存在"}), 404

            progress = teaching.get_progress(module_id)
            steps = []
            for step in module.steps:
                steps.append({
                    "step_id": step.step_id,
                    "title": step.title,
                    "content": step.content,
                    "code_example": step.code_example,
                    "key_points": step.key_points,
                    "warning": step.warning
                })

            return jsonify({
                "success": True,
                "module": {
                    "id": module.module_id,
                    "category": module.category.value,
                    "title": module.title,
                    "description": module.description,
                    "difficulty": module.difficulty.value,
                    "estimated_time": module.estimated_time,
                    "is_practical": module.is_practical,
                    "prerequisites": module.prerequisites,
                    "steps": steps,
                    "quiz": module.quiz,
                    "progress": progress
                }
            })
        except Exception as e:
            logger.error(f"获取教学模块详情失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/teaching/modules/<module_id>/progress', methods=['POST'])
    def teaching_update_progress(module_id):
        try:
            data = request.get_json() or {}
            step_index = data.get('step', 0)
            teaching = get_teaching_system()
            teaching.set_progress(module_id, step_index)
            return jsonify({"success": True, "progress": step_index})
        except Exception as e:
            logger.error(f"更新学习进度失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/teaching/modules/<module_id>/quiz', methods=['POST'])
    def teaching_quiz(module_id):
        try:
            data = request.get_json() or {}
            answers = data.get('answers', {})
            teaching = get_teaching_system()
            module = teaching.get_module(module_id)

            if not module:
                return jsonify({"success": False, "error": "模块不存在"}), 404

            correct_count = 0
            results = []
            for i, q in enumerate(module.quiz):
                user_answer = answers.get(str(i))
                is_correct = user_answer == q.get('correct')
                if is_correct:
                    correct_count += 1
                results.append({
                    "question_index": i,
                    "correct": is_correct,
                    "correct_answer": q.get('correct'),
                    "explanation": q.get('explanation', '')
                })

            score = int(correct_count / len(module.quiz) * 100) if module.quiz else 0

            return jsonify({
                "success": True,
                "score": score,
                "correct_count": correct_count,
                "total": len(module.quiz),
                "results": results
            })
        except Exception as e:
            logger.error(f"提交测验失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 握手模拟 ==============
    @app.route('/api/handshake/lessons', methods=['GET'])
    def handshake_lessons():
        try:
            sim = get_handshake_simulator()
            lessons = sim.get_all_lessons()
            return jsonify({"success": True, "lessons": lessons})
        except Exception as e:
            logger.error(f"获取握手课程列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/handshake/lessons/<lesson_id>', methods=['GET'])
    def handshake_lesson_detail(lesson_id):
        try:
            sim = get_handshake_simulator()
            lesson = sim.get_lesson(lesson_id)
            if lesson:
                return jsonify({"success": True, "lesson": lesson})
            return jsonify({"success": False, "error": "课程不存在"}), 404
        except Exception as e:
            logger.error(f"获取握手课程详情失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/handshake/start', methods=['POST'])
    def handshake_start():
        try:
            data = request.get_json() or {}
            ssid = data.get('ssid', 'TestNetwork')
            password = data.get('password', 'password123')
            sim = get_handshake_simulator()
            sim.start_simulation(ssid=ssid, password=password)
            return jsonify({"success": True, "message": "握手模拟已启动"})
        except Exception as e:
            logger.error(f"启动握手模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/handshake/next', methods=['POST'])
    def handshake_next():
        try:
            sim = get_handshake_simulator()
            result = sim.do_step()
            return jsonify({"success": True, "step": result})
        except Exception as e:
            logger.error(f"握手模拟下一步失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/handshake/reset', methods=['POST'])
    def handshake_reset():
        try:
            sim = get_handshake_simulator()
            sim.start_simulation()
            return jsonify({"success": True, "message": "握手模拟已重置"})
        except Exception as e:
            logger.error(f"重置握手模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/handshake/status', methods=['GET'])
    def handshake_status():
        try:
            sim = get_handshake_simulator()
            return jsonify({
                "success": True,
                "step": sim.step,
                "completed": sim.completed,
                "packets_count": len(sim.packets),
                "derivation_steps_count": len(sim.derivation_steps)
            })
        except Exception as e:
            logger.error(f"获取握手模拟状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 攻防场景 ==============
    @app.route('/api/attack/categories', methods=['GET'])
    def attack_categories():
        try:
            sim = get_attack_defense_simulator()
            categories = sim.get_categories()
            return jsonify({"success": True, "categories": categories})
        except Exception as e:
            logger.error(f"获取攻击分类失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/scenarios', methods=['GET'])
    def attack_scenarios():
        try:
            category = request.args.get('category')
            sim = get_attack_defense_simulator()
            scenarios = sim.get_all_scenarios(category)
            return jsonify({"success": True, "scenarios": scenarios})
        except Exception as e:
            logger.error(f"获取攻击场景列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/scenarios/<scenario_id>', methods=['GET'])
    def attack_scenario_detail(scenario_id):
        try:
            sim = get_attack_defense_simulator()
            scenario = sim.get_scenario(scenario_id)
            if scenario:
                return jsonify({"success": True, "scenario": scenario})
            return jsonify({"success": False, "error": "场景不存在"}), 404
        except Exception as e:
            logger.error(f"获取攻击场景详情失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/simulate/start', methods=['POST'])
    def attack_simulate_start():
        try:
            data = request.get_json() or {}
            scenario_id = data.get('scenario_id', '')
            sim = get_attack_defense_simulator()
            result = sim.start_simulation(scenario_id)
            return jsonify(result)
        except Exception as e:
            logger.error(f"启动攻击模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/simulate/next', methods=['POST'])
    def attack_simulate_next():
        try:
            data = request.get_json() or {}
            use_defense = data.get('use_defense', False)
            sim = get_attack_defense_simulator()
            result = sim.next_simulation_step(use_defense=use_defense)
            return jsonify({
                "success": True,
                "step": result.step,
                "status": result.status,
                "message": result.message,
                "defense_triggered": result.defense_triggered,
                "details": result.details
            })
        except Exception as e:
            logger.error(f"攻击模拟下一步失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/simulate/reset', methods=['POST'])
    def attack_simulate_reset():
        try:
            sim = get_attack_defense_simulator()
            result = sim.reset_simulation()
            return jsonify(result)
        except Exception as e:
            logger.error(f"重置攻击模拟失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/attack/defense-summary', methods=['GET'])
    def attack_defense_summary():
        try:
            sim = get_attack_defense_simulator()
            summary = sim.get_all_defense_summary()
            return jsonify({"success": True, "defense_summary": summary})
        except Exception as e:
            logger.error(f"获取防御汇总失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 设置与数据管理 ==============
    @app.route('/api/settings', methods=['GET'])
    def settings_get_all():
        try:
            config = app.config['CONFIG']
            all_config = config.get_all()
            ai_client = app.config['AI_CLIENT']
            ai_status = ai_client.get_status()
            return jsonify({
                "success": True,
                "settings": all_config,
                "ai_status": ai_status
            })
        except Exception as e:
            logger.error(f"获取设置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/settings/general', methods=['POST'])
    def settings_general():
        try:
            data = request.get_json() or {}
            config = app.config['CONFIG']

            theme = data.get('theme')
            language = data.get('language')
            gentle_mode = data.get('gentle_mode')
            log_level = data.get('log_level')
            auto_cleanup = data.get('auto_cleanup')

            if theme is not None:
                config.set('theme', theme)
            if language is not None:
                config.set('language', language)
            if gentle_mode is not None:
                config.set('gentle_mode', gentle_mode)
                app.config['SAFETY'].set_gentle_mode(gentle_mode)
            if log_level is not None:
                config.set('log_level', log_level)
            if auto_cleanup is not None:
                config.set('auto_cleanup', auto_cleanup)

            return jsonify({"success": True, "message": "通用设置已更新"})
        except Exception as e:
            logger.error(f"更新通用设置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/settings/data', methods=['POST'])
    def settings_data():
        try:
            data = request.get_json() or {}
            config = app.config['CONFIG']

            data_path = data.get('data_path')
            if data_path:
                config.set('data_path', data_path)

            return jsonify({"success": True, "message": "数据设置已更新"})
        except Exception as e:
            logger.error(f"更新数据设置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/settings/ai', methods=['POST'])
    def settings_ai():
        try:
            data = request.get_json() or {}
            ai_client = app.config['AI_CLIENT']

            provider = data.get('provider')
            model = data.get('model')
            api_key = data.get('api_key')
            api_url = data.get('api_url')

            if provider:
                ai_client.set_provider(provider, api_url or '')
            if model:
                ai_client.set_model(model)
            if api_key:
                ai_client.set_api_key(api_key)

            return jsonify({"success": True, "message": "AI设置已更新"})
        except Exception as e:
            logger.error(f"更新AI设置失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/settings/ai/test', methods=['POST'])
    def settings_ai_test():
        try:
            ai_client = app.config['AI_CLIENT']
            success = ai_client.test_connection()
            return jsonify({
                "success": success,
                "message": "连接成功" if success else "连接失败"
            })
        except Exception as e:
            logger.error(f"测试AI连接失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/storage/info', methods=['GET'])
    def storage_info():
        try:
            data_manager = app.config['DATA_MANAGER']
            info = data_manager.get_storage_info()
            return jsonify({"success": True, "storage": info})
        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/storage/cleanup', methods=['POST'])
    def storage_cleanup():
        try:
            data = request.get_json() or {}
            cleanup_type = data.get('type', 'temp')
            data_manager = app.config['DATA_MANAGER']

            if cleanup_type == 'temp':
                result = data_manager.cleanup_temp_files()
            elif cleanup_type == 'old':
                days = data.get('days', 7)
                result = data_manager.cleanup_old_data(days)
            else:
                result = data_manager.cleanup_temp_files()

            return jsonify({"success": True, "result": result})
        except Exception as e:
            logger.error(f"清理存储失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/providers', methods=['GET'])
    def ai_providers():
        try:
            providers = [
                {"id": "deepseek", "name": "DeepSeek (推荐)", "models": ["deepseek-chat", "deepseek-reasoner"]},
                {"id": "openai", "name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]},
                {"id": "claude", "name": "Anthropic Claude", "models": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]},
                {"id": "custom", "name": "自定义API", "models": []}
            ]
            return jsonify({"success": True, "providers": providers})
        except Exception as e:
            logger.error(f"获取AI提供商列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== AI增强 ==============
    @app.route('/api/ai/scenarios', methods=['GET'])
    def ai_scenarios():
        try:
            prompt_manager = app.config['PROMPT_MANAGER']
            scenarios = prompt_manager.list_scenarios()
            result = []
            for name, desc in scenarios.items():
                result.append({"id": name, "name": desc, "description": desc})
            return jsonify({"success": True, "scenarios": result})
        except Exception as e:
            logger.error(f"获取AI场景列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/learning-path', methods=['POST'])
    def ai_learning_path():
        try:
            data = request.get_json() or {}
            user_level = data.get('level', 'beginner')
            ai_client = app.config['AI_CLIENT']
            prompt_manager = app.config['PROMPT_MANAGER']

            prompt = prompt_manager.get_learning_path_prompt(user_level)
            response = ai_client.chat(
                prompt,
                system_prompt=prompt_manager.get_system_prompt('teaching')
            )

            if response:
                return jsonify({
                    "success": True,
                    "content": response.content,
                    "level": user_level
                })
            return jsonify({"success": False, "error": "AI响应失败"}), 500
        except Exception as e:
            logger.error(f"获取学习路径推荐失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/ai/explain', methods=['POST'])
    def ai_explain():
        """
        AI动态讲解内容生成
        根据主题和上下文动态生成专业讲解
        """
        try:
            data = request.get_json() or {}
            topic = data.get('topic', '')
            context = data.get('context', {})
            level = data.get('level', 'intermediate')
            detail = data.get('detail', 'basic')

            if not topic:
                return jsonify({"success": False, "error": "主题不能为空"}), 400

            ai_client = app.config['AI_CLIENT']
            prompt_manager = app.config['PROMPT_MANAGER']

            if not ai_client.is_configured():
                return jsonify({
                    "success": False,
                    "error": "AI未配置，请先设置API密钥",
                    "fallback": True
                }), 400

            context_str = ""
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])

            detail_desc = {
                "basic": "简洁明了，适合初学者，200字以内",
                "detailed": "详细深入，包含技术细节，500字左右",
                "full": "全面深入，包含原理、案例、代码示例，1000字左右"
            }.get(detail, "详细深入，包含技术细节")

            prompt = f"""请为我讲解关于「{topic}」的内容。

【讲解要求】
- 知识水平：{level}
- 详细程度：{detail_desc}
- 风格要求：专业但通俗易懂，适当使用比喻和类比
- 结构要求：分点阐述，条理清晰

【相关上下文】
{context_str if context_str else '无额外上下文'}

【输出格式】
请使用HTML格式输出，包含以下部分（如适用）：
1. <h5>概述</h5> - 简要介绍概念
2. <p>...</p> - 核心原理解释
3. <div class="highlight-box">...</div> - 关键点/注意事项
4. <div class="info-steps">...</div> - 步骤/流程（如适用）
5. <div class="teaching-tip-box">...</div> - 实用提示（如适用）

注意：只输出HTML内容，不要包含markdown代码块标记，不要输出其他说明文字。"""

            system_prompt = prompt_manager.get_system_prompt('teaching')
            response = ai_client.chat(
                prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            if response:
                return jsonify({
                    "success": True,
                    "content": response.content,
                    "topic": topic,
                    "detail": detail
                })
            return jsonify({"success": False, "error": "AI响应失败"}), 500
        except Exception as e:
            logger.error(f"AI讲解生成失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== 高级练习 ==============
    @app.route('/api/practice/status', methods=['GET'])
    def practice_status():
        try:
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            status = practice.get_authorization_status()
            return jsonify({"success": True, "status": status})
        except Exception as e:
            logger.error(f"获取高级练习状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/modes', methods=['GET'])
    def practice_modes():
        try:
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            modes = practice.get_practice_modes()
            return jsonify({"success": True, "modes": modes})
        except Exception as e:
            logger.error(f"获取练习模式列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/verify-password-1', methods=['POST'])
    def practice_verify_password_1():
        try:
            data = request.get_json() or {}
            password = data.get('password', '')
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            result = practice.verify_password_1(password)
            return jsonify({"success": result, "message": "验证成功" if result else "验证失败"})
        except Exception as e:
            logger.error(f"高级练习验证第一密码失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/verify-password-2', methods=['POST'])
    def practice_verify_password_2():
        try:
            data = request.get_json() or {}
            password = data.get('password', '')
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            result = practice.verify_password_2(password)
            return jsonify({"success": result, "message": "验证成功" if result else "验证失败"})
        except Exception as e:
            logger.error(f"高级练习验证第二密码失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/confirm-network', methods=['POST'])
    def practice_confirm_network():
        try:
            data = request.get_json() or {}
            user_confirmation = data.get('confirm', False)
            target_network = data.get('target_network', '')
            user_statement = data.get('user_statement', '')

            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            result = practice.confirm_network_authorization(
                user_confirmation, target_network, user_statement
            )
            return jsonify({"success": result, "message": "确认成功" if result else "确认失败"})
        except Exception as e:
            logger.error(f"高级练习网络确认失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/start', methods=['POST'])
    def practice_start():
        try:
            data = request.get_json() or {}
            mode = data.get('mode', 'monitoring')
            target_network = data.get('target_network', '')

            from src.core.advanced_practice import PracticeMode
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )

            mode_enum = PracticeMode(mode)
            result = practice.start_practice_session(mode_enum, target_network)
            return jsonify(result)
        except Exception as e:
            logger.error(f"开始高级练习会话失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/end', methods=['POST'])
    def practice_end():
        try:
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            result = practice.end_session()
            return jsonify(result)
        except Exception as e:
            logger.error(f"结束高级练习会话失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/practice/extend', methods=['POST'])
    def practice_extend():
        try:
            practice = get_advanced_practice_manager(
                safety_manager=app.config['SAFETY'],
                config_manager=app.config['CONFIG']
            )
            result = practice.extend_session()
            return jsonify(result)
        except Exception as e:
            logger.error(f"延长高级练习会话失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ============== WEP破解练习 ==============
    @app.route('/api/wep-practice/status', methods=['GET'])
    def wep_practice_status():
        try:
            sim = get_wep_practice_simulator()
            status = sim.get_progress()
            return jsonify({"success": True, "status": status})
        except Exception as e:
            logger.error(f"获取WEP练习状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/start', methods=['POST'])
    def wep_practice_start():
        try:
            data = request.get_json() or {}
            wep_key = data.get('wep_key', 'abc123')
            ssid = data.get('ssid', 'WEP-Learning-Net')
            sim = get_wep_practice_simulator()
            result = sim.start_practice(wep_key=wep_key, ssid=ssid)
            return jsonify(result)
        except Exception as e:
            logger.error(f"启动WEP练习失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/capture', methods=['POST'])
    def wep_practice_capture():
        try:
            data = request.get_json() or {}
            count = data.get('count', 1000)
            sim = get_wep_practice_simulator()
            result = sim.capture_ivs(count=count)
            return jsonify(result)
        except Exception as e:
            logger.error(f"WEP练习捕获IV失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/crack', methods=['POST'])
    def wep_practice_crack():
        try:
            sim = get_wep_practice_simulator()
            result = sim.get_crack_attempt()
            return jsonify(result)
        except Exception as e:
            logger.error(f"WEP练习破解失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/reset', methods=['POST'])
    def wep_practice_reset():
        try:
            sim = get_wep_practice_simulator()
            result = sim.reset()
            return jsonify(result)
        except Exception as e:
            logger.error(f"重置WEP练习失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/lesson', methods=['GET'])
    def wep_practice_lesson():
        try:
            sim = get_wep_practice_simulator()
            lesson_id = request.args.get('lesson_id')
            if lesson_id:
                result = sim.go_to_lesson(lesson_id)
            else:
                result = sim.get_lesson_content()
            return jsonify(result)
        except Exception as e:
            logger.error(f"获取WEP教学内容失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/lessons', methods=['GET'])
    def wep_practice_lessons_list():
        try:
            sim = get_wep_practice_simulator()
            lessons = sim.get_all_lessons()
            return jsonify({"success": True, "lessons": lessons})
        except Exception as e:
            logger.error(f"获取WEP课程列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/lesson/next', methods=['POST'])
    def wep_practice_lesson_next():
        try:
            sim = get_wep_practice_simulator()
            result = sim.next_lesson()
            return jsonify(result)
        except Exception as e:
            logger.error(f"WEP下一课失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/wep-practice/lesson/prev', methods=['POST'])
    def wep_practice_lesson_prev():
        try:
            sim = get_wep_practice_simulator()
            result = sim.prev_lesson()
            return jsonify(result)
        except Exception as e:
            logger.error(f"WEP上一课失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("WiFi可视化安全学习工具 v2 - Web服务器")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("温和模式已启用")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)

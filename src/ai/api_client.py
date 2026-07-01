"""
大模型API客户端 - WiFi可视化安全学习工具 v2
支持多种大模型API
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from src.core.logger import get_logger
from src.core.config import get_config

logger = get_logger("ai_client")


@dataclass
class AIResponse:
    """AI响应"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class AIClient:
    """
    大模型API客户端
    支持 OpenAI GPT、Claude 等
    """

    def __init__(self):
        """初始化AI客户端"""
        self.config = get_config()
        self._load_config()

        # 请求历史（用于上下文）
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10  # 最大历史记录数

    def _load_config(self):
        """从配置加载API设置"""
        self.api_provider = self.config.get("ai_provider", "openai")
        self.api_key = self.config.get_secure("ai_api_key", "")
        self.model = self.config.get("ai_model", "gpt-4o-mini")
        self.api_url = self._get_api_url()

    def _get_api_url(self) -> str:
        """获取API地址"""
        if self.api_provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.api_provider == "claude":
            return "https://api.anthropic.com/v1/messages"
        elif self.api_provider == "deepseek":
            return "https://api.deepseek.com/chat/completions"
        elif self.api_provider == "custom":
            return self.config.get("ai_api_url", "")
        return ""

    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.config.set_secure("ai_api_key", api_key)
        self.api_key = api_key
        self._load_config()

    def set_provider(self, provider: str, api_url: str = ""):
        """设置提供商"""
        self.config.set("ai_provider", provider)
        if api_url:
            self.config.set("ai_api_url", api_url)
        self._load_config()

    def set_model(self, model: str):
        """设置模型"""
        self.config.set("ai_model", model)
        self.model = model

    def add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

    def chat(
        self,
        message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[AIResponse]:
        """
        发送对话请求

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            AI响应
        """
        if not self.api_key:
            logger.error("API密钥未设置")
            return None

        # 构建消息
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加历史
        messages.extend(self.conversation_history)

        # 添加当前消息
        messages.append({"role": "user", "content": message})

        try:
            if self.api_provider == "openai" or self.api_provider == "deepseek":
                return self._chat_openai(messages, temperature, max_tokens)
            elif self.api_provider == "claude":
                return self._chat_claude(messages, max_tokens)
            else:
                return self._chat_custom(messages, temperature, max_tokens)

        except Exception as e:
            logger.error(f"API请求失败: {e}")
            return None

    def _chat_openai(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int
    ) -> Optional[AIResponse]:
        """OpenAI API请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # 添加到历史
            self.add_to_history("user", messages[-1]["content"])
            self.add_to_history("assistant", content)

            return AIResponse(
                content=content,
                model=result.get("model", self.model),
                usage=result.get("usage", {}),
                finish_reason=result["choices"][0].get("finish_reason", "")
            )
        else:
            logger.error(f"OpenAI API错误: {response.status_code} - {response.text}")
            return None

    def _chat_claude(
        self,
        messages: List[Dict],
        max_tokens: int
    ) -> Optional[AIResponse]:
        """Claude API请求"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # 转换消息格式
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            role = "user" if msg["role"] == "user" else "assistant"
            claude_messages.append({"role": role, "content": msg["content"]})

        data = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": max_tokens
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]

            self.add_to_history("user", messages[-1]["content"])
            self.add_to_history("assistant", content)

            return AIResponse(
                content=content,
                model=result.get("model", self.model),
                usage=result.get("usage", {}),
                finish_reason="stop"
            )
        else:
            logger.error(f"Claude API错误: {response.status_code} - {response.text}")
            return None

    def _chat_custom(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int
    ) -> Optional[AIResponse]:
        """自定义API请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            self.add_to_history("user", messages[-1]["content"])
            self.add_to_history("assistant", content)

            return AIResponse(
                content=content,
                model=result.get("model", self.model),
                usage=result.get("usage", {}),
                finish_reason=result["choices"][0].get("finish_reason", "")
            )
        else:
            logger.error(f"API错误: {response.status_code} - {response.text}")
            return None

    def test_connection(self) -> bool:
        """测试API连接"""
        test_message = "你好，请回复'连接成功'。"

        try:
            response = self.chat(
                test_message,
                system_prompt="你是一个测试助手。",
                temperature=0.1,
                max_tokens=50
            )

            if response and "成功" in response.content:
                logger.info(f"API连接测试成功，模型: {response.model}")
                return True
            else:
                logger.warning("API连接测试失败")
                return False

        except Exception as e:
            logger.error(f"API连接测试异常: {e}")
            return False

    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key and self.api_url)

    def get_status(self) -> Dict[str, Any]:
        """获取客户端状态"""
        return {
            "provider": self.api_provider,
            "model": self.model,
            "configured": self.is_configured(),
            "history_length": len(self.conversation_history)
        }

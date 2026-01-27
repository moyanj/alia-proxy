import httpx
import json
import time
from typing import Any, Dict, Optional, AsyncGenerator, List
from .base import BaseProvider, ChatRequest, ChatResponse, Usage, ChatMessage


class AnthropicProvider(BaseProvider):
    """
    Anthropic 接口实现类。
    负责处理与 Anthropic API 的通信，并将响应映射为 OpenAI 兼容格式。
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url or "https://api.anthropic.com/v1")

    def _map_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        内部工具方法：将内部消息模型转换为 Anthropic API 要求的格式。
        """
        return [{"role": m.role, "content": m.content} for m in messages]

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        发送非流式聊天请求到 Anthropic。
        包含对系统消息的特殊处理（Anthropic 要求系统消息作为顶层参数）。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            # 提取系统消息
            system_message = next(
                (m.content for m in request.messages if m.role == "system"), None
            )
            # 过滤掉系统消息，保留普通对话消息
            messages = [m for m in request.messages if m.role != "system"]

            payload = {
                "model": request.model,
                "messages": self._map_messages(messages),
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            }
            # Anthropic 强制要求指定 max_tokens
            if not payload["max_tokens"]:
                raise ValueError("Anthropic requires 'max_tokens' to be specified.")
            if system_message:
                payload["system"] = system_message

            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            # 将 Anthropic 响应映射为 OpenAI 兼容的 ChatResponse
            return ChatResponse(
                id=data["id"],
                created=int(time.time()),
                model=data["model"],
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                data["content"][0]["text"] if data["content"] else ""
                            ),
                        },
                        "finish_reason": data.get("stop_reason"),
                    }
                ],
                usage=Usage(
                    prompt_tokens=data["usage"]["input_tokens"],
                    completion_tokens=data["usage"]["output_tokens"],
                    total_tokens=data["usage"]["input_tokens"]
                    + data["usage"]["output_tokens"],
                ),
            )

    async def stream(
        self, request: ChatRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        发送流式聊天请求到 Anthropic。
        实时将 Anthropic 的事件流转换为 OpenAI 的 data: 格式。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            system_message = next(
                (m.content for m in request.messages if m.role == "system"), None
            )
            messages = [m for m in request.messages if m.role != "system"]

            payload = {
                "model": request.model,
                "messages": self._map_messages(messages),
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": True,
            }
            if not payload["max_tokens"]:
                raise ValueError("Anthropic requires 'max_tokens' to be specified.")
            if system_message:
                payload["system"] = system_message

            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        event_data = json.loads(data_str)

                        # 映射 Anthropic 流事件到 OpenAI 兼容格式
                        event_type = event_data.get("type")
                        if event_type == "content_block_delta":
                            yield {
                                "choices": [
                                    {
                                        "delta": {
                                            "content": event_data["delta"]["text"]
                                        },
                                        "index": 0,
                                        "finish_reason": None,
                                    }
                                ]
                            }
                        elif event_type == "message_stop":
                            break

    async def image_gen(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        Anthropic 目前不支持图像生成。
        """
        raise NotImplementedError("Anthropic does not support image generation")

    async def text_to_speech(self, text: str, model: str, voice: str) -> bytes:
        """
        Anthropic 目前不支持语音合成。
        """
        raise NotImplementedError("Anthropic does not support text-to-speech")

import httpx
import json
import time
from typing import Any, Dict, Optional, AsyncGenerator, List
from .base import (
    BaseProvider,
    ChatRequest,
    ChatResponse,
    Usage,
    ChatMessage,
    ToolCall,
    ToolCallFunction,
    ChatCompletionChoice,
    ProviderConfig,
    EmbeddingsRequest,
    EmbeddingsResponse,
)


class AnthropicProvider(BaseProvider):
    """
    Anthropic 接口实现类。
    负责处理与 Anthropic API 的通信，并将响应映射为 OpenAI 兼容格式。
    """

    def __init__(self, config: ProviderConfig):
        if not config.base_url:
            config.base_url = "https://api.anthropic.com/v1"
        super().__init__(config)

    async def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResponse:
        """
        Anthropic 目前不支持嵌入生成。
        """
        raise NotImplementedError("Anthropic does not support embeddings")

    def _map_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        内部工具方法：将内部消息模型转换为 Anthropic API 要求的格式。
        支持多模态和工具调用转换。
        """
        mapped = []
        for m in messages:
            content = m.content
            # 处理多模态内容转换 (OpenAI 格式 -> Anthropic 格式)
            if isinstance(content, list):
                new_content = []
                for item in content:
                    if item.get("type") == "text":
                        new_content.append({"type": "text", "text": item["text"]})
                    elif item.get("type") == "image_url":
                        # OpenAI: {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                        # Anthropic: {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
                        url = item["image_url"]["url"]
                        if url.startswith("data:"):
                            header, data = url.split(",", 1)
                            media_type = header.split(";")[0].split(":")[1]
                            new_content.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": data,
                                    },
                                }
                            )
                content = new_content

            if m.role == "assistant" and m.tool_calls:
                # 转换工具调用为 Anthropic 的 tool_use 块
                if not isinstance(content, list):
                    content = [{"type": "text", "text": content or ""}]
                for tc in m.tool_calls:
                    content.append(
                        {
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.function.name,
                            "input": json.loads(tc.function.arguments),
                        }
                    )

            if m.role == "tool":
                # Anthropic 要求工具结果作为 'user' 角色的 content block
                # 且必须紧跟在 tool_use 之后
                mapped.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": m.tool_call_id,
                                "content": m.content,
                            }
                        ],
                    }
                )
                continue

            mapped.append({"role": m.role, "content": content})
        return mapped

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        发送非流式聊天请求到 Anthropic。
        包含对系统消息、工具调用、停止序列等的处理。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            # 提取并合并所有系统消息
            system_messages = [
                m.content for m in request.messages if m.role == "system"
            ]
            system_message = (
                "\n".join([str(m) for m in system_messages])
                if system_messages
                else None
            )
            # 过滤掉系统消息
            messages = [m for m in request.messages if m.role != "system"]

            payload = {
                "model": request.model,
                "messages": self._map_messages(messages),
                "max_tokens": request.max_tokens or 4096,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }

            if request.stop:
                payload["stop_sequences"] = (
                    [request.stop] if isinstance(request.stop, str) else request.stop
                )

            if system_message:
                payload["system"] = system_message

            if request.tools:
                payload["tools"] = [
                    {
                        "name": t.function.name,
                        "description": t.function.description or "",
                        "input_schema": t.function.parameters
                        or {"type": "object", "properties": {}},
                    }
                    for t in request.tools
                ]
                # 处理工具选择策略转换
                if request.tool_choice:
                    if request.tool_choice == "auto":
                        payload["tool_choice"] = {"type": "auto"}
                    elif request.tool_choice == "required":
                        payload["tool_choice"] = {"type": "any"}
                    elif isinstance(request.tool_choice, dict):
                        func_name = request.tool_choice.get("function", {}).get("name")
                        if func_name:
                            payload["tool_choice"] = {
                                "type": "tool",
                                "name": func_name,
                            }

            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            # 解析 Anthropic 内容块 (text + tool_use)
            content_text = ""
            tool_calls_list = []
            for block in data.get("content", []):
                if block["type"] == "text":
                    content_text += block["text"]
                elif block["type"] == "tool_use":
                    tool_calls_list.append(
                        ToolCall(
                            id=block["id"],
                            type="function",
                            function=ToolCallFunction(
                                name=block["name"],
                                arguments=json.dumps(block["input"]),
                            ),
                        )
                    )

            return ChatResponse(
                id=data["id"],
                created=int(time.time()),
                model=data["model"],
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=content_text or None,
                            tool_calls=tool_calls_list if tool_calls_list else None,
                        ),
                        finish_reason=(
                            "tool_calls" if tool_calls_list else data.get("stop_reason")
                        ),
                    )
                ],
                usage=Usage(
                    prompt_tokens=data["usage"]["input_tokens"],
                    completion_tokens=data["usage"]["output_tokens"],
                    total_tokens=data["usage"]["input_tokens"]
                    + data["usage"]["output_tokens"],
                ),
            )

    async def chat_native(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        原生 Anthropic 消息接口。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def stream_native(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        原生 Anthropic 消息流接口。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload["stream"] = True
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line

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
                "max_tokens": request.max_tokens or 4096,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "stream": True,
            }

            if request.stop:
                payload["stop_sequences"] = (
                    [request.stop] if isinstance(request.stop, str) else request.stop
                )

            if system_message:
                payload["system"] = system_message

            if request.tools:
                payload["tools"] = [
                    {
                        "name": t.function.name,
                        "description": t.function.description or "",
                        "input_schema": t.function.parameters
                        or {"type": "object", "properties": {}},
                    }
                    for t in request.tools
                ]
                # 处理工具选择策略转换
                if request.tool_choice:
                    if request.tool_choice == "auto":
                        payload["tool_choice"] = {"type": "auto"}
                    elif request.tool_choice == "required":
                        payload["tool_choice"] = {"type": "any"}
                    elif isinstance(request.tool_choice, dict):
                        func_name = request.tool_choice.get("function", {}).get("name")
                        if func_name:
                            payload["tool_choice"] = {
                                "type": "tool",
                                "name": func_name,
                            }

            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                message_id = ""
                model_name = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        event_data = json.loads(data_str)
                        event_type = event_data.get("type")

                        if event_type == "message_start":
                            message_id = event_data["message"]["id"]
                            model_name = event_data["message"]["model"]
                            yield {
                                "id": message_id,
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": model_name,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {"role": "assistant", "content": ""},
                                        "finish_reason": None,
                                    }
                                ],
                            }

                        elif event_type == "content_block_delta":
                            delta = event_data["delta"]
                            block_index = event_data.get("index", 0)
                            if delta["type"] == "text_delta":
                                yield {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": model_name,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {"content": delta["text"]},
                                            "finish_reason": None,
                                        }
                                    ],
                                }
                            elif delta["type"] == "input_json_delta":
                                # 处理工具调用参数流
                                yield {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": model_name,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {
                                                "tool_calls": [
                                                    {
                                                        "index": block_index,
                                                        "function": {
                                                            "arguments": delta[
                                                                "partial_json"
                                                            ]
                                                        },
                                                    }
                                                ]
                                            },
                                            "finish_reason": None,
                                        }
                                    ],
                                }

                        elif event_type == "content_block_start":
                            block_index = event_data.get("index", 0)
                            if event_data["content_block"]["type"] == "tool_use":
                                block = event_data["content_block"]
                                yield {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": model_name,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {
                                                "tool_calls": [
                                                    {
                                                        "index": block_index,
                                                        "id": block["id"],
                                                        "type": "function",
                                                        "function": {
                                                            "name": block["name"],
                                                            "arguments": "",
                                                        },
                                                    }
                                                ]
                                            },
                                            "finish_reason": None,
                                        }
                                    ],
                                }

                        elif event_type == "message_delta":
                            stop_reason = event_data["delta"].get("stop_reason")
                            finish_reason = stop_reason
                            if stop_reason == "end_turn":
                                finish_reason = "stop"
                            elif stop_reason == "tool_use":
                                finish_reason = "tool_calls"

                            yield {
                                "id": message_id,
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": model_name,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": finish_reason,
                                    }
                                ],
                                "usage": (
                                    {
                                        "prompt_tokens": 0,  # Anthropic 流不实时返回总用量，除非收尾
                                        "completion_tokens": event_data["usage"][
                                            "output_tokens"
                                        ],
                                        "total_tokens": event_data["usage"][
                                            "output_tokens"
                                        ],
                                    }
                                    if "usage" in event_data
                                    else None
                                ),
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

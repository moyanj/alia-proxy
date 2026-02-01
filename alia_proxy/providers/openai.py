import httpx
import json
from typing import Any, Dict, Optional, AsyncGenerator, List
from .base import (
    BaseProvider,
    ChatRequest,
    ChatResponse,
    ProviderConfig,
    EmbeddingsRequest,
    EmbeddingsResponse,
)


class OpenAIProvider(BaseProvider):
    """
    OpenAI 接口实现类。
    适用于 OpenAI 官方 API 以及任何兼容 OpenAI 格式的第三方代理。
    """

    def __init__(self, config: ProviderConfig):
        if not config.base_url:
            config.base_url = "https://api.openai.com/v1"
        super().__init__(config)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        发送非流式聊天请求。
        """
        timeout = getattr(self.config, "timeout", 60.0)
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            return ChatResponse(**data)

    async def embeddings(self, request: EmbeddingsRequest) -> EmbeddingsResponse:
        """
        发送嵌入生成请求。
        """
        timeout = getattr(self.config, "timeout", 60.0)
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            return EmbeddingsResponse(**data)

    async def stream(
        self, request: ChatRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        发送流式聊天请求。
        """
        timeout = getattr(self.config, "timeout", 60.0)
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = request.model_dump(exclude_none=True)
            payload["stream"] = True
            # 默认请求包含 usage，以便记录 Token 消耗
            if "stream_options" not in payload:
                payload["stream_options"] = {"include_usage": True}

            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        yield json.loads(data_str)

    async def image_gen(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        发送图像生成请求。
        要求返回 b64_json 格式以便后端保存。
        """
        timeout = getattr(self.config, "timeout", 60.0)
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json={"prompt": prompt, "model": model, "response_format": "b64_json"},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()

    async def text_to_speech(self, text: str, model: str, voice: str) -> bytes:
        """
        发送文本转语音请求。
        """
        timeout = getattr(self.config, "timeout", 60.0)
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(
                f"{self.base_url}/audio/speech",
                headers=headers,
                json={"input": text, "model": model, "voice": voice},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.content

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        获取 OpenAI 兼容接口的模型列表。
        """
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            response = await client.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

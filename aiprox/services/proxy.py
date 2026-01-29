import time
import json
import base64
from typing import Any, Dict, Tuple, AsyncGenerator
from ..providers.base import (
    BaseProvider,
    ChatRequest,
    EmbeddingsRequest,
    EmbeddingsResponse,
)
from ..services.logger import log_request
from ..services.media import save_media


class ProxyService:
    """
    代理服务类。
    封装了对具体提供商的调用逻辑，并自动集成日志记录和媒体存储功能。
    """

    def __init__(
        self,
        provider: BaseProvider,
        model: str,
        instance_name: str,
        request_ip: str = "",
    ):
        """
        初始化代理服务。
        :param provider: 已实例化的提供商对象
        :param model: 请求中指定的模型名称
        :param instance_name: 提供商配置的实例名称 (用于日志)
        :param request_ip: 请求者的 IP 地址
        """
        self.provider = provider
        self.model = model
        self.instance_name = instance_name
        self.request_ip = request_ip

    async def chat(self, chat_request: ChatRequest) -> Dict[str, Any]:
        """
        处理非流式聊天请求。
        调用提供商 API，记录日志并返回响应结果。
        """
        start_time = time.perf_counter()
        try:
            response = await self.provider.chat(chat_request)
            latency = time.perf_counter() - start_time

            resp_content = response.choices[0].message.content
            if isinstance(resp_content, list):
                resp_content = json.dumps(resp_content, ensure_ascii=False)
            elif resp_content is None:
                resp_content = ""

            # 记录请求和响应到数据库
            await log_request(
                provider=self.instance_name,
                endpoint="chat",
                model=self.model,
                prompt=str(chat_request.messages),
                response=resp_content,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                status_code=200,
                latency=latency,
                ip_address=self.request_ip,
                request_id=response.id,
                is_streaming=False,
            )
            return response.model_dump(exclude_none=True)
        except Exception as e:
            latency = time.perf_counter() - start_time
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="chat",
                model=self.model,
                prompt=str(chat_request.messages),
                error=str(e),
                status_code=status_code,
                latency=latency,
                ip_address=self.request_ip,
            )
            raise

    async def embeddings(self, request: EmbeddingsRequest) -> Dict[str, Any]:
        """
        处理嵌入请求。
        调用提供商 API，记录日志并返回响应结果。
        """
        start_time = time.perf_counter()
        try:
            response = await self.provider.embeddings(request)
            latency = time.perf_counter() - start_time
            # 记录请求和响应到数据库
            await log_request(
                provider=self.instance_name,
                endpoint="embeddings",
                model=self.model,
                prompt=str(request.input),
                response="[Embeddings Data]",
                prompt_tokens=response.usage.prompt_tokens,
                total_tokens=response.usage.total_tokens,
                status_code=200,
                latency=latency,
                ip_address=self.request_ip,
                request_id=getattr(response, "id", None),
                is_streaming=False,
            )
            return response.model_dump(exclude_none=True)
        except Exception as e:
            latency = time.perf_counter() - start_time
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="embeddings",
                model=self.model,
                prompt=str(request.input),
                error=str(e),
                status_code=status_code,
                latency=latency,
                ip_address=self.request_ip,
            )
            raise

    async def chat_stream(self, chat_request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        处理流式聊天请求。
        逐块返回数据，并在流结束后将完整对话记录到日志中。
        """
        start_time = time.perf_counter()
        full_content = ""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        status_code = 200

        try:
            async for chunk in self.provider.stream(chat_request):
                if chunk:
                    # 提取增量内容用于最后记录完整响应
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            full_content += delta["content"]

                        # 某些提供商在最后一块返回 usage
                        if "usage" in chunk and chunk["usage"]:
                            usage = chunk["usage"]
                            prompt_tokens = usage.get("prompt_tokens", 0)
                            completion_tokens = usage.get("completion_tokens", 0)
                            total_tokens = usage.get("total_tokens", 0)

                    yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="chat",
                model=self.model,
                prompt=str(chat_request.messages),
                error=str(e),
                status_code=status_code,
                latency=time.perf_counter() - start_time,
                ip_address=self.request_ip,
            )
            raise

        latency = time.perf_counter() - start_time
        # 流结束后异步记录完整日志
        await log_request(
            provider=self.instance_name,
            endpoint="chat",
            model=self.model,
            prompt=str(chat_request.messages),
            response=full_content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            status_code=status_code,
            latency=latency,
            ip_address=self.request_ip,
            is_streaming=True,
        )

    async def image_gen(self, prompt: str) -> Dict[str, Any]:
        """
        处理图像生成请求。
        生成图像后将其保存到本地存储，并将 Base64 替换为本地访问 URL。
        """
        start_time = time.perf_counter()
        try:
            response = await self.provider.image_gen(prompt, self.model)
            latency = time.perf_counter() - start_time

            media_filename = ""
            for item in response.get("data", []):
                if "b64_json" in item:
                    # 解码 Base64 并保存为本地文件
                    image_bytes = base64.b64decode(item["b64_json"])
                    filename = await save_media(image_bytes, "png")
                    # 替换为内部 API URL
                    item["url"] = f"/api/media/{filename}"
                    del item["b64_json"]
                    media_filename = filename

            # 记录日志
            await log_request(
                provider=self.instance_name,
                endpoint="image",
                model=self.model,
                prompt=prompt,
                media_path=media_filename,
                status_code=200,
                latency=latency,
                ip_address=self.request_ip,
            )
            return response
        except Exception as e:
            latency = time.perf_counter() - start_time
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="image",
                model=self.model,
                prompt=prompt,
                error=str(e),
                status_code=status_code,
                latency=latency,
                ip_address=self.request_ip,
            )
            raise

    async def text_to_speech(self, text: str, voice: str) -> Tuple[bytes, str]:
        """
        处理文本转语音请求。
        将生成的音频流保存到本地，并返回音频数据及其文件名。
        """
        start_time = time.perf_counter()
        try:
            content = await self.provider.text_to_speech(text, self.model, voice)
            latency = time.perf_counter() - start_time
            filename = await save_media(content, "mp3")
            # 记录音频请求日志
            await log_request(
                provider=self.instance_name,
                endpoint="audio",
                model=self.model,
                prompt=text,
                media_path=filename,
                media_type="audio",
                status_code=200,
                latency=latency,
                ip_address=self.request_ip,
            )
            return content, filename
        except Exception as e:
            latency = time.perf_counter() - start_time
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="audio",
                model=self.model,
                prompt=text,
                error=str(e),
                status_code=status_code,
                latency=latency,
                ip_address=self.request_ip,
            )
            raise

    async def anthropic_chat(self, body: Dict[str, Any]) -> Any:
        """
        处理 Anthropic 原生消息请求。
        """
        start_time = time.perf_counter()
        # 确保模型字段正确
        body["model"] = self.model

        # 如果是流式请求
        if body.get("stream"):
            return self.anthropic_chat_stream(body)

        # 否则是非流式
        from ..providers.anthropic import AnthropicProvider

        if isinstance(self.provider, AnthropicProvider):
            try:
                response = await self.provider.chat_native(body)
                latency = time.perf_counter() - start_time

                # 记录日志
                content = ""
                for block in response.get("content", []):
                    if block["type"] == "text":
                        content += block["text"]

                await log_request(
                    provider=self.instance_name,
                    endpoint="anthropic/messages",
                    model=self.model,
                    prompt=str(body.get("messages")),
                    response=content,
                    prompt_tokens=response.get("usage", {}).get("input_tokens", 0),
                    completion_tokens=response.get("usage", {}).get("output_tokens", 0),
                    total_tokens=response.get("usage", {}).get("input_tokens", 0)
                    + response.get("usage", {}).get("output_tokens", 0),
                    status_code=200,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_id=response.get("id"),
                    is_streaming=False,
                )
                return response
            except Exception as e:
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=self.instance_name,
                    endpoint="anthropic/messages",
                    model=self.model,
                    prompt=str(body.get("messages")),
                    error=str(e),
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                )
                raise
        else:
            raise ValueError(
                "Selected provider does not support Anthropic native format"
            )

    async def anthropic_chat_stream(
        self, body: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        处理 Anthropic 原生流式消息请求。
        """
        start_time = time.perf_counter()
        from ..providers.anthropic import AnthropicProvider

        if not isinstance(self.provider, AnthropicProvider):
            raise ValueError(
                "Selected provider does not support Anthropic native format"
            )

        full_content = ""
        input_tokens = 0
        output_tokens = 0
        status_code = 200

        try:
            async for line in self.provider.stream_native(body):
                # 解析内容用于记录日志
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data["type"] == "content_block_delta":
                        if data["delta"]["type"] == "text_delta":
                            full_content += data["delta"]["text"]
                    elif data["type"] == "message_start":
                        input_tokens = data["message"]["usage"]["input_tokens"]
                    elif data["type"] == "message_delta":
                        output_tokens = data["usage"]["output_tokens"]

                yield line + "\n"
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            await log_request(
                provider=self.instance_name,
                endpoint="anthropic/messages",
                model=self.model,
                prompt=str(body.get("messages")),
                error=str(e),
                status_code=status_code,
                latency=time.perf_counter() - start_time,
                ip_address=self.request_ip,
            )
            raise

        # 记录日志
        await log_request(
            provider=self.instance_name,
            endpoint="anthropic/messages",
            model=self.model,
            prompt=str(body.get("messages")),
            response=full_content,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            status_code=status_code,
            latency=time.perf_counter() - start_time,
            ip_address=self.request_ip,
            is_streaming=True,
        )

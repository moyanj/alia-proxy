import time
import json
import base64
from typing import Any, Dict, Tuple, AsyncGenerator, List, Union, Optional
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
    支持故障自动降级 (Fallback)。
    """

    def __init__(
        self,
        provider: BaseProvider,
        model: str,
        instance_name: str,
        request_ip: str = "",
        fallbacks: Optional[List[str]] = None,
        original_model: Optional[str] = None,
    ):
        """
        初始化代理服务。
        :param provider: 已实例化的提供商对象
        :param model: 请求中指定的模型名称
        :param instance_name: 提供商配置的实例名称 (用于日志)
        :param request_ip: 请求者的 IP 地址
        :param fallbacks: 降级备选模型列表
        :param original_model: 用户请求的原始模型名称 (用于日志记录)
        """
        self.provider = provider
        self.model = model
        self.instance_name = instance_name
        self.request_ip = request_ip
        self.fallbacks = fallbacks or []
        self.original_model = original_model

    def _get_candidates(self) -> List[Tuple[BaseProvider, str, str]]:
        """
        获取所有候选提供商 (主提供商 + 降级提供商)。
        :return: List[(Provider, ModelName, InstanceName)]
        """
        candidates = [(self.provider, self.model, self.instance_name)]
        if self.fallbacks:
            from ..providers.factory import ProviderFactory

            for fb in self.fallbacks:
                try:
                    # resolve_model returns (instance, model, fallbacks)
                    # We ignore nested fallbacks to prevent infinite recursion/complexity
                    inst, mod, _ = ProviderFactory.resolve_model(fb)
                    prov = ProviderFactory.get_provider(inst)
                    candidates.append((prov, mod, inst))
                except Exception:
                    # 如果解析或获取 fallback 失败，忽略该候选项
                    pass
        return candidates

    def _get_request_model(self) -> Optional[str]:
        """
        获取请求模型名称。
        如果原始模型名与当前模型名不同，则返回原始模型名。
        """
        if self.original_model and self.original_model != self.model:
            return self.original_model
        return None

    async def _process_messages_for_log(
        self, messages: List[Any]
    ) -> Tuple[str, List[str]]:
        """
        处理消息列表，提取并转存 Base64 图片，返回脱敏后的 prompt 文本和媒体文件列表。
        """
        processed_messages = []
        media_paths = []

        for m in messages:
            # 兼容对象和字典
            role = getattr(m, "role", None) or m.get("role")
            content = getattr(m, "content", None) or m.get("content")

            if isinstance(content, list):
                new_content = []
                for item in content:
                    if (
                        isinstance(item, dict)
                        and item.get("type") == "image_url"
                        and "image_url" in item
                    ):
                        url = item["image_url"].get("url", "")
                        if url.startswith("data:image"):
                            try:
                                # 提取 base64 数据
                                header, data = url.split(",", 1)
                                ext = header.split(";")[0].split("/")[1]
                                image_bytes = base64.b64decode(data)
                                # 转存
                                filename = await save_media(image_bytes, ext)
                                media_paths.append(filename)
                                # 替换为占位符
                                new_content.append(
                                    {
                                        "type": "image_url",
                                        "image_url": f"[IMAGE: {filename}]",
                                    }
                                )
                                continue
                            except Exception:
                                pass
                    new_content.append(item)
                processed_messages.append({"role": role, "content": new_content})
            else:
                processed_messages.append({"role": role, "content": content})

        return json.dumps(processed_messages, ensure_ascii=False), media_paths

    async def chat(self, chat_request: ChatRequest) -> Dict[str, Any]:
        """
        处理非流式聊天请求。
        调用提供商 API，记录日志并返回响应结果。
        支持自动降级。
        """
        # 预处理请求，转存图片 (仅需做一次)
        prompt_json, media_paths = await self._process_messages_for_log(
            chat_request.messages
        )

        candidates = self._get_candidates()
        last_exception = None

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            try:
                # 更新请求中的模型名称
                chat_request.model = model

                response = await provider.chat(chat_request)
                latency = time.perf_counter() - start_time

                resp_content = response.choices[0].message.content
                if isinstance(resp_content, list):
                    resp_content = json.dumps(resp_content, ensure_ascii=False)
                elif resp_content is None:
                    resp_content = ""

                # 记录请求和响应到数据库
                await log_request(
                    provider=instance_name,
                    endpoint="chat",
                    model=model,
                    prompt=prompt_json,
                    response=resp_content,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    status_code=200,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_id=response.id,
                    is_streaming=False,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                return response.model_dump(exclude_none=True)

            except Exception as e:
                last_exception = e
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)

                # 记录错误日志
                await log_request(
                    provider=instance_name,
                    endpoint="chat",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )

                # 如果是最后一个候选项，则抛出异常
                if i == len(candidates) - 1:
                    raise

        # Should be unreachable if candidates is not empty
        if last_exception:
            raise last_exception
        raise Exception("No providers available")

    async def embeddings(self, request: EmbeddingsRequest) -> Dict[str, Any]:
        """
        处理嵌入请求。
        支持自动降级。
        """
        prompt_str = json.dumps(request.input, ensure_ascii=False)
        candidates = self._get_candidates()
        last_exception = None

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            try:
                request.model = model
                response = await provider.embeddings(request)
                latency = time.perf_counter() - start_time

                # 记录请求和响应到数据库
                await log_request(
                    provider=instance_name,
                    endpoint="embeddings",
                    model=model,
                    prompt=prompt_str,
                    response="[Embeddings Data]",
                    prompt_tokens=response.usage.prompt_tokens,
                    total_tokens=response.usage.total_tokens,
                    status_code=200,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_id=getattr(response, "id", None),
                    is_streaming=False,
                    request_model=self._get_request_model(),
                )
                return response.model_dump(exclude_none=True)
            except Exception as e:
                last_exception = e
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=instance_name,
                    endpoint="embeddings",
                    model=model,
                    prompt=prompt_str,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_model=self._get_request_model(),
                )
                if i == len(candidates) - 1:
                    raise

        if last_exception:
            raise last_exception
        raise Exception("No providers available")

    async def chat_stream(self, chat_request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        处理流式聊天请求。
        支持自动降级 (仅在流启动失败时重试)。
        """
        prompt_json, media_paths = await self._process_messages_for_log(
            chat_request.messages
        )

        candidates = self._get_candidates()

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            full_content = ""
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            status_code = 200
            error_occured = False

            try:
                chat_request.model = model

                # 获取生成器
                stream_gen = provider.stream(chat_request)

                # 尝试获取第一个块 (用于检测启动错误)
                try:
                    first_chunk = await stream_gen.__anext__()
                except StopAsyncIteration:
                    # 空流？视为成功但无内容
                    yield "data: [DONE]\n\n"
                    return
                except Exception as e:
                    # 启动失败，记录并尝试下一个
                    raise e

                # 如果成功获取第一块，说明连接建立，开始输出

                # 处理第一个块
                if first_chunk:
                    if "choices" in first_chunk and len(first_chunk["choices"]) > 0:
                        delta = first_chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            full_content += delta["content"]
                    if "usage" in first_chunk and first_chunk["usage"]:
                        usage = first_chunk["usage"]
                        prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                        completion_tokens = usage.get(
                            "completion_tokens", completion_tokens
                        )
                        total_tokens = usage.get(
                            "total_tokens", prompt_tokens + completion_tokens
                        )
                    yield f"data: {json.dumps(first_chunk)}\n\n"

                # 处理后续块
                async for chunk in stream_gen:
                    if chunk:
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_content += delta["content"]
                        if "usage" in chunk and chunk["usage"]:
                            usage = chunk["usage"]
                            prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                            completion_tokens = usage.get(
                                "completion_tokens", completion_tokens
                            )
                            total_tokens = usage.get(
                                "total_tokens", prompt_tokens + completion_tokens
                            )
                        yield f"data: {json.dumps(chunk)}\n\n"

                yield "data: [DONE]\n\n"

                # 成功完成整个流，记录完整日志
                latency = time.perf_counter() - start_time
                await log_request(
                    provider=instance_name,
                    endpoint="chat",
                    model=model,
                    prompt=prompt_json,
                    response=full_content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    is_streaming=True,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                return

            except Exception as e:
                error_occured = True
                status_code = getattr(e, "status_code", 500)
                latency = time.perf_counter() - start_time

                await log_request(
                    provider=instance_name,
                    endpoint="chat",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )

                # 如果是最后一个，抛出
                if i == len(candidates) - 1:
                    raise
                # 否则继续下一个循环
                continue

    async def image_gen(self, prompt: str) -> Dict[str, Any]:
        """
        处理图像生成请求。
        支持自动降级。
        """
        prompt_json = json.dumps(prompt, ensure_ascii=False)
        candidates = self._get_candidates()
        last_exception = None

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            try:
                response = await provider.image_gen(prompt, model)
                latency = time.perf_counter() - start_time

                media_filenames = []
                for item in response.get("data", []):
                    if "b64_json" in item:
                        # 解码 Base64 并保存为本地文件
                        image_bytes = base64.b64decode(item["b64_json"])
                        filename = await save_media(image_bytes, "png")
                        # 替换为内部 API URL
                        item["url"] = f"/api/media/{filename}"
                        del item["b64_json"]
                        media_filenames.append(filename)
                    elif "url" in item and item["url"].startswith("http"):
                        pass

                # 记录日志
                await log_request(
                    provider=instance_name,
                    endpoint="image",
                    model=model,
                    prompt=prompt_json,
                    media_path=media_filenames,
                    status_code=200,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_model=self._get_request_model(),
                )
                return response
            except Exception as e:
                last_exception = e
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=instance_name,
                    endpoint="image",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_model=self._get_request_model(),
                )
                if i == len(candidates) - 1:
                    raise

        if last_exception:
            raise last_exception
        raise Exception("No providers available")

    async def text_to_speech(self, text: str, voice: str) -> Tuple[bytes, str]:
        """
        处理文本转语音请求。
        支持自动降级。
        """
        prompt_json = json.dumps(text, ensure_ascii=False)
        candidates = self._get_candidates()
        last_exception = None

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            try:
                content = await provider.text_to_speech(text, model, voice)
                latency = time.perf_counter() - start_time
                filename = await save_media(content, "mp3")

                await log_request(
                    provider=instance_name,
                    endpoint="audio",
                    model=model,
                    prompt=prompt_json,
                    media_path=filename,
                    media_type="audio",
                    status_code=200,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_model=self._get_request_model(),
                )
                return content, filename
            except Exception as e:
                last_exception = e
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=instance_name,
                    endpoint="audio",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    request_model=self._get_request_model(),
                )
                if i == len(candidates) - 1:
                    raise

        if last_exception:
            raise last_exception
        raise Exception("No providers available")

    async def anthropic_chat(self, body: Dict[str, Any]) -> Any:
        """
        处理 Anthropic 原生消息请求。
        支持自动降级 (仅限支持 Anthropic 协议的提供商)。
        """
        messages = body.get("messages", [])
        prompt_json, media_paths = await self._process_messages_for_log(messages)

        candidates = self._get_candidates()

        # 如果是流式请求
        if body.get("stream"):
            return self.anthropic_chat_stream(body, prompt_json, media_paths)

        from ..providers.anthropic import AnthropicProvider

        last_exception = None

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()

            # 检查提供商类型
            if not isinstance(provider, AnthropicProvider):
                # 如果不是 Anthropic 提供商，如果是主提供商则报错，如果是 fallback 则跳过
                e = ValueError(
                    f"Provider {instance_name} does not support Anthropic native format"
                )
                if i == 0 and len(candidates) == 1:
                    raise e
                # 记录跳过日志? 暂时略过
                continue

            try:
                # 确保模型字段正确
                body["model"] = model

                response = await provider.chat_native(body)
                latency = time.perf_counter() - start_time

                content = ""
                for block in response.get("content", []):
                    if block["type"] == "text":
                        content += block["text"]

                await log_request(
                    provider=instance_name,
                    endpoint="anthropic/messages",
                    model=model,
                    prompt=prompt_json,
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
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                return response
            except Exception as e:
                last_exception = e
                latency = time.perf_counter() - start_time
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=instance_name,
                    endpoint="anthropic/messages",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=latency,
                    ip_address=self.request_ip,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                if i == len(candidates) - 1:
                    raise

        if last_exception:
            raise last_exception
        raise ValueError("Selected provider does not support Anthropic native format")

    async def anthropic_chat_stream(
        self, body: Dict[str, Any], prompt_json: str, media_paths: List[str]
    ) -> AsyncGenerator[str, None]:
        """
        处理 Anthropic 原生流式消息请求。
        """
        candidates = self._get_candidates()
        from ..providers.anthropic import AnthropicProvider

        for i, (provider, model, instance_name) in enumerate(candidates):
            start_time = time.perf_counter()
            full_content = ""
            input_tokens = 0
            output_tokens = 0
            status_code = 200

            if not isinstance(provider, AnthropicProvider):
                if i == len(candidates) - 1 and i == 0:
                    raise ValueError(
                        "Selected provider does not support Anthropic native format"
                    )
                continue

            try:
                body["model"] = model
                stream_gen = provider.stream_native(body)

                # 尝试获取第一块
                try:
                    first_line = await stream_gen.__anext__()
                except StopAsyncIteration:
                    return
                except Exception as e:
                    raise e

                # 处理第一行
                if first_line.startswith("data: "):
                    data = json.loads(first_line[6:])
                    if data["type"] == "content_block_delta":
                        if data["delta"]["type"] == "text_delta":
                            full_content += data["delta"]["text"]
                    elif data["type"] == "message_start":
                        input_tokens = data["message"]["usage"]["input_tokens"]
                    elif data["type"] == "message_delta":
                        output_tokens = data["usage"]["output_tokens"]
                yield first_line + "\n"

                async for line in stream_gen:
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

                # 成功
                await log_request(
                    provider=instance_name,
                    endpoint="anthropic/messages",
                    model=model,
                    prompt=prompt_json,
                    response=full_content,
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    status_code=status_code,
                    latency=time.perf_counter() - start_time,
                    ip_address=self.request_ip,
                    is_streaming=True,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                return

            except Exception as e:
                status_code = getattr(e, "status_code", 500)
                await log_request(
                    provider=instance_name,
                    endpoint="anthropic/messages",
                    model=model,
                    prompt=prompt_json,
                    error=f"Attempt {i + 1}/{len(candidates)} failed: {str(e)}",
                    status_code=status_code,
                    latency=time.perf_counter() - start_time,
                    ip_address=self.request_ip,
                    media_path=media_paths,
                    request_model=self._get_request_model(),
                )
                if i == len(candidates) - 1:
                    raise
                continue

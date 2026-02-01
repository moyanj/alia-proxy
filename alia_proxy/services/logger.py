from datetime import date
from typing import Optional, List, Union
from ..models import RequestLog, RequestContent, MediaResource


async def log_request(
    provider: str,
    endpoint: str,
    model: str,
    prompt: str = "",
    response: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    status_code: int = 200,
    latency: float = 0.0,
    media_path: Optional[Union[str, List[str]]] = "",
    error: str = "",
    ip_address: str = "",
    request_id: Optional[str] = None,
    is_streaming: bool = False,
    metadata: Optional[dict] = None,
    media_type: str = "image",
    request_model: Optional[str] = None,
):
    """
    异步记录请求日志。
    使用 Tortoise-ORM 将请求元数据、Token 统计和内容负载分别保存到对应的表中。
    """
    # 1. 创建核心元数据日志
    log = await RequestLog.create(
        provider=provider,
        endpoint=endpoint,
        model=model,
        request_model=request_model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        status_code=status_code,
        latency=latency,
        ip_address=ip_address,
        request_id=request_id,
        is_streaming=is_streaming,
        metadata=metadata,
        date=date.today(),
    )

    # 2. 创建详情内容 (Prompt/Response/Error)
    await RequestContent.create(
        log=log,
        prompt=prompt,
        response=response,
        error=error,
    )

    # 3. 如果有关联媒体资源，创建媒体记录
    if media_path:
        paths = [media_path] if isinstance(media_path, str) else media_path
        for path in paths:
            await MediaResource.create(
                log=log,
                file_path=path,
                file_type=media_type,
            )

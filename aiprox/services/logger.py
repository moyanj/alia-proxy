from ..models import RequestLog


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
    media_path: str = "",
    error: str = "",
):
    """
    异步记录请求日志。
    使用 Tortoise-ORM 将请求元数据、Token 统计和错误信息保存到数据库。
    """
    await RequestLog.create(
        provider=provider,
        endpoint=endpoint,
        model=model,
        prompt=prompt,
        response=response,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        status_code=status_code,
        media_path=media_path,
        error=error,
    )

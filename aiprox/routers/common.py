from fastapi import APIRouter, HTTPException, Query
from ..models import RequestLog
from ..config import settings
from tortoise.functions import Count
from typing import Optional

router = APIRouter()


@router.get("/")
async def read_root():
    """
    根路径，用于健康检查。
    """
    return {"app": "AI Proxy Service"}


@router.get("/api/logs")
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
):
    """
    获取请求日志列表，支持过滤和分页。
    """
    query = RequestLog.all()
    if provider:
        query = query.filter(provider=provider)
    if model:
        query = query.filter(model__icontains=model)
    if endpoint:
        query = query.filter(endpoint=endpoint)
    if status_code:
        query = query.filter(status_code=status_code)

    return await query.order_by("-timestamp").limit(limit).offset(offset)


@router.get("/api/logs/{log_id}")
async def get_log_detail(log_id: int):
    """
    获取特定请求日志的详细信息。
    """
    log = await RequestLog.get_or_none(id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.delete("/api/logs/{log_id}")
async def delete_log(log_id: int):
    """
    删除特定的请求日志。
    """
    log = await RequestLog.get_or_none(id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    await log.delete()
    return {"status": "success", "message": f"Log {log_id} deleted"}


@router.delete("/api/logs")
async def clear_logs(
    provider: Optional[str] = None,
    before_timestamp: Optional[str] = None,
):
    """
    批量删除日志，支持按提供商或时间筛选。
    """
    query = RequestLog.all()
    if provider:
        query = query.filter(provider=provider)
    if before_timestamp:
        query = query.filter(timestamp__lt=before_timestamp)

    count = await query.count()
    await query.delete()
    return {"status": "success", "deleted_count": count}


@router.get("/api/stats")
async def get_stats():
    """
    获取全局统计信息，包括总请求数和已配置的提供商信息。
    """
    # 总请求数
    total_requests = await RequestLog.all().count()

    # 按提供商统计
    provider_stats = (
        await RequestLog.all()
        .annotate(count=Count("id"))
        .group_by("provider")
        .values("provider", "count")
    )

    # 按模型统计
    model_stats = (
        await RequestLog.all()
        .annotate(count=Count("id"))
        .group_by("model")
        .values("model", "count")
    )

    stats = {
        "total_requests": total_requests,
        "provider_counts": {item["provider"]: item["count"] for item in provider_stats},
        "model_counts": {item["model"]: item["count"] for item in model_stats},
        "providers_config": {},
    }

    # 遍历配置中的提供商
    for name, config in settings.providers.items():
        stats["providers_config"][name] = {
            "type": config.type,
        }

    return stats


@router.get("/api/providers")
async def get_providers():
    """
    获取当前系统配置的所有提供商详情。
    """
    return settings.providers


@router.get("/api/health")
async def health_check():
    """
    检查所有配置的提供商连接状态。
    """
    from ..providers.factory import ProviderFactory

    health = {}
    for name in settings.providers.keys():
        try:
            # 尝试获取提供商实例并调用 list_models 作为简单的存活检查
            provider = ProviderFactory.get_provider(name)
            await provider.list_models()
            health[name] = "healthy"
        except Exception as e:
            health[name] = f"unhealthy: {str(e)}"

    return {"status": "online", "providers": health}


@router.get("/api/config")
async def get_config():
    """
    获取当前配置信息 (脱敏)。
    """
    config_data = settings.model_dump()
    # 脱敏处理：隐藏 API Key
    if "providers" in config_data:
        for provider in config_data["providers"].values():
            if "api_key" in provider and provider["api_key"]:
                key = provider["api_key"]
                if len(key) > 8:
                    provider["api_key"] = f"{key[:4]}...{key[-4:]}"
                else:
                    provider["api_key"] = "****"
    return config_data


@router.post("/api/config")
async def update_config(new_config: dict):
    """
    更新配置信息。
    支持处理脱敏过的 API Key。
    """
    from ..config import save_config, Settings

    current_config = settings.model_dump()

    # 处理提供商配置
    if "providers" in new_config:
        for name, provider in new_config["providers"].items():
            # 如果新配置中的 API Key 是脱敏形式，则保留原有 Key
            if "api_key" in provider:
                val = provider["api_key"]
                if val == "****" or (val and "..." in val and len(val) >= 11):
                    if (
                        name in current_config["providers"]
                        and "api_key" in current_config["providers"][name]
                    ):
                        provider["api_key"] = current_config["providers"][name][
                            "api_key"
                        ]

    # 更新全局设置对象
    try:
        updated_settings = Settings(**new_config)
        # 更新内存中的设置
        settings.debug = updated_settings.debug
        settings.database_url = updated_settings.database_url
        settings.media_dir = updated_settings.media_dir
        settings.providers = updated_settings.providers

        # 保存到文件
        save_config(settings)
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")


@router.get("/api/models")
async def list_all_models():
    """
    获取所有配置提供商支持的模型列表。
    """
    from ..providers.factory import ProviderFactory

    all_models = {}
    for name in settings.providers.keys():
        try:
            provider = ProviderFactory.get_provider(name)
            models = await provider.list_models()
            all_models[name] = models
        except Exception as e:
            all_models[name] = {"error": str(e)}

    return all_models

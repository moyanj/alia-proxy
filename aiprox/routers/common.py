from fastapi import APIRouter
from ..models import RequestLog
from ..config import settings
from tortoise.functions import Count

router = APIRouter()


@router.get("/")
async def read_root():
    """
    根路径，用于健康检查。
    """
    return {"app": "AI Proxy Service"}


@router.get("/api/logs")
async def get_logs(limit: int = 100):
    """
    获取最近的请求日志列表。
    """
    return await RequestLog.all().order_by("-timestamp").limit(limit)


@router.get("/api/stats")
async def get_stats():
    """
    获取全局统计信息，包括总请求数和已配置的提供商信息。
    """
    # 使用聚合查询提高效率
    res = (
        await RequestLog.all()
        .annotate(total_requests=Count("id"))
        .values("total_requests")
    )

    aggregation = res[0] if res else {"total_requests": 0}

    stats = {
        "total_requests": aggregation["total_requests"] or 0,
        "providers": {},
    }

    # 遍历配置中的提供商
    for name, config in settings.providers.items():
        stats["providers"][name] = {
            "type": config.type,
        }

    return stats


@router.get("/api/providers")
async def get_providers():
    """
    获取当前系统配置的所有提供商详情。
    """
    return settings.providers

import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from ..providers.base import ChatRequest, EmbeddingsRequest
from .deps import get_proxy_service
from ..services.proxy import ProxyService
from ..config import settings
from ..providers.factory import ProviderFactory
import time
import asyncio

router = APIRouter()

# 模型列表缓存，避免频繁调用各提供商 API
MODELS_CACHE = {}
CACHE_TTL = 3600  # 缓存有效期 (秒)


@router.get("/v1/models")
async def list_models():
    """
    列出所有已配置提供商支持的模型。
    支持缓存机制，并将模型 ID 转换为 <provider>/<model> 格式。
    """
    all_models = []
    current_time = time.time()

    tasks = []
    instance_names = list(settings.providers.keys())

    for name in instance_names:
        # 检查缓存是否有效
        if name in MODELS_CACHE:
            ts, models = MODELS_CACHE[name]
            if current_time - ts < CACHE_TTL:
                for m in models:
                    m_copy = m.copy()
                    m_copy["id"] = f"{name}/{m['id']}"
                    all_models.append(m_copy)
                continue

        # 缓存失效或不存在，准备异步请求提供商
        try:
            provider = ProviderFactory.get_provider(name)
            tasks.append((name, provider.list_models()))
        except Exception:
            print(traceback.format_exc())
            # 某个提供商配置错误或宕机，跳过
            continue

    if tasks:
        # 并发获取各提供商的模型列表
        results = await asyncio.gather(*(t[1] for t in tasks), return_exceptions=True)
        for i, result in enumerate(results):
            name = tasks[i][0]
            print(f"{name}: {result}")

            if isinstance(result, list):
                # 更新缓存
                MODELS_CACHE[name] = (current_time, result)
                for m in result:
                    if isinstance(m, dict) and "id" in m:
                        m_copy = m.copy()
                        m_copy["id"] = f"{name}/{m['id']}"
                        all_models.append(m_copy)

            else:
                # 请求失败，回退到过期缓存 (如果有)
                if name in MODELS_CACHE:
                    _, cached_models = MODELS_CACHE[name]
                    if isinstance(cached_models, list):
                        for m in cached_models:
                            if isinstance(m, dict) and "id" in m:
                                m_copy = m.copy()
                                m_copy["id"] = f"{name}/{m['id']}"
                                all_models.append(m_copy)

    # 添加配置中的映射模型 (from settings.mapping)
    for alias in settings.mapping.keys():
        all_models.append(
            {
                "id": alias,
                "object": "model",
                "created": int(current_time),
                "owned_by": "system-mapping",
                "permission": [],
                "root": alias,
                "parent": None,
            }
        )

    return {"object": "list", "data": all_models}


@router.get("/v1/models/cache/clear")
async def clear_models_cache():
    """
    清除模型列表缓存。
    """
    MODELS_CACHE.clear()
    return {"detail": "Models cache cleared"}


@router.post("/v1/images/generations")
async def image_generations(
    request: Request, proxy: ProxyService = Depends(get_proxy_service)
):
    """
    OpenAI 兼容的图像生成接口。
    """
    body = await request.json()
    response = await proxy.image_gen(body.get("prompt"))
    return response


@router.post("/v1/audio/speech")
async def audio_speech(
    request: Request, proxy: ProxyService = Depends(get_proxy_service)
):
    """
    OpenAI 兼容的文本转语音 (TTS) 接口。
    """
    body = await request.json()
    voice = body.get("voice")
    if not voice:
        raise HTTPException(status_code=400, detail="Missing 'voice' field")
    content, filename = await proxy.text_to_speech(body.get("input"), voice)
    return StreamingResponse(iter([content]), media_type="audio/mpeg")


@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request, proxy: ProxyService = Depends(get_proxy_service)
):
    """
    OpenAI 兼容的聊天完成接口。
    支持流式 (Server-Sent Events) 和非流式响应。
    """
    body = await request.json()
    body["model"] = proxy.model  # 使用解析后的实际模型名

    try:
        chat_request = ChatRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if chat_request.stream:
        return StreamingResponse(
            proxy.chat_stream(chat_request), media_type="text/event-stream"
        )
    else:
        return await proxy.chat(chat_request)


@router.post("/v1/embeddings")
async def embeddings(
    request: Request, proxy: ProxyService = Depends(get_proxy_service)
):
    """
    OpenAI 兼容的嵌入生成接口。
    """
    body = await request.json()
    body["model"] = proxy.model  # 使用解析后的实际模型名

    try:
        emb_request = EmbeddingsRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return await proxy.embeddings(emb_request)

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from .deps import get_proxy_service
from ..services.proxy import ProxyService

router = APIRouter()


@router.post("/v1/messages")
async def messages(request: Request, proxy: ProxyService = Depends(get_proxy_service)):
    """
    Anthropic 原生消息接口。
    """
    body = await request.json()

    try:
        response = await proxy.anthropic_chat(body)
        if body.get("stream"):
            return StreamingResponse(response, media_type="text/event-stream")
        else:
            return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import HTTPException, Request
from ..providers.factory import ProviderFactory
from ..services.proxy import ProxyService


async def get_proxy_service(request: Request) -> ProxyService:
    """
    解析请求体中的模型字段，并返回初始化好的 ProxyService 实例。
    期望模型字段格式为: <provider_instance>/<model_name>
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_field = body.get("model")
    if not model_field:
        raise HTTPException(status_code=400, detail="Missing 'model' field")

    # 获取请求者的 IP 地址
    request_ip = request.client.host if request.client else ""

    try:
        # 解析提供商实例名和实际模型名
        instance_name, actual_model = ProviderFactory.resolve_model(model_field)
        # 获取提供商对象
        provider = ProviderFactory.get_provider(instance_name)
        # 返回封装好的代理服务
        return ProxyService(
            provider, actual_model, instance_name, request_ip=request_ip
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

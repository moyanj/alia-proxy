from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from .routers import openai, media, export, common, anthropic
from .config import settings
from .providers.factory import ProviderFactory


async def config_watcher():
    """
    配置文件的热重载监听器。
    """
    config_path = "config.toml"
    if not os.path.exists(config_path):
        return

    last_mtime = os.path.getmtime(config_path)
    while True:
        await asyncio.sleep(5)  # 每 5 秒检查一次
        if not settings.hot_reload:
            continue

        try:
            current_mtime = os.path.getmtime(config_path)
            if current_mtime > last_mtime:
                print(f"检测到配置更改，正在重新加载 {config_path}...")
                settings.reload(config_path)
                ProviderFactory.clear_cache()
                last_mtime = current_mtime
                print("配置重载完成。")
        except Exception as e:
            print(f"配置重载失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动配置监听任务
    watcher_task = asyncio.create_task(config_watcher())

    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["aiprox.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    watcher_task.cancel()
    await Tortoise.close_connections()


app = FastAPI(
    title="AI Proxy Service",
    description="支持多提供商的统一 AI API 代理服务",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 FastAPI 内部抛出的 HTTPException。
    将其格式化为符合 OpenAI API 标准的错误响应。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "invalid_request_error",
                "param": None,
                "code": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证错误。
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": str(exc),
                "type": "invalid_request_error",
                "param": None,
                "code": None,
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    捕获应用运行时的所有未处理异常。
    返回 500 内部错误响应。
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": str(exc),
                "type": "internal_error",
                "param": None,
                "code": None,
            }
        },
    )


app.include_router(openai.router)
app.include_router(anthropic.router)
app.include_router(media.router)
app.include_router(export.router)
app.include_router(common.router)


# 挂载前端静态文件 (如果存在)
frontend_path = os.path.join(os.getcwd(), "frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

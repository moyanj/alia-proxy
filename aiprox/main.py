from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from tortoise import Tortoise
from .routers import openai, media, export, common
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["aiprox.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


app = FastAPI(
    title="AI Proxy Service",
    description="支持多提供商的统一 AI API 代理服务",
    version="0.1.0",
    lifespan=lifespan,
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
app.include_router(media.router)
app.include_router(export.router)
app.include_router(common.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

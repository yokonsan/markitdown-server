from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger


from backend.app.core.config import (
    APP_NAME,
    DEBUG,
    HOST,
    PORT,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    MINIO_ENDPOINT,
    REDIS_URL
)
from backend.app.api.v1.md_conv.async_routes import router as async_router


@asynccontextmanager
async def register_init(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    启动初始化

    :param app: FastAPI 应用实例
    :return:
    """
    logger.info("启动Markdown转换服务...")
    logger.info(f"MinIO endpoint: {MINIO_ENDPOINT}")
    logger.info(f"Redis URL: {REDIS_URL}")
    logger.success("服务启动完成")

    yield

    logger.info("停止Markdown转换服务...")
    logger.success("服务停止完成")

app = FastAPI(
    title=APP_NAME,
    description="基于FastAPI和MarkItDown的文件转换服务，支持异步处理",
    version="2.0.0",
    openapi_tags=[
        {"name": "Markdown转换", "description": "同步转换接口"},
        {"name": "异步转换", "description": "基于MinIO和Celery的异步转换接口"},
    ],
    lifespan=register_init,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# 注册路由
# app.include_router(md_conv_router, prefix="/api/v1")
app.include_router(async_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Markdown转换服务API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": ["同步转换", "异步转换", "MinIO存储", "Celery任务队列"]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "markdown-converter-v2"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
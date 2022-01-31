"""
Main FastAPI app instance declaration
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings, redis as redis_conf
from app.utils import RedisClient

log = logging.getLogger("uvicorn.error")


async def on_startup():
    """Fastapi startup event handler.

    Creates RedisClient session.

    """
    # Initialize utilities for whole FastAPI application without passing object
    await RedisClient.open_redis_client()

    # Try to ping, if failed. Retry after sometime
    if not await RedisClient.ping():
        log.error("Could not connect to Redis ... Retrying ...")
    log.debug("Connected to Redis Storage")


async def on_shutdown():
    """Fastapi shutdown event handler.

    Destroys RedisClient and AiohttpClient session.

    """
    log.debug("Execute FastAPI shutdown event handler.")

    # Gracefully close utilities.
    await RedisClient.close_redis_client()

    log.debug("All utilities have been gracefully closed.")


app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url="/openapi.json",
        docs_url="/",
        debug=settings.DEBUG,
        on_shutdown=[on_shutdown],
        on_startup=[on_startup],
    )

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

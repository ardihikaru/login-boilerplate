"""
Main FastAPI app instance declaration
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api import api_router
from app.webapps.base import api_router as web_app_router
from app.core.config import settings, redis as redis_conf
from app.utils import RedisClient
from fastapi.staticfiles import StaticFiles

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
	openapi_url="/api/v1/openapi.json",
	docs_url="/api/v1/docs",
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

# Include routers
app.include_router(api_router)
app.include_router(web_app_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


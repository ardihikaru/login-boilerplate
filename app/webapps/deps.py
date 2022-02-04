from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models.user import User
from app.db.session import async_session

templates = Jinja2Templates(directory="app/templates")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	""" Create database session

	:return:
	"""
	async with async_session() as session:
		yield session


async def get_current_session(request: Request) -> Optional[dict]:
	""" Try to get the logged in user

	:param request:
	:return: Optional[dict]
	"""
	user = request.session.get('user')
	if user is not None:
		return user
	else:
		return None

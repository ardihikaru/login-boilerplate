from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.models.user import User
from app.db.session import async_session
from app.db.adapters.user.user import update_session_login

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


async def save_session(user: User, request: Request, session: AsyncSession) -> None:
	""" Save current valid user information into the session

	:param user:
	:param request:
	:return: None
	"""

	# Set new session for this user
	request.session['user'] = {
		"email": user.email,
		"full_name": user.full_name,
	}

	# Update total login and last active session
	await update_session_login(user, session)

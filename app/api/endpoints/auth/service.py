from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.models.user import User
from app.utils import RedisClient
from datetime import datetime

L = logging.getLogger("uvicorn.error")


async def validate_user(
    session: AsyncSession, form_data: OAuth2PasswordRequestForm
) -> User:
	result = await session.execute(select(User).where(User.email == form_data.username))
	user: Optional[User] = result.scalars().first()
	if user is None:
		raise HTTPException(status_code=400, detail="Incorrect email or password")

	if not security.verify_password(form_data.password, user.hashed_password):  # type: ignore
		raise HTTPException(status_code=400, detail="Incorrect email or password")

	return user

async def update_login_counter(
    session: AsyncSession, user: User
) -> User:
	""" Update login counter for each successful login """

	# since login success, log the total number of logins (`total_login`)
	if user.total_login is None:
		user.total_login = 1
	else:
		user.total_login += 1
		user.session_at = datetime.utcnow()

	session.add(user)
	await session.commit()
	await session.refresh(user)

	return user

async def store_tokens(
    access_token: str,
	refresh_token: str,
) -> None:
	# store the information into redis storage
	ac_exp_in_secs = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
	await RedisClient.set(access_token, refresh_token, ac_exp_in_secs)
	rc_exp_in_secs = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
	await RedisClient.set(refresh_token, access_token, rc_exp_in_secs)

async def revoke_tokens(
    access_token: str,
) -> None:
	# first, get refresh token from the provided access_token
	refresh_token = await RedisClient.get(access_token)

	# revoke access_token -> Delete from redis
	await RedisClient.delete(access_token)

	# revoke refresh_token -> Delete from redis
	await RedisClient.delete(refresh_token)


async def valid_refresh_token(refresh_token: str) -> bool:
	# # TODO: Fix unittest for RedisCache
	# if settings.ENVIRONMENT != "PYTEST":
	# 	if await RedisClient.get(refresh_token) is None:
	# 		return False

	if await RedisClient.get(refresh_token) is None:
		return False

	return True

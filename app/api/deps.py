from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas
from app.core import security
from app.core.config import settings
from app.db.models.user import User
from app.db.session import async_session
from app.utils import RedisClient

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_token(
    token: str = Depends(reusable_oauth2)
) -> str:

    return token

async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(reusable_oauth2)
) -> User:
    # validate token first!
    if await token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your token have been revoked",
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    result = await session.execute(select(User).where(User.id == token_data.sub))
    user: Optional[User] = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def token_revoked(access_token: str) -> bool:
    if await RedisClient.get(access_token) is None:
        return True

    return False

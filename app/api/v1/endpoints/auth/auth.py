from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.models.user import User
from app.api.v1.endpoints.auth.service import (
    validate_user, update_login_counter, store_tokens, revoke_tokens, valid_refresh_token
)

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    session: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token, get an access token for future requests using username and password
    """

    # first, validate the input
    user = await validate_user(session, form_data)

    # once validated, update the login counter
    user = await update_login_counter(session, user)

    # finally, generate access token adn refresh token for this user, and store to redis storage
    access_token, expire_at = security.create_access_token(user.id)
    refresh_token, refresh_expire_at = security.create_refresh_token(user.id)
    await store_tokens(access_token, refresh_token)

    return {
        "token_type": "bearer",
        "access_token": access_token,
        "expire_at": expire_at,
        "refresh_token": refresh_token,
        "refresh_expire_at": refresh_expire_at,
    }


@router.get("/logout", response_model=schemas.UserLogout)
async def logout_access_token(
    current_user: User = Depends(deps.get_current_user),
    access_token = Depends(deps.get_current_token),
):
    """
        Revoke the currently active access token
    """

    # revoke this current user
    await revoke_tokens(access_token)

    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "logout_status": True,
    }


@router.post("/refresh-token", response_model=schemas.Token)
async def refresh_token(
    input: schemas.TokenRefresh,
    session: AsyncSession = Depends(deps.get_session),
):
    """
    OAuth2 compatible token, get an access token for future requests using refresh token
    """
    # validate if the refresh token valid or not
    if not await valid_refresh_token(input.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalidated/Invalid refresh token",
        )

    try:
        payload = jwt.decode(
            input.refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if not token_data.refresh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    result = await session.execute(select(User).where(User.id == token_data.sub))
    user: Optional[User] = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_token, expire_at = security.create_access_token(user.id)
    refresh_token, refresh_expire_at = security.create_refresh_token(user.id)
    return {
        "token_type": "bearer",
        "access_token": access_token,
        "expire_at": expire_at,
        "refresh_token": refresh_token,
        "refresh_expire_at": refresh_expire_at,
    }

from fastapi import (
    APIRouter, Depends
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import schemas
from app.db.models import user as models
from app.api import deps
from app.api.v1.endpoints.users.service import insert, get_all_users
from app.core.security import get_password_hash
from starlette.responses import RedirectResponse
from app.exceptions import ErrorMessage
import httpx

router = APIRouter()


@router.get("", response_model=schemas.UserAll)
async def read_user_me(
    _: models.User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
    query_data: schemas.QueryParams = Depends(schemas.query_params),  # read URL query to get [activated] value
):
    """
    Get current user.
    """

    # await get_all_users(session)
    users = await get_all_users(session, query_data.activated, query_data.signup_by)

    return {
        "total": len(users),
        "data": users,
    }


@router.post("", response_model=schemas.User)
async def create_user(
    user_create: schemas.UserCreate,
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Create new user. Only for logged users.
    """
    hashed_password = get_password_hash(user_create.password)
    new_user = models.User(
        email=user_create.email, hashed_password=hashed_password, full_name=user_create.full_name
    )

    # try to insert; return an exception if failed
    await insert(new_user, session)

    return new_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_update: schemas.UserUpdate,
    session: AsyncSession = Depends(deps.get_session),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Update current user.
    """
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)  # type: ignore
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name  # type: ignore
    if user_update.email is not None:
        current_user.email = user_update.email  # type: ignore

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get current user.
    """
    return current_user

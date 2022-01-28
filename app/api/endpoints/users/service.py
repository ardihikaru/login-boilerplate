from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models import User
from sqlalchemy.exc import IntegrityError
from app.core.utils import get_pgsql_integrity_error_msg
from app.exceptions import ErrorMessage
import logging

L = logging.getLogger("uvicorn.error")


async def insert(
    user: User,
    session: AsyncSession = Depends(deps.get_session),
):
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=await get_pgsql_integrity_error_msg(err),
        )
    except Exception as err:
        L.error(f"[{ErrorMessage.UNKNOWN_ERROR.value}] {str(err)}")  # print detailed error in the console

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessage.UNKNOWN_ERROR.value,
        )

from typing import List, Mapping
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from sqlalchemy.exc import IntegrityError
from app.core.utils import get_pgsql_integrity_error_msg
from app.exceptions import ErrorMessage
from sqlalchemy import select, func
from sqlalchemy.sql import text
import logging

L = logging.getLogger("uvicorn.error")


async def insert(
    user: User,
    session: AsyncSession,
) -> None:
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

async def build_where_by(activated: bool, signup_by: str) -> str:
    where_by = "1 = 1"

    if activated is not None:
        opt = "NOT" if not activated else ""
        where_by += f" and activated IS {opt} TRUE"

    if signup_by is not None:
        where_by += f" and signup_by = '{signup_by}'"

    return where_by


async def get_all_users(
    session: AsyncSession, activated: bool, signup_by: str
) -> List[Mapping]:
    # build where_by
    where_by = await build_where_by(activated, signup_by)

    result = await session.execute(text(f"SELECT * FROM public.user WHERE {where_by}"))
    results_as_dict = result.mappings().all()
    return results_as_dict

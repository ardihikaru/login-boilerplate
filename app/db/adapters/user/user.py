from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.utils import get_pgsql_integrity_error_msg
from app.exceptions import ErrorMessage
from datetime import datetime


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
	result = await session.execute(select(User).where(User.email == email))
	user: Optional[User] = result.scalars().first()

	return user


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


async def update_activation_status(
		user: User,
		session: AsyncSession,
		activated: bool
) -> None:
	user.activated = activated
	await session.commit()
	await session.refresh(user)


async def get_all_users(session: AsyncSession) -> Optional[List]:
	result = await session.execute(select(User))
	users: Optional[List] = result.scalars().all()

	return users


async def update_session_login(
		user: User,
		session: AsyncSession,
) -> None:
	user.total_login += 1  # update total login
	user.session_at = datetime.utcnow()

	await session.commit()
	await session.refresh(user)

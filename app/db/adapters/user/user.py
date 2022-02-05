from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from typing import Optional, List, Mapping
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.utils import get_pgsql_integrity_error_msg
from app.exceptions import ErrorMessage
from datetime import datetime, timedelta, date
from sqlalchemy.sql import text


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


async def get_users(
		session: AsyncSession,
		limit: Optional[int] = None,
		order_desc: Optional[bool] = False
) -> List[Mapping]:
	""" Get all user data in the database

	:param session:
	:param limit:
	:return:
	"""
	# initial query
	query = "SELECT full_name, email, signup_by, total_login, session_at, created_at, activated " \
			"FROM public.user "

	# add limit if any
	if limit is not None:
		query += f" LIMIT {limit}"

	if order_desc:
		query += " ORDER BY created_at DESC"

	# get the results
	result = await session.execute(text(query))
	results_as_dict = result.mappings().all()
	return results_as_dict


async def update_session_login(
		user: User,
		session: AsyncSession,
) -> None:
	user.total_login += 1  # update total login
	user.session_at = datetime.utcnow()

	await session.commit()
	await session.refresh(user)


async def get_session_today(
		session: AsyncSession,
) -> List[Mapping]:
	query = "SELECT full_name, email, signup_by, total_login, session_at, created_at, activated " \
			"FROM public.user " \
			"WHERE DATE(session_at) = DATE(NOW()) " \

	result = await session.execute(text(query))
	results_as_dict = result.mappings().all()
	return results_as_dict


async def get_sessions_last_7days(
		session: AsyncSession,
) -> List[Mapping]:

	# get today and last 7 days
	today = date.today()
	week_ago = today - timedelta(days=6)

	# build a virtual table with 7 days backwards
	vtable_7d = f"SELECT day::date as date " \
				f"FROM generate_series('{str(week_ago)}', '{str(today)}', INTERVAL '1 day') day"

	# build a virtual table to count total sessions each day
	vtable_session = "SELECT DATE(session_at) date, COUNT(DATE(session_at)) as total " \
			"FROM public.user " \
			"GROUP BY DATE(session_at) "

	# (LEFT) JOIN `vtable_7d` table with `session_vtable` table, and set default value as 0 IFNULL
	query = f"SELECT d.date, COALESCE(u.total, 0) as total " \
			f"FROM ({vtable_7d}) as d LEFT JOIN ({vtable_session}) as u ON d.date = u.date " \

	result = await session.execute(text(query))
	results_as_dict = result.mappings().all()
	return results_as_dict


async def get_unverified_users(
		session: AsyncSession,
		month: int,
) -> List[Mapping]:
	""" Get unverified user filtered by month

	:param session:
	:param month:
	:return:
	"""
	# initial query
	# https://www.postgresql.org/docs/8.0/functions-datetime.html
	query = "SELECT full_name, email, signup_by, total_login, session_at, created_at, activated " \
			"FROM public.user " \
			f"WHERE activated is false AND cast(date_part('month', created_at) as int) = {month}"

	# get the results
	result = await session.execute(text(query))
	results_as_dict = result.mappings().all()
	return results_as_dict


async def update_current_password(
		session: AsyncSession,
		user: User,
		new_password: str
) -> None:
	user.hashed_password = new_password
	await session.commit()
	await session.refresh(user)

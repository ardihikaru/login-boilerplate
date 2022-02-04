from sqlalchemy.ext.asyncio import AsyncSession
from app.db.adapters.user.user import get_user_by_email
from typing import Optional
from app.db.models import user as models
from app.db.models.user import User, SignupBy
from app.db.adapters.user.user import insert, update_current_password
from app.utils.password_validator import PasswordValidator
from app.core.security import get_password_hash, verify_password
import logging

L = logging.getLogger("uvicorn.error")


async def get_user(session: AsyncSession, email: str) -> Optional[User]:
	""" Get one user record by a given mail

	:param session:
	:param email:
	:return:
	"""
	# get record by email
	return await get_user_by_email(session, email)


async def validate_ch_passwd(user: User, pass_old: str, pass_new: str, pass_new_again: str) -> Optional[str]:
	""" Validate Change password data

	:param session:
	:param pass_old:
	:param pass_new:
	:param pass_new_again:
	:return:
	"""
	# if user register NOT by EMAIL, reject
	if user.signup_by != SignupBy.EMAIL.value:
		return f"You cannot change the password when you registered with {user.signup_by}."

	# if old password did not match
	if not verify_password(pass_old, user.hashed_password):
		return "Incorrect old password."

	# validate NEW password quality
	passwd_validator = PasswordValidator(pass_new)
	err_msg = await passwd_validator.validate_and_wait()

	# if error msg exists, means that there is an error
	if err_msg is not None:
		return err_msg

	# make sure that new password again has the same value
	if pass_new !=  pass_new_again:
		return "New password did not match"

	# otherwise, everything is OK.
	return None


async def update_password(session: AsyncSession, user: User, new_password: str) -> None:
	# hash password
	hash_password = get_password_hash(new_password)

	await update_current_password(session, user, hash_password)



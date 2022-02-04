from sqlalchemy.ext.asyncio import AsyncSession
from app.db.adapters.user.user import get_user_by_email, update_activation_status
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Optional
from app.db.models.user import SignupBy, User
from app.core.security import verify_password, create_email_verification_token
import logging
from app.utils.common import get_root_url

L = logging.getLogger("uvicorn.error")

templates = Jinja2Templates(directory="app/templates")


async def get_user(session: AsyncSession, email: str) -> Optional[User]:
	""" Get one user record by a given mail

	:param session:
	:param email:
	:return:
	"""
	# get record by email
	return await get_user_by_email(session, email)


async def validate_login(user: User, password: str, request: Request) -> (str, str):
	""" Validate login data

	:param user:
	:param password:
	:param request:
	:return:
	"""
	# if record not found, returns user not found error
	if user is None:
		err_msg = "User not found."
		return (err_msg, None)

	# if record found but is inactive, sends error message and generate a new email verification link to be used
	if not user.activated:
		err_msg = "You account is currently inactive."
		evlink = await generate_email_verification_request_uri(request, user.email)
		return (err_msg, evlink)

	# if record exist but user was registering by using FACEBOOK or GOOGLE,
	# inform the user to use that social login instead
	if user.activated and user.signup_by != SignupBy.EMAIL.value:
		err_msg = f"You signed by {user.signup_by}. Please use that social login instead."
		return (err_msg, None)

	# finally, check if password match? if not, inform that password is incorrect
	if not verify_password(password, user.hashed_password):
		err_msg = "Incorrect password."
		return (err_msg, None)

	# otherwise, everything is OK.
	return None, None


async def generate_email_verification_request_uri(request: Request, email: str) -> str:
	""" Generate email verification request URI to be used by the user to trigger composing and sending en email to them,
		asking to verify their account

	:param request:
	:param email:
	:return:
	"""
	# get root uri for email verification
	root_url = get_root_url(request.url._url)
	verification_root_uri = f"{root_url}/verification-request"  # Function request_verification_email()

	# build email verification link
	email_ver_request_link = "{}/{}".format(
		verification_root_uri, email
	)

	L.info(f"Email Verification Request Link={email_ver_request_link}")

	return email_ver_request_link


async def generate_email_verification_uri(request: Request, email: str) -> str:
	""" Generate email verification URI used as part of the contents on the posted email. Once the link clicked
		through the email, it will first validate the given token. It may resulted an invalid token, expired token, or
		a valid token.

	:param request:
	:param email:
	:return:
	"""
	# create token
	token, _ = create_email_verification_token(email)

	# get root uri for email verification
	verification_uri = request.url_for('verify_email')

	# build email verification link
	email_ver_link = "{}?l={}".format(
		verification_uri, token
	)

	L.info(f"Email Verification URL={email_ver_link}")

	return email_ver_link


async def activate_account(session: AsyncSession, email: str):
	""" Activate user account and enable the activated user to login into the system

	:param session:
	:param email:
	:return:
	"""
	# get user by email
	user = await get_user_by_email(session, email)

	await update_activation_status(user, session, True)

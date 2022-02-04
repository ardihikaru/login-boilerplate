from sqlalchemy.ext.asyncio import AsyncSession
from app.db.adapters.user.user import get_user_by_email, update_activation_status
from app.webapps.user.service import get_user
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Optional
from app.db.models import user as models
from app.db.models.user import SignupBy, User
from app.db.adapters.user.user import insert
from app.core.security import verify_password, create_email_verification_token
from app.db.adapters.user.user import update_session_login
from app.utils.common import get_root_url
from app.utils.password_validator import PasswordValidator
from app.core.security import get_password_hash
import logging

L = logging.getLogger("uvicorn.error")

templates = Jinja2Templates(directory="app/templates")


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


async def validate_signup(user: User, password: str) -> Optional[str]:
	""" Validate signup data

	:param user:
	:param password:
	:return:
	"""
	# if record found, reject
	if user is not None:
		return "This email has been registered into our system."

	# validate password quality
	passwd_validator = PasswordValidator(password)
	err_msg = await passwd_validator.validate_and_wait()

	# if error msg exists, means that there is an error
	if err_msg is not None:
		return err_msg

	# otherwise, everything is OK.
	return None


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


async def save_new_user(session: AsyncSession, full_name: str, email: str, password: str) -> None:
	""" Activate user account and enable the activated user to login into the system

	:param session:
	:param full_name:
	:param email:
	:param password:
	:return:
	"""
	# hash password
	hashed_password = get_password_hash(password)

	# build user model
	new_user = models.User(
		full_name=full_name, email=email, hashed_password=hashed_password
	)

	# insert to db
	await insert(new_user, session)


async def save_and_load_user(session: AsyncSession, email: str, full_name: str,
							 social_login_id: str, signup_by: str) -> User:
	# get user by email
	user = await get_user(session, email)

	# if not found, create user whis this credentials
	if user is None:
		# create a hash password
		hashed_password = get_password_hash(social_login_id)  # use this social login ID as a password

		# build user model
		new_user = models.User(
			full_name=full_name, email=email, hashed_password=hashed_password, signup_by=signup_by
		)

		# insert to db
		await insert(new_user, session)

		# return a newly updated user information
		return new_user

	return user

async def save_session_and_wait(user: User, request: Request, session: AsyncSession) -> None:
	""" Save current valid user information into the session

	:param user:
	:param request:
	:return: None
	"""

	# Set new session for this user
	request.session['user'] = {
		"email": user.email,
		"full_name": user.full_name,
	}

	# Update total login and last active session
	await update_session_login(user, session)

from typing import Optional
from fastapi import Request, APIRouter, Depends, Form, status
from fastapi.templating import Jinja2Templates
from app.db import schemas
from app.webapps import deps
from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.webapps.auth.service import (
	validate_login, get_user, generate_email_verification_request_uri, activate_account,
	generate_email_verification_uri
)
from app.core.security import get_email_by_verification_token
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/login")
async def login_web(
		request: Request,
		current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
):
	""" Open login page if there is no session, or be forwarded into dashboard page if a session found

	:param request:
	:param current_session:
	:return:
	"""
	# if session exist, forward to dashboard page
	if current_session is not None:
		redirect_uri = request.url_for('dashboard')
		return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

	# otherwise, allow user to open login page
	return templates.TemplateResponse("auth/login.html", context={"request": request})


@router.post("/login")
async def login_web_post(
		request: Request,
		email: str = Form(...),
		password: str = Form(...),
		session: AsyncSession = Depends(deps.get_session),

):
	""" Process login data from user request

	:param request:
	:param email:
	:param password:
	:param session:
	:return:
	"""
	# get user by email
	user = await get_user(session, email)

	# validate login input
	# may get error message only or with a link to trigger email validation sending
	err_msg, evlink = await validate_login(user, password, request)

	# if invalid, send an error to the login page
	if err_msg is not None:
		return templates.TemplateResponse("auth/login.html", context={"request": request, "err_msg": err_msg, "evlink": evlink})

	# if there is no issue, save the session
	await deps.save_session(user, request, session)

	# redirect to the dashboard
	redirect_uri = request.url_for('dashboard')
	return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)


@router.get("/verification-request/{email}")
async def request_verification_email(
		request: Request, email: str,
		session: AsyncSession = Depends(deps.get_session),
):
	""" Request system to send an email validation link via user's email

	:param request:
	:param email:
	:return:
	"""
	# get user by email
	user = await get_user(session, email)

	# if user does not exists, send an error message
	if user is None:
		err_msg = "User not found."
		return templates.TemplateResponse("auth/login.html",
									  context={"request": request, "err_msg": err_msg, "evlink": None})

	# if user exist, inform a link to verify
	success_msg = "You verification email has been send to your email."
	email_ver_link = await generate_email_verification_uri(request, user.email)

	# TODO: Compose an email via Email Publisher Service

	return templates.TemplateResponse("auth/login.html", context={"request": request, "success_msg": success_msg})

@router.get("/verify")
async def verify_email(
		request: Request,
		query_params: schemas.UserSignupQuery = Depends(schemas.q_signup),  # read URL query to get [activated] value
		session: AsyncSession = Depends(deps.get_session),
):
	""" Verify a given email verification token

	:param request:
	:param query_params:
	:param session:
	:return:
	"""
	token = query_params.email_verification_token

	# validate token expiration time
	valid, email = get_email_by_verification_token(token)

	# expired yet valid token
	if not valid and email is not None:
		err_msg = "Your email verification link has been expired. Please re-send again."
		evlink = await generate_email_verification_request_uri(request, email)
		return templates.TemplateResponse("auth/login.html", context={"request": request, "err_msg": err_msg,
																	  "evlink": evlink})

	# if expired, return none
	if email is None:
		err_msg = "Invalid email verification link."
		return templates.TemplateResponse("auth/login.html", context={"request": request, "err_msg": err_msg})

	# verification success!
	success_msg = "Email verification success! You may login now."

	# update active status from False to True!
	await activate_account(session, email)

	return templates.TemplateResponse("auth/login.html", context={"request": request, "success_msg": success_msg})


@router.get("/logout", response_model=schemas.UserLogout)
async def logout_web(
		request: Request,
		current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
):
	""" Revoke the currently active session

	:param request:
	:param current_session:
	:return:
	"""

	# revoke this current user if exists
	if current_session is not None:
		request.session.pop('user', None)

	redirect_uri = request.url_for('dashboard')
	return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

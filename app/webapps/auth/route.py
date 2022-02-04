from typing import Optional
from fastapi import Request, APIRouter, Depends, Form, status
from fastapi.templating import Jinja2Templates
from app.db import schemas
from app.webapps import deps
from app.db.models.user import User, SignupBy
from sqlalchemy.ext.asyncio import AsyncSession
from app.webapps.auth.service import (
	validate_login, get_user, generate_email_verification_request_uri, activate_account,
	generate_email_verification_uri, validate_signup, save_new_user, save_session_and_wait,
	save_and_load_user
)
from app.core.security import get_email_by_verification_token
from starlette.responses import RedirectResponse
from app.utils.common import get_root_url
from app.utils.social_login.facebook import FacebookLogin
from app.utils.social_login.google import GoogleLogin
from app.core.config import settings
import logging

L = logging.getLogger("uvicorn.error")

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
		return templates.TemplateResponse("auth/login.html",
										  context={"request": request, "err_msg": err_msg, "evlink": evlink})

	# if there is no issue, save the session
	await save_session_and_wait(user, request, session)

	# redirect to the dashboard
	redirect_uri = request.url_for('dashboard')
	return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)


@router.get("/signup")
async def signup_web(
		request: Request,
		current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
):
	""" Open signup page if there is no session, or be forwarded into dashboard page if a session found

	:param request:
	:param current_session:
	:return:
	"""
	# if session exist, forward to dashboard page
	if current_session is not None:
		redirect_uri = request.url_for('dashboard')
		return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

	# otherwise, allow user to open login page
	return templates.TemplateResponse("auth/signup.html", context={"request": request})


@router.post("/signup")
async def signup_web_post(
		request: Request,
		full_name: str = Form(...),
		email: str = Form(...),
		password: str = Form(...),
		session: AsyncSession = Depends(deps.get_session),

):
	""" Process signup data from user request

	:param request:
	:param full_name:
	:param email:
	:param password:
	:param session:
	:return:
	"""
	# get user by email
	user = await get_user(session, email)

	# validate signup input data
	err_msg = await validate_signup(user, password)

	# if invalid, send an error to the login page
	if err_msg is not None:
		return templates.TemplateResponse("auth/signup.html", context={"request": request, "err_msg": err_msg})

	# store to database
	await save_new_user(session, full_name, email, password)

	# build email verification link
	email_ver_link = await generate_email_verification_uri(request, email)
	# TODO: Compose an email via Email Publisher Service

	success_msg = f"Registration success. We have sent a verification account link into your email. " \
				  f"(REMEMBER: The link will valid ONLY for {settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} minutes)"
	return templates.TemplateResponse("auth/login.html", context={"request": request, "success_msg": success_msg})


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


@router.get('/login_facebook')
async def login_facebook(request: Request):
	# Create facebook session
	facebook = FacebookLogin(request)
	await facebook.oauth2connect()

	authorization_url = await facebook.get_auth_url()

	return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.get('/fb-callback')
async def login_facebook_callback(
		request: Request,
		session: AsyncSession = Depends(deps.get_session),
):
	# Create facebook session
	facebook = FacebookLogin(request)
	await facebook.oauth2connect(apply_fix=True)

	user_info = await facebook.get_token_and_wait()

	# TODO: What happen when there is no response from facebook?
	if user_info is None:
		pass

	social_login_id = user_info["id"]  # use it as an identifier; for now, use it as the password
	email = user_info["email"]
	name = user_info["name"]

	# check email on the database
	# if not found, add this user into the database
	user = await save_and_load_user(session, email, name, social_login_id, SignupBy.FACEBOOK.value)

	# save session
	await save_session_and_wait(user, request, session)

	# https://stackoverflow.com/questions/62119138/how-to-do-a-post-redirect-get-prg-in-fastapi
	# https://httpstatuses.com/302 -> To enforce from POST (source URL) to GET (target URL)
	return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/login_google')  # Tag it as "authentication" for our docs
async def login_google(request: Request):
	# Redirect Google OAuth back to our application
	redirect_uri = request.url_for('google_auth')

	# create google authenticator
	google = GoogleLogin(request)
	await google.oauth2connect()

	# get auth URL and redirect tha page
	return await google.get_authorized_and_redirected(redirect_uri)


@router.get('/google-auth')
async def google_auth(
		request: Request,
		session: AsyncSession = Depends(deps.get_session),
):
	# Perform Google OAuth
	google = GoogleLogin(request)
	await google.oauth2connect()

	# extract user information
	google_user_raw = await google.get_user_information()
	google_user = dict(google_user_raw)

	# check email on the database
	# if not found, add this user into the database
	user = await save_and_load_user(session, google_user["email"], google_user["name"], google_user["sub"],
									SignupBy.GMAIL.value)

	# save session
	await save_session_and_wait(user, request, session)

	# redirect to dashboard
	return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

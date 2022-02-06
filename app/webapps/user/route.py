from typing import Optional
from fastapi import Request, Depends, APIRouter, status, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from app.webapps import deps
from sqlalchemy.ext.asyncio import AsyncSession
from app.webapps.user.service import get_user, validate_ch_passwd, update_password, update_full_name
from app.db.models.user import SignupBy
from app.db.adapters.user.user import get_users

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/users")
async def users(
        request: Request,
        current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
        session: AsyncSession = Depends(deps.get_session),
):
    """ Show list of all registered users if the session found, otherwise redirected into a login page

    :param request:
    :param current_session:
    :param session:
    :return:
    """
    if current_session is None:
        redirect_uri = request.url_for('login_web')

        return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

    # Get user data from database
    users = await get_users(session)

    return templates.TemplateResponse("user/datatable.html", {"request": request,
                                                              "session": current_session,
                                                              "users": users})


@router.get("/ch-passwd")
async def changed_passwd(
        request: Request,
        current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
        session: AsyncSession = Depends(deps.get_session),
):
    """ Form to change password

    :param request:
    :param current_session:
    :param session:
    :return:
    """
    if current_session is None:
        redirect_uri = request.url_for('login_web')

        return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

    # get user by email; there is a chance that the user does not exist (user=None)
    user = await get_user(session, current_session["email"])

    # if not register by EMAIL, reject it directly!
    if user is not None and user.signup_by != SignupBy.EMAIL.value:
        err_msg = f"You cannot change the password when you registered with {user.signup_by}."
        return templates.TemplateResponse("user/change_password.html",
                                          context={"request": request, "err_msg": err_msg, "session": current_session})

    return templates.TemplateResponse("user/change_password.html", {"request": request, "session": current_session})


@router.post("/ch-passwd")
async def changed_passwd_post(
        request: Request,
        old_password: str = Form(...),
        new_password: str = Form(...),
        new_password_again: str = Form(...),
        current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
        session: AsyncSession = Depends(deps.get_session),

):
    """ Process login data from user request

    :param request:
    :param old_password:
    :param new_password:
    :param new_password_again:
    :param session:
    :return:
    """
    # get user by email
    user = await get_user(session, current_session["email"])

    # start validating email
    err_msg = await validate_ch_passwd(user, old_password, new_password, new_password_again)

    # if invalid, send an error to the login page
    if err_msg is not None:
        return templates.TemplateResponse("user/change_password.html",
                                          context={"request": request, "err_msg": err_msg, "session": current_session})

    # no error. update the password
    await update_password(session, user, new_password)

    # go to the change password
    success_msg = "Your password has been successfully changed."
    return templates.TemplateResponse("user/change_password.html",
                                      context={"request": request, "success_msg": success_msg, "session": current_session})


@router.get("/user/profile")
async def user_profile(
        request: Request,
        current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
        session: AsyncSession = Depends(deps.get_session),
):
    """ Form to show profile information

    :param request:
    :param current_session:
    :param session:
    :return:
    """
    if current_session is None:
        redirect_uri = request.url_for('login_web')

        return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

    # get user by email
    user = await get_user(session, current_session["email"])

    return templates.TemplateResponse("user/profile.html", {"request": request, "session": current_session, "user": user})


@router.post("/user/profile")
async def user_profile_post(
        request: Request,
        full_name: str = Form(...),
        current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
        session: AsyncSession = Depends(deps.get_session),

):
    """ Process login data from user request

    :param request:
    :param old_password:
    :param new_password:
    :param new_password_again:
    :param session:
    :return:
    """
    # get user by email
    user = await get_user(session, current_session["email"])

    # # if invalid, send an error to the login page
    # if err_msg is not None:
    # 	return templates.TemplateResponse("user/profile.html",
    # 									  context={"request": request, "err_msg": err_msg, "session": current_session})

    # no error. update the password
    current_session = await update_full_name(session, user, full_name, request, current_session)

    # go to the change password
    success_msg = "Your fullname has been successfully changed."
    return templates.TemplateResponse("user/profile.html",
                                      context={"request": request, "success_msg": success_msg,
                                               "session": current_session, "user": user})

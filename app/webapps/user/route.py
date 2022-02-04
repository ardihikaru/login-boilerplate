from typing import Optional
from fastapi import Request, Depends, APIRouter, status
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse
from app.webapps import deps
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.adapters.user.user import get_all_users

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
	users = await get_all_users(session)
	print(users)

	return templates.TemplateResponse("user/datatable.html", {"request": request,
															  "session": current_session,
															  "users": users})

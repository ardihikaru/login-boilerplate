from typing import Optional
from fastapi import Request, Depends, APIRouter, status
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse
from app.webapps import deps

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def dashboard(
		request: Request,
		current_session: Optional[dict] = Depends(deps.get_current_session),  # prevent to access without active session
):
	""" Login page to the dashboard if the session found, or be redirected into a login page if the given session
		is invalid

	:param request:
	:param current_session:
	:return:
	"""
	if current_session is None:
		redirect_uri = request.url_for('login_web')

		return RedirectResponse(url=redirect_uri, status_code=status.HTTP_302_FOUND)

	# TODO: create a dummy data

	return templates.TemplateResponse("general_pages/dashboard.html", {"request": request, "session": current_session})


@router.get('/favicon.ico')
async def favicon() -> FileResponse:
	""" Return a favicon icon in the browser

	:return:
	"""
	favicon_path = 'app/static/favicon.ico'
	return FileResponse(favicon_path)

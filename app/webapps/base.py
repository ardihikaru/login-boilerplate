from fastapi import APIRouter
from app.webapps.dashboard import route as route_dashboard
from app.webapps.auth import route as route_login
from app.webapps.user import route as route_user

api_router = APIRouter()
api_router.include_router(route_dashboard.router, prefix="", tags=["dashboard-webapp"])
api_router.include_router(route_login.router, prefix="", tags=["auth-webapp"])
api_router.include_router(route_user.router, prefix="", tags=["user-webapp"])

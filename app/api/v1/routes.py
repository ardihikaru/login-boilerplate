from fastapi import APIRouter

from app.api.v1.endpoints.auth import auth
from app.api.v1.endpoints.users import users

API_VERSION = "v1"

api_router = APIRouter()
api_router.include_router(auth.router, prefix=f"/api/{API_VERSION}/auth", tags=["auth"])
api_router.include_router(users.router, prefix=f"/api/{API_VERSION}/users", tags=["users"])

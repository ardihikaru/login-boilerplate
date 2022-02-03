# from fastapi import APIRouter
#
# from app.api.endpoints.auth import auth
# from app.api.endpoints.users import users
from app.api.v1.routes import api_router

# api_router = APIRouter()
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])

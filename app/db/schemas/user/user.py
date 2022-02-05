from typing import Optional, List

from fastapi import Query, Form
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.db.models.user import SignupBy, signup_by_list


class BaseUser(BaseModel):
    class Config:
        orm_mode = True


class User(BaseUser):
    id: int
    full_name: str
    email: EmailStr
    total_login: int
    signup_by: str
    activated: bool
    created_at: datetime
    session_at: datetime


class UserUpdate(BaseUser):
    email: Optional[EmailStr]
    password: Optional[str]
    full_name: Optional[str]


class UserCreate(BaseUser):
    email: EmailStr
    password: str
    full_name: str


class UserDummyCreate(BaseUser):
    full_name: str
    email: EmailStr
    hashed_password: str
    total_login: int
    signup_by: str
    created_at: str
    updated_at: str
    session_at: str


class UserLogout(BaseUser):
    full_name: Optional[str]
    email: Optional[str]
    logout_status: Optional[bool]


class UserAll(BaseUser):
    total: int
    data: List[User]


class QueryParams(BaseModel):
    activated: Optional[bool] = None  # None, True, or False
    signup_by: Optional[str] = None


async def query_params(
        activated: Optional[bool] = Query(None, description="Activated account or not"),
        signup_by: Optional[str] = Query(
            None,
            enum=signup_by_list,
            description="Type of registration method used by the user"
        ),
):
    return QueryParams(activated=activated, signup_by=signup_by)

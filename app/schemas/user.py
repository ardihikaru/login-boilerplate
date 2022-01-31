from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


class BaseUser(BaseModel):
    class Config:
        orm_mode = True


class User(BaseUser):
    id: int
    full_name: str
    email: EmailStr
    total_login: int
    login_by: str
    activated: bool
    created_at: datetime


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
    login_by: str
    created_at: str
    updated_at: str
    session_at: str


class UserLogout(BaseUser):
    full_name: Optional[str]
    email: Optional[str]
    logout_status: Optional[bool]
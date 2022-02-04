from typing import Optional
from fastapi import Query
from .user import BaseModel


async def q_signup(
        l: str = Query(str, description="Email activation token"),
):
    return UserSignupQuery(email_verification_token=l)


class UserSignupQuery(BaseModel):
    email_verification_token: str

from fastapi import Query
from .user import BaseModel


async def q_signup(
        token: str = Query(str, description="Email activation token"),
):
    return UserSignupQuery(email_verification_token=token)


class UserSignupQuery(BaseModel):
    email_verification_token: str

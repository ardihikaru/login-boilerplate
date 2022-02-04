"""
Black-box security shortcuts to generate JWT tokens and password hash/verify

`subject` in access/refresh func may be antyhing unique to User account, `id` etc.
"""

from datetime import datetime, timedelta
from typing import Any, Tuple, Union, Optional, Dict

from jose import jwt
from passlib.context import CryptContext
from app.db.schemas import TokenPayload
from pydantic import ValidationError

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: Union[str, Any]) -> Tuple[str, datetime]:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "refresh": False}
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt, expire


def create_refresh_token(subject: Union[str, Any]) -> Tuple[str, datetime]:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "refresh": True}
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt, expire


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_email_verification_token(subject: Union[str, Any]) -> Tuple[str, datetime]:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "refresh": False}
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt, expire


def get_email_by_verification_token(validation_token: str) -> (bool, Optional[str]):
    try:
        payload = jwt.decode(
            validation_token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return True, payload["sub"]

    # extract only the email
    except jwt.ExpiredSignatureError:
        payload = jwt.decode(
            validation_token, settings.SECRET_KEY, algorithms=[ALGORITHM], options={'verify_exp': False}
        )
        return False, payload["sub"]

    # reject the request
    except (jwt.JWTError, ValidationError):
        return False, None

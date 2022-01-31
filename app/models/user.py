"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Any, cast
from enum import Enum

Base = cast(Any, declarative_base())


class LoginBy(Enum):
    EMAIL = "EMAIL"
    FACEBOOK = "FACEBOOK"
    GMAIL = "GMAIL"


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(254), nullable=True)
    email = Column(String(254), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    total_login = Column(Integer, nullable=False, default=0)
    activated = Column(Boolean(), nullable=False, default=False)
    login_by = Column(String(50), nullable=False, default=LoginBy.EMAIL.value)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_at = Column(DateTime, nullable=False, default=datetime.utcnow)

"""
SQL Alchemy models declaration.

Note, imported by alembic migrations logic, see `alembic/env.py`
"""

from typing import Any, cast
from sqlalchemy.orm import declarative_base

Base = cast(Any, declarative_base())

# Import all the models, so that Base has them before being called
from app.db.models.user import User

import asyncio
from typing import AsyncGenerator, Optional, Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.main import app
from app.db.models.user import User, Base
from app.db.session import async_engine, async_session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    """ Create HTTP test client for testting purpose

    :return:
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
async def test_db_setup_sessionmaker():
    """ Test database session creatiom

    :return:
    """
    # assert if we use TEST_DB URL for 100%
    assert settings.ENVIRONMENT == "PYTEST"
    assert str(async_engine.url) == settings.TEST_SQLALCHEMY_DATABASE_URI

    # always drop and create test db tables between tests session
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return async_session


@pytest.fixture
async def session(test_db_setup_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """ Create database session

    :param test_db_setup_sessionmaker:
    :return:
    """
    async with test_db_setup_sessionmaker() as session:
        yield session


@pytest.fixture
async def activated_user_data() -> Dict:
    """ Set up a dummy data for activated user

    :return:
    """
    return {
        "full_name": "activated.user",
        "email": "activated.user@gmail.com",
        "password": "activated.user@gmail.com",
        "activated": True,
    }


@pytest.fixture
async def inactive_user_data() -> Dict:
    """ Set up a dummy data for inactive user

    :return:
    """
    return {
        "full_name": "inactive.user",
        "email": "inactive.user@gmail.com",
        "password": "inactive.user@gmail.com",
        "activated": False,
    }


@pytest.fixture
async def random_user_login() -> Dict:
    """ Set up a dummy user data

    :return:
    """
    return {
        "full_name": "random.user",
        "email": "random.user@gmail.com",
        "password": "random.user@gmail.com",
        "activated": False,
    }


@pytest.fixture
async def default_activated_user(session: AsyncSession, activated_user_data: Dict):
    """ Create a default activated user in the database

    :param session:
    :param inactive_user_data:
    :return:
    """
    result = await session.execute(select(User).where(User.email == activated_user_data["email"]))
    user: Optional[User] = result.scalars().first()
    if user is None:
        new_user = User(
            email=activated_user_data["email"],
            hashed_password=get_password_hash(activated_user_data["password"]),
            full_name=activated_user_data["full_name"],
            activated=activated_user_data["activated"],
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    return user


@pytest.fixture
async def default_inactive_user(session: AsyncSession, inactive_user_data: Dict):
    """ Create a default inactive user in the database

    :param session:
    :param inactive_user_data:
    :return:
    """
    result = await session.execute(select(User).where(User.email == inactive_user_data["email"]))
    user: Optional[User] = result.scalars().first()
    if user is None:
        new_user = User(
            email=inactive_user_data["email"],
            hashed_password=get_password_hash(inactive_user_data["password"]),
            full_name=inactive_user_data["full_name"],
            activated=inactive_user_data["activated"],
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    return user

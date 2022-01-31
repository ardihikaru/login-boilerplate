from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from app.core.config import settings

# In the unit test mode, it uses the local database using sqlite instead of using pre-deployed postgresql
# Solution: https://github.com/talkpython/web-applications-with-fastapi-course/issues/4
# Important on the requirements file:
# SQLAlchemy==1.4.3
# aiosqlite==0.17.0
if settings.ENVIRONMENT == "PYTEST":
    sqlalchemy_database_uri = settings.TEST_SQLALCHEMY_DATABASE_URI
    async_engine = create_async_engine(sqlalchemy_database_uri, echo=True)

# uses pre-deployed postgresql as the main database
else:
    sqlalchemy_database_uri = settings.DEFAULT_SQLALCHEMY_DATABASE_URI
    async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

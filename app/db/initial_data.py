"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By defualt `main` create a superuser if not exists
"""

import asyncio
from typing import Optional

from sqlalchemy import select, func

from app.core import security
from app.core.config import settings
from app.db.models.user import User
from app.db.session import async_session
from app.scripts.users.generator import DummyUserDataGenerator


async def main() -> None:
    print("Start initial data")
    async with async_session() as session:

        result = await session.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        user: Optional[User] = result.scalars().first()

        if user is None:
            new_superuser = User(
                full_name=settings.FIRST_SUPERUSER_EMAIL,
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=security.get_password_hash(
                    settings.FIRST_SUPERUSER_PASSWORD
                ),
            )
            session.add(new_superuser)
            await session.commit()
            print("Superuser was created")
        else:
            print("Superuser already exists in database")

        # count total users
        result = await session.execute(select(func.count()).select_from(select(User).subquery()))
        total_users = result.scalars().one()

        # check if it enforces to create dummy users or not
        # also make sure that the dummy data generation should be performed ONCE!
        if settings.ADD_DUMMY_USERS and total_users > settings.TOTAL_DUMMY_USERS:
            print("Dummy data have been generated. Nothing to do.")

        # otherwise, try creating some dummy users
        elif settings.ADD_DUMMY_USERS and total_users < settings.TOTAL_DUMMY_USERS:
            generator = DummyUserDataGenerator(settings.TOTAL_DUMMY_USERS)
            await generator.run()
            dummy_users = await generator.get_dummy_users()

            for dummy_user in dummy_users:
                new_dummy_user = User(
                    full_name=dummy_user["full_name"],
                    email=dummy_user["email"],
                    hashed_password=dummy_user["hashed_password"],
                    total_login=dummy_user["total_login"],
                    signup_by=dummy_user["signup_by"],
                    activated=dummy_user["activated"],
                    created_at=dummy_user["created_at"],
                    updated_at=dummy_user["updated_at"],
                    session_at=dummy_user["session_at"],
                )
                # new_dummy_user = User(dummy_user)
                session.add(new_dummy_user)
                await session.commit()
                print("Dummy User(={}) was created".format(dummy_user["full_name"]))

            print("\nInitial data created with some dummy data")
        else:
            print("Initial data created WITHOUT any dummy data")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
from app.core.security import get_password_hash
from app.db.schemas.user.user import UserDummyCreate
from app.db.models.user import SignupBy
from typing import Dict
from pydantic import BaseModel
import names
from datetime import timedelta, datetime


class DummyUserModel(BaseModel):
    dictionaries: Dict[str, UserDummyCreate]


class DummyUserDataGenerator:
    def __init__(self, num_users=10, export_path="dummy_users.json"):
        # Capture input parameters
        self.num_users = num_users
        self.path = export_path

        # setup login type
        self.signup_type = [
            SignupBy.EMAIL.value,
            SignupBy.FACEBOOK.value,
            SignupBy.GMAIL.value,
        ]

        self.dummy_users = []

    def __await__(self):
        async def closure():
            return self

        return closure().__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def run(self):
        await self.__generate()

    async def generate_one(self, default_activated=None, raw=False):
        # create a random user
        rand_full_name = names.get_full_name().lower()

        # get date by randoming between this week and last three week ago
        today_dt = datetime.now()
        today_date = today_dt.date()
        today_time = today_dt.time()
        weekday = today_date.weekday()
        week_change = random.randint(0, 2)  # to control between this week (=0) or last weeks (<0)
        start_delta = timedelta(days=weekday, weeks=week_change)
        start_of_week = today_date - start_delta  # e.g. datetime.date(2022, 01, 31)
        # convert back to a datetime
        to_datetime_again = datetime.combine(start_of_week, today_time)
        total_login = random.randint(0, 60)

        # if `default_activated` parameter is given, set the activated value as per given value
        if default_activated:
            # generate variable values
            signup_by = self.signup_type[random.randint(0, 2)]  # get login type by index
            activated = bool(random.randint(0, 1)) if signup_by == SignupBy.EMAIL.value else True

        # if total login is higher than zero, set the activated value as True
        elif total_login > 0:
            activated = True
            signup_by = self.signup_type[random.randint(0, 2)]  # get login type by index

        # otherwise, if login by Email, randomize the activation status between True or False
        else:
            activated = default_activated
            signup_by = SignupBy.EMAIL.value  # generate variable values

        # generate a random user detailed information based on the generate random name
        user = {
            "full_name": rand_full_name,
            "email": "{}@gmail.com".format(rand_full_name.replace(" ", ".")),
            "hashed_password": get_password_hash(rand_full_name),
            "total_login": random.randint(0, 60),
            "signup_by": signup_by,
            "activated": activated,
            "created_at": to_datetime_again,
            "updated_at": to_datetime_again,
            "session_at": to_datetime_again,
        }

        # prepare the key for storing the user data into database
        if not raw:
            user.update({
                "hashed_password": get_password_hash(rand_full_name),
            })

        # prepare the key for raw user data used for an input (e.g. to register a new user)
        else:
            user.update({
                "password": rand_full_name,
            })

        return user

    async def __generate(self):
        """ generates random dummy users """
        for i in range(self.num_users):
            user = await self.generate_one()

            self.dummy_users.append(user)

    async def get_dummy_users(self):
        return self.dummy_users

    def export_to_json_file(self, generated_users):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(generated_users, f, ensure_ascii=False, indent=4)

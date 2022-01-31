#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
from app.core.security import get_password_hash
from app.schemas.user import UserDummyCreate
from app.models.user import SignupBy
from typing import Dict
from pydantic import BaseModel
import names
from datetime import date, timedelta, datetime

class DummyUserModel(BaseModel):
	dictionaries: Dict[str, UserDummyCreate]


class DummyUserDataGenerator:
	def __init__(self, num_users, export_path="dummy_users.json"):
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

	def run(self):
		self.__generate()

	def __generate(self):
		""" generates random dummy users """
		for i in range(self.num_users):
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

			# generate variable values
			signup_by = self.signup_type[random.randint(0, 2)]  # get login type by index
			# if login by Email, randomize the activation status between True or False
			activated = bool(random.randint(0, 1)) if signup_by == SignupBy.EMAIL.value else True

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

			self.dummy_users.append(user)

	def get_dummy_users(self):
		return self.dummy_users

	def export_to_json_file(self, generated_users):
		with open(self.path, 'w', encoding='utf-8') as f:
			json.dump(generated_users, f, ensure_ascii=False, indent=4)

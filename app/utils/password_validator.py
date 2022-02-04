import asyncio
from typing import Generator
import logging
from enum import Enum

L = logging.getLogger("uvicorn.error")


class CharType(Enum):
	LOWER = "LOWER"
	UPPER = "UPPER"
	DIGIT = "DIGIT"
	SYMBOL = "SYMBOL"


class PasswordValidator(object):
	"""
	An asynchronous class to validate a given password with multiple scenarios
	"""

	def __init__(self, password):
		self.password = password

		# define the rules
		self.min_chars = 8
		self.min_lower_chars = 1
		self.min_upper_chars = 1
		self.min_digit_chars = 1
		self.min_symbol_chars = 1

		# saved results
		self.results = {
			CharType.LOWER.value: 0,
			CharType.UPPER.value: 0,
			CharType.DIGIT.value: 0,
			CharType.SYMBOL.value: 0,
		}

	def __await__(self):
		async def closure():
			return self

		return closure().__await__()

	async def __aenter__(self):
		return self

	async def __aexit__(self, *args):
		pass

	async def validate_and_wait(self):
		# asynchronously verify the char type
		for process_result in asyncio.as_completed(
				[self._check_char_type(ch) for ch in self.password]
		):

			_ = await process_result

		L.error(f"Total chars={len(self.password)}; Results={self.results}")

		# Now verify each validator
		# (1) contains at least one lower character
		if self.results[CharType.LOWER.value] < self.min_lower_chars:
			return "Password should contains at least one lower character"

		# (2) contains at least one upper character
		if self.results[CharType.UPPER.value] < self.min_upper_chars:
			return "Password should contains at least one upper character"

		# (3) contains at least one digit character
		if self.results[CharType.DIGIT.value] < self.min_digit_chars:
			return "Password should contains at least one digit character"

		# (4) contains at least one special character
		if self.results[CharType.SYMBOL.value] < self.min_symbol_chars:
			return "Password should contains at least one special character"

		# (5) contains at least 8 characters
		if len(self.password) < self.min_chars:
			return "Password should contains at least contains 8 characters"

	async def _check_char_type(self, ch):
		""" Check character type

		:param ch:
		:return:
		"""
		# check lowercase
		if ch.islower():
			self.results[CharType.LOWER.value] += 1

		# check uppercase
		if ch.isupper():
			self.results[CharType.UPPER.value] += 1

		# check digit
		if (ch >= "0" and ch <= "9"):
			self.results[CharType.DIGIT.value] += 1

		# check special chars
		if self.is_special_char(ch):
			self.results[CharType.SYMBOL.value] += 1

	def is_special_char(self, ch):
		special_characters = "\"!@#$%^&*()-+?_=,<>/\""
		if ch in special_characters:
			return True

		return False


"""
# How to use:

async def main():
	sample_password = "aRdi-1fds*"

	passwd_validator = PasswordValidator(sample_password)
	err_msg = await passwd_validator.validate_and_wait()

	# print error if found
	if err_msg is not None:
		L.error(f"Error Message: {err_msg}")

	exit()  # Exit


if __name__ == '__main__':
	try:
		asyncio.get_event_loop().run_until_complete(main())
		asyncio.get_event_loop().run_forever()
	except Exception as err:
		print("Got error in the middle of execution ({})".format(err))
	except KeyboardInterrupt as err:
		print("Interrupted by keyboard")
	finally:
		print("Exiting App")

"""

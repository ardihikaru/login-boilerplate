from enum import Enum


class AuthErrMessage(Enum):
	INCORRECT_EMAIL_PASSWORD = "Incorrect email or password"
	INACTIVE_USER = "Your account has not been activated yet"
	UNAUTHORIZED_USER = "Not authenticated"

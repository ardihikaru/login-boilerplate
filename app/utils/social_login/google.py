from app.core.config import google as google_conf
from app.utils.common import get_root_url
from typing import Dict, Optional

from authlib.integrations.starlette_client import OAuth

from enum import Enum
import asyncio
import logging

L = logging.getLogger("uvicorn.error")


class GoogleLogin(object):
	"""
	An asynchronous class to support the execution of google login
	"""

	def __init__(self, request):
		self.request = request

		# initialize default value
		self.oauth = None

	def __await__(self):
		async def closure():
			return self

		return closure().__await__()

	async def __aenter__(self):
		return self

	async def __aexit__(self, *args):
		pass

	async def oauth2connect(self) -> None:
		""" Create the Oauth2 session connection to Google API

		:return:
		"""
		# initialize
		self.oauth = OAuth()

		# register into google registry
		self.oauth.register(
			name='google',
			client_id=google_conf.GOOGLE_CLIENT_ID,
			client_secret=google_conf.GOOGLE_CLIENT_SECRET,
			server_metadata_url=google_conf.GOOGLE_CONF_URL,
			client_kwargs={
				'scope': 'openid email profile'
			},
		)

	async def get_authorized_and_redirected(self, redirect_uri):
		""" Get the Google's authorization URL and get redirected

		:return:
		"""
		return await self.oauth.google.authorize_redirect(self.request, redirect_uri)

	async def _get_authorize_access_token(self):
		""" Get the Google's authorize access token

		:return:
		"""
		return await self.oauth.google.authorize_access_token(self.request)

	async def get_user_information(self):
		""" Get the Google's user information

		:return:
		"""
		# get auth token
		auth_token = await self._get_authorize_access_token()

		""" Sample user information
			{
			  'iss': 'https://accounts.google.com',
			  'azp': '1037937xxx889-hqkrnck0ud9dgr60v33aqq440aumcks7.apps.googleusercontent.com',
			  'aud': '1037937xxx889-hqkrnck0ud9dgr60v33aqq440aumcks7.apps.googleusercontent.com',
			  'sub': 'xxx8594265xxx47033526',
			  'email': 'ardihikaru3@gmail.com',
			  'email_verified': True,
			  'at_hash': '4ZYbGgxxxnugqxxxGhS0yQ',
			  'nonce': 'SSQxxxmkGMBZNZXXXXk4',
			  'name': 'muhammad febrian Ardiansyah',
			  'picture': 'https://lh3.googleusercontent.com/a-/AOh14Ghpy8YVxxxjYfIdFvmRrxxxx_fuJMapzrEws1jlbg=s96-c',
			  'given_name': 'muhammad febrian',
			  'family_name': 'Ardiansyah',
			  'locale': 'en',
			  'iat': 1643864553,
			  'exp': 1643868153
			}
		"""

		return await self.oauth.google.parse_id_token(self.request, auth_token)

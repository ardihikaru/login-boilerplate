from app.core.config import facebook as fb_conf
from app.utils.common import get_root_url
from typing import Dict, Optional

import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

import logging

L = logging.getLogger("uvicorn.error")


class FacebookLogin(object):
    """
    An asynchronous class to support the execution of facebook login
    """

    def __init__(self, request):
        self.request = request

        # initialize default value
        self.fb = None

    def __await__(self):
        async def closure():
            return self

        return closure().__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def oauth2connect(self, apply_fix=False) -> None:
        """ Create the Oauth2 session connection to Facebook API

        :return:
        """
        # build redirect URI
        # `/fb-callback` is the callback for facebook which is defined in `auth/route.py` under login_facebook_callback()
        redirect_uri = get_root_url(self.request.url._url) + "/fb-callback"

        # initialize facebook session
        self.fb = requests_oauthlib.OAuth2Session(
            fb_conf.FB_CLIENT_ID,
            redirect_uri=redirect_uri,
            scope=fb_conf.FB_SCOPE
        )

        # apply a fix for Facebook if enabled
        if apply_fix:
            self.fb = facebook_compliance_fix(self.fb)

    async def get_auth_url(self) -> str:
        """ Get the Facebook's authorization URL

        :return:
        """
        authorization_url, _ = self.fb.authorization_url(fb_conf.FB_AUTHORIZATION_BASE_URL)

        L.info(f"Facebook auth URL={authorization_url}")

        return authorization_url

    async def get_token_and_wait(self) -> Optional[Dict]:
        # fetch token
        self.fb.fetch_token(
            fb_conf.FB_TOKEN_URL,
            client_secret=fb_conf.FB_CLIENT_SECRET,

            # Sample value: https://<domain>>/fb-callback?code=<the_code_from_facebook>
            authorization_response=self.request.url._url,
        )

        # get facebook user information
        user_info = self.fb.get(
            "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
        ).json()

        """
        Sample:
        {
          'id': '102xxx82921944xxx',
          'name': 'Muhammad Febrian Ardiansyah',
          'email': 'ardixxxxxxx@xxxxx.com',
          'picture': {
            'data': {
              'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=1022xxx2921944xxx&height=50&width=50&ext=1646383747&hash=AeRnxxxJgVwvT_e32Yg'
            }
          }
        }
        """

        return user_info

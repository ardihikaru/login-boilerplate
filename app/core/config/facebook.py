# -*- coding: utf-8 -*-
"""Facebook Social Login Configuration."""

from pathlib import Path
from pydantic import BaseSettings
from typing import List

PROJECT_DIR = Path(__file__).parent.parent.parent.parent

class Facebook(BaseSettings):
    """Facebook configuration model definition.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        EXT_FB_CLIENT_ID
        EXT_FB_CLIENT_SECRET
        EXT_FB_AUTHORIZATION_BASE_URL
        EXT_FB_TOKEN_URL
        EXT_FB_SCOPE
        EXT_FB_QUERY

    Attributes:
        FB_CLIENT_ID(str): Facebook client ID.
        FB_CLIENT_SECRET(str): Facebook client secret.
        FB_AUTHORIZATION_BASE_URL(str): Facebook authorization base URL.
        FB_TOKEN_URL(str): Facebook token URL.
        FB_SCOPE(List): Facebook scope of access.
        FB_QUERY(str): Facebook query to retrieve the user information from the graph API.

    """

    # Facebook Config
    FB_CLIENT_ID: str = None
    FB_CLIENT_SECRET: str = None
    FB_AUTHORIZATION_BASE_URL: str = None
    FB_TOKEN_URL: str = None
    FB_SCOPE: List = ["email"]

    class Config:
        """Config sub-class needed to customize BaseSettings settings.

        More details can be found in pydantic documentation:
        https://pydantic-docs.helpmanual.io/usage/settings/

        """

        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True
        env_prefix = "EXT_"


facebook = Facebook()

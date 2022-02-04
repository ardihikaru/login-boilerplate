# -*- coding: utf-8 -*-
"""Google Social Login Configuration."""

from pathlib import Path
from pydantic import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent.parent

class Google(BaseSettings):
    """Google configuration model definition.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        EXT_GOOGLE_CLIENT_ID
        EXT_GOOGLE_CLIENT_SECRET
        EXT_GOOGLE_CONF_URL

    Attributes:
        GOOGLE_CLIENT_ID(str): Google client ID.
        GOOGLE_CLIENT_SECRET(str): Google client secret.
        GOOGLE_CONF_URL(str): Google openid configuration.

    """

    # Google Config
    GOOGLE_CLIENT_ID: str = None
    GOOGLE_CLIENT_SECRET: str = None
    GOOGLE_CONF_URL: str = None

    class Config:
        """Config sub-class needed to customize BaseSettings settings.

        More details can be found in pydantic documentation:
        https://pydantic-docs.helpmanual.io/usage/settings/

        """

        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True
        env_prefix = "EXT_"


google = Google()

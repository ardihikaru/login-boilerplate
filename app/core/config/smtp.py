# -*- coding: utf-8 -*-
"""Email Composer Configuration."""

from pathlib import Path
from pydantic import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent.parent


class SMTP(BaseSettings):
    """Email Composer configuration model definition.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        EXT_SMTP_SERVER
        EXT_SMTP_PORT
        EXT_SMTP_SENDER
        EXT_SMTP_USERNAME
        EXT_SMTP_PASSWORD
        EXT_SMTP_SSL
        EXT_SMTP_TEMPLATE_PATH

    Attributes:
        SMTP_SERVER(str): SMTP server.
        SMTP_PORT(int): SMTP port.
        SMTP_SENDER(str): SMTP sender (email).
        SMTP_USERNAME(str): SMTP username.
        SMTP_PASSWORD(str): SMTP password.
        SMTP_SSL(bool): SMTP SSL configuration status (enabled or disabled).
        SMTP_TEMPLATE_PATH(str): SMTP HTML template folder path.

    """

    # Email Composer Config
    SMTP_SERVER: str = "smtp.gmail.com"  # e.g. using smtp.gmail.com
    SMTP_PORT: int = 465  # e.g. using gmail.com
    SMTP_SENDER: str = None
    SMTP_USERNAME: str = None
    SMTP_PASSWORD: str = None
    SMTP_SSL: bool = True
    SMTP_TEMPLATE_PATH: str = True

    class Config:
        """Config sub-class needed to customize BaseSettings settings.

        More details can be found in pydantic documentation:
        https://pydantic-docs.helpmanual.io/usage/settings/

        """

        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True
        env_prefix = "EXT_"


smtp = SMTP()

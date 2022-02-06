# -*- coding: utf-8 -*-
"""Redis configuration."""

from pathlib import Path
from pydantic import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent.parent


class Redis(BaseSettings):
    """Redis configuration model definition.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        EXT_REDIS_HOST
        EXT_REDIS_PORT
        EXT_REDIS_USERNAME
        EXT_REDIS_PASSWORD
        EXT_EXT_REDIS_DB
        EXT_REDIS_USE_SENTINEL

    Attributes:
        REDIS_HOST(str): Redis host.
        REDIS_PORT(int): Redis port.
        REDIS_USERNAME(str): Redis username.
        REDIS_PASSWORD(str): Redis password.
        REDIS_DB(str): Redis database.
        REDIS_USE_SENTINEL(bool): If provided Redis config is for Sentinel.

    """

    # Redis Config
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_USERNAME: str = None
    REDIS_PASSWORD: str = None
    REDIS_DB: str = "0"
    REDIS_USE_SENTINEL: bool = False

    # REDIS_USE_SENTINEL: bool = False
    class Config:
        """Config sub-class needed to customize BaseSettings settings.

        More details can be found in pydantic documentation:
        https://pydantic-docs.helpmanual.io/usage/settings/

        """

        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True
        env_prefix = "EXT_"


redis = Redis()

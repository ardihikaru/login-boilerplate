import pytest
from typing import Dict
from httpx import AsyncClient

from app.db.models.user import User
from app.api.v1.endpoints.auth.utils import AuthErrMessage

# All test coroutines in file will be treated as marked (async allowed).
pytestmark = pytest.mark.asyncio


async def test_login_activated_user(client: AsyncClient, default_activated_user: User, activated_user_data: Dict):
    """ Test login access token with the pre-defined activated user data
        with `default_activated_user` parameter to ensure the user has been created

    :param client:
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    access_token_resp = await get_token_resp(client, activated_user_data)
    assert access_token_resp.status_code == 200
    resp_json = access_token_resp.json()

    # assert the existance of each key
    assert resp_json.get("token_type", None) is not None
    assert resp_json.get("access_token", None) is not None
    assert resp_json.get("expire_at", None) is not None
    assert resp_json.get("refresh_token", None) is not None
    assert resp_json.get("refresh_expire_at", None) is not None

    # assert the data type
    assert type(resp_json["token_type"]) is str
    assert type(resp_json["access_token"]) is str
    assert type(resp_json["expire_at"]) is str
    assert type(resp_json["refresh_token"]) is str
    assert type(resp_json["refresh_expire_at"]) is str

    # assert the expected value
    assert resp_json["token_type"] == "bearer"


async def test_login_inactive_user(client: AsyncClient, default_inactive_user: User, inactive_user_data: Dict):
    """ Test login access token with the pre-defined activated user data
        with `default_activated_user` parameter to ensure the user has been created

    :param client:
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    access_token_resp = await get_token_resp(client, inactive_user_data)
    assert access_token_resp.status_code == 400
    resp_json = access_token_resp.json()

    # assert the existance of each key
    assert resp_json.get("detail", None) is not None

    # assert the data type
    assert type(resp_json["detail"]) is str

    # assert the expected value
    assert resp_json["detail"] == AuthErrMessage.INACTIVE_USER.value


async def test_login_unauthorized_user(client: AsyncClient, random_user_login: Dict):
    """ Test login access token with a random user data

    :param client:
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    access_token_resp = await get_token_resp(client, random_user_login)
    assert access_token_resp.status_code == 400
    resp_json = access_token_resp.json()

    # assert the existance of each key
    assert resp_json.get("detail", None) is not None

    # assert the data type
    assert type(resp_json["detail"]) is str

    # assert the expected value
    assert resp_json["detail"] == AuthErrMessage.INCORRECT_EMAIL_PASSWORD.value


async def test_logout_unauthorized_user(client: AsyncClient):
    """ Test logout without any prior active session

    :param client:`
    :return:
    """
    logout_resp = await client.get(
        "/api/v1/auth/logout",  # logout endpoint
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert logout_resp.status_code == 401
    resp_json = logout_resp.json()

    # assert the existance of each key
    assert resp_json.get("detail", None) is not None

    # assert the data type
    assert type(resp_json["detail"]) is str

    # assert the expected value
    assert resp_json["detail"] == AuthErrMessage.UNAUTHORIZED_USER.value


async def test_logout_authorized_user(client: AsyncClient, default_activated_user: User, activated_user_data: Dict):
    """ Test logout with a random user data with `default_activated_user` parameter to ensure the user has been created

    :param client:`
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    # first, do login to get the access token
    access_token_resp = await get_token_resp(client, activated_user_data)
    assert access_token_resp.status_code == 200
    resp_json = access_token_resp.json()

    assert resp_json.get("access_token", None) is not None
    access_token = resp_json["access_token"]
    logout_resp = await client.get(
        "/api/v1/auth/logout",  # access-token endpoint
        headers={"Authorization": f"Bearer {access_token}"},
    )
    logout_resp_json = logout_resp.json()
    assert logout_resp.status_code == 200

    # assert the existance of each key
    assert logout_resp_json.get("full_name", None) is not None
    assert logout_resp_json.get("email", None) is not None
    assert logout_resp_json.get("logout_status", None) is not None

    # assert the data type
    assert type(logout_resp_json["full_name"]) is str
    assert type(logout_resp_json["email"]) is str
    assert type(logout_resp_json["logout_status"]) is bool

    # assert the expected value
    assert logout_resp_json["full_name"] == activated_user_data["full_name"]
    assert logout_resp_json["email"] == activated_user_data["email"]
    assert logout_resp_json.get("logout_status", False) is True


async def test_valid_refresh_token(client: AsyncClient, default_activated_user: User, activated_user_data: Dict):
    """ Test refresh token of a logged user with `default_activated_user` parameter to ensure the user has been created

    :param client:`
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    # first, do login to get the access token
    access_token_resp = await get_token_resp(client, activated_user_data)
    assert access_token_resp.status_code == 200
    resp_json = access_token_resp.json()

    assert resp_json.get("refresh_token", None) is not None
    refresh_token = resp_json["refresh_token"]
    refresh_token_resp = await client.post(
        "/api/v1/auth/refresh-token",  # refresh-token endpoint
        json={
            "refresh_token": refresh_token
        }
    )
    assert refresh_token_resp.status_code == 200
    resp_json = refresh_token_resp.json()

    # assert the existance of each key
    assert resp_json.get("token_type", None) is not None
    assert resp_json.get("access_token", None) is not None
    assert resp_json.get("expire_at", None) is not None
    assert resp_json.get("refresh_token", None) is not None
    assert resp_json.get("refresh_expire_at", None) is not None

    # assert the data type
    assert type(resp_json["token_type"]) is str
    assert type(resp_json["access_token"]) is str
    assert type(resp_json["expire_at"]) is str
    assert type(resp_json["refresh_token"]) is str
    assert type(resp_json["refresh_expire_at"]) is str

    # assert the expected value
    assert resp_json["token_type"] == "bearer"


async def test_invalid_refresh_token(
        client: AsyncClient,
        default_activated_user: User,  # to enforce the creation of activated user
        activated_user_data: Dict,
):
    """ Test refresh token of an invalid refresh token

    :param client:`
    :param default_activated_user:
    :param activated_user_data:
    :return:
    """
    # first, do login to get the access token
    access_token_resp = await get_token_resp(client, activated_user_data)
    assert access_token_resp.status_code == 200
    resp_json = access_token_resp.json()

    assert resp_json.get("refresh_token", None) is not None
    refresh_token_resp = await client.post(
        "/api/v1/auth/refresh-token",  # refresh-token endpoint
        json={
            "refresh_token": "an invalid refresh token"
        }
    )
    assert refresh_token_resp.status_code == 403


async def get_token_resp(client: AsyncClient, user_data: Dict):
    """ Get access token response

    :param client:
    :param user_data:
    :return:
    """

    access_token_resp = await client.post(
        "/api/v1/auth/access-token",  # access-token endpoint
        data={
            "username": user_data["email"],  # it uses email as the username
            "password": user_data["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    return access_token_resp

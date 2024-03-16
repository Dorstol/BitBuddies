from httpx import AsyncClient
from sqlalchemy import select

from conftest import async_session_maker
from src.accounts.models import User

test_user = {
    "first_name": "test",
    "last_name": "test",
    "email": "user@test.com",
    "password": "string",
}


async def test_register(ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json=test_user,
    )
    assert response.status_code == 201
    assert response.json() is None


async def test_user_already_exist(ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json=test_user,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "REGISTER_USER_ALREADY_EXISTS"}


async def test_register_failed(ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json={},
    )
    assert response.status_code == 422


async def test_request_verify_token(ac: AsyncClient):
    response = await ac.post(
        "/auth/request-verify-token",
        json={"email": test_user["email"]},
    )
    assert response.status_code == 202
    assert response.json() is None


async def test_make_user_verified():
    async with async_session_maker() as session:
        stmt = select(User).where(User.id == 1)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        user.is_verified = True
        await session.commit()

    assert user.first_name == test_user["first_name"]


async def test_user_login(ac: AsyncClient):
    data = {
        "username": test_user["email"],
        "password": test_user["password"],
    }
    response = await ac.post(
        "/auth/jwt/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert response.json() != {}
    assert response.json()["token_type"] == "bearer"


async def test_user_logout_failed(ac: AsyncClient):
    response = await ac.post("/auth/jwt/logout")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


async def test_request_forgot_password(ac: AsyncClient):
    response = await ac.post(
        "/auth/forgot-password",
        json={"email": test_user["email"]},
    )
    assert response.status_code == 202
    assert response.json() is None


async def test_request_forgot_password_failed(ac: AsyncClient):
    response = await ac.post(
        "/auth/forgot-password",
        json={},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["input"] is None


async def test_request_verify_token_verified_user(ac: AsyncClient):
    response = await ac.post(
        "/auth/request-verify-token",
        json={"email": test_user["email"]},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "VERIFY_USER_ALREADY_VERIFIED"}


async def test_request_verify_token_failed(ac: AsyncClient):
    response = await ac.post(
        "/auth/request-verify-token",
        json={
            "email": "not_existed_user@gmail.com",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "USER_DOES_NOT_EXIST"}

    response = await ac.post(
        "/auth/request-verify-token",
        json={},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["input"] is None

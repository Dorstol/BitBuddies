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

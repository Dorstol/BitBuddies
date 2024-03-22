import json

import pytest
from fastapi_users.authentication import JWTStrategy
from fastapi_users.password import PasswordHelper
from httpx import AsyncClient
from sqlalchemy import insert
from src.accounts.schemas import UserRead
from conftest import async_session_maker
from src.accounts.crud import get_user
from src.accounts.models import User

password_helper = PasswordHelper()


class TestUser:
    jwt_strategy = JWTStrategy(secret="SECRET", lifetime_seconds=3600)

    @pytest.fixture(scope="session", autouse=True)
    async def create_user(self):
        async with async_session_maker() as session:
            hashed_password = password_helper.hash("qwe123")
            stmt = insert(User).values(
                first_name="Test",
                last_name="test",
                email="test@gmail.com",
                hashed_password=hashed_password,
                is_verified=True,
                is_active=True,
                is_superuser=False,
            )
            await session.execute(stmt)
            await session.commit()
            self.user = await get_user(user_id=1, session=session)
            return self.user

    @pytest.fixture(scope="session", autouse=True)
    async def write_user_token(self):
        token = await self.jwt_strategy.write_token(user=self.user)
        return token

    async def test_user_me(self, write_user_token, create_user, ac: AsyncClient):
        response = await ac.get(
            "/users/me",
            headers={"Authorization": "Bearer " + write_user_token},
        )
        assert response is not None
        assert response.status_code == 200
        assert response.json()["id"] == create_user.id
        assert response.json()["email"] == create_user.email
        assert create_user.is_active is not None
        assert create_user.is_verified is not None
        assert create_user.is_superuser is not None

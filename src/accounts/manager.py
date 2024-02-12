from typing import Optional

from fastapi import Depends, Request
from fastapi_mail import MessageSchema, MessageType, FastMail
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    models,
    exceptions,
    FastAPIUsers,
)
from fastapi_users.jwt import generate_jwt
from starlette.responses import JSONResponse

from src.accounts.config import auth_backend
from src.accounts.models import User
from src.config import conf
from src.database import get_user_db

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ):
        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )

        html = f"localhost:3000/verify/{token}"

        message = MessageSchema(
            subject="Verify account",
            recipients=[user.email],
            body=html,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        return await fm.send_message(message)

    async def request_verify(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ):
        return await self.on_after_register(user=user)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ) -> JSONResponse:
        html = f"localhost:3000/reset-password/{token}"

        message = MessageSchema(
            subject="Forgot password",
            recipients=[user.email],
            body=html,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "email has been sent"})


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

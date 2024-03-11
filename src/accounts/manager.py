from typing import Optional

from fastapi import Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi_mail import MessageSchema, MessageType, FastMail
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    models,
    exceptions,
)
from fastapi_users.jwt import generate_jwt
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext

from src.accounts.config import auth_backend
from src.accounts.fastapi_users.fastapi_users import CustomFastAPIUsers
from src.accounts.models import User
from src.config import conf
from src.database import get_user_db

templates = Jinja2Templates(directory="src/emails")
SECRET = "SECRET"

context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def generate_data_message(
        self,
        request: Optional[Request],
        user: models.UP,
        verify: bool = False,
    ):

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
        if verify:
            template_context = {
                "url": f"http://localhost:3000/verify/{token}",
            }

            html = templates.TemplateResponse(
                request=request,
                name="email_confirmation.html",
                context=template_context,
                media_type="text/html",
            ).body.decode("utf-8")

            message = MessageSchema(
                subject="Verify account",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html,
            )
        else:
            template_context = {
                "url": f"http://localhost:3000/forgot-password/{token}",
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

            html = templates.TemplateResponse(
                request=request,
                name="forgot_password_confirmation.html",
                context=template_context,
                media_type="text/html",
            ).body.decode("utf-8")

            message = MessageSchema(
                subject="Forgot password",
                recipients=[user.email],
                body=html,
                subtype=MessageType.html,
            )

        fm = FastMail(conf)

        await fm.send_message(message=message)

    async def on_after_register(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ):
        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        return await self.generate_data_message(
            request=request,
            user=user,
            verify=True,
        )

    async def request_verify(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ):
        if not user:
            raise HTTPException(status_code=404, detail="USER_DOES_NOT_EXIST")
        if user.is_verified:
            raise HTTPException(status_code=400, detail="VERIFY_USER_ALREADY_VERIFIED")

        return await self.generate_data_message(
            request=request,
            user=user,
            verify=True,
        )

    async def forgot_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        """
        Start a forgot password request.

        Triggers the on_after_forgot_password handler on success.

        :param user: The user that forgot its password.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserInactive: The user is inactive.
        """
        if not user.is_active:
            raise exceptions.UserInactive()

        await self.generate_data_message(request=request, user=user)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, password_helper)


fastapi_users = CustomFastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

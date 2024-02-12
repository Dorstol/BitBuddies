from fastapi import Response, status
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, Strategy


class CustomAuthenticationBackend(AuthenticationBackend):
    async def login(
        self, strategy: Strategy[models.UP, models.ID], user: models.UP
    ) -> Response:
        if not user.is_verified:
            return Response(
                content='"detail": "LOGIN_USER_NOT_VERIFIED"',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token)

from typing import Generic, Type

from fastapi import APIRouter
from fastapi_users import FastAPIUsers, models, schemas

from src.accounts.fastapi_users.register import get_register_router
from src.accounts.fastapi_users.verify import get_verify_router


class CustomFastAPIUsers(FastAPIUsers, Generic[models.UP, models.ID]):
    def get_register_router(
        self, user_schema: Type[schemas.U], user_create_schema: Type[schemas.UC]
    ) -> APIRouter:
        """
        Return a router with a register route.

        :param user_schema: Pydantic schema of a public user.
        :param user_create_schema: Pydantic schema for creating a user.
        """
        return get_register_router(self.get_user_manager, user_create_schema)

    def get_verify_router(self, user_schema: Type[schemas.U]) -> APIRouter:
        """
        Return a router with e-mail verification routes.

        :param user_schema: Pydantic schema of a public user.
        """
        return get_verify_router(self.get_user_manager)

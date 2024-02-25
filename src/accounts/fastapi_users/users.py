import uuid
from typing import Type

from PIL import Image
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    File,
    UploadFile,
)
from fastapi.params import Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication import Authenticator
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import User, Position
from src.accounts.schemas import UserRead
from src.config import BASE_DIR
from src.database import get_async_session


def get_users_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: Type[schemas.U],
    user_update_schema: Type[schemas.UU],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with the authentication routes."""
    router = APIRouter()

    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification
    )
    get_current_superuser = authenticator.current_user(
        active=True, verified=requires_verification, superuser=True
    )

    async def get_user_or_404(
        id: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ) -> models.UP:
        try:
            parsed_id = user_manager.parse_id(id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/me",
        response_model=user_schema,
        name="users:current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
        },
    )
    async def me(
        user: models.UP = Depends(get_current_active_user),
    ):
        return schemas.model_validate(user_schema, user)

    @router.patch(
        "/me",
        response_model=user_schema,
        dependencies=[Depends(get_current_active_user)],
        name="users:patch_current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def update_me(
        request: Request,
        user_update: user_update_schema,  # type: ignore
        user: models.UP = Depends(get_current_active_user),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.update(
                user_update, user, safe=True, request=request
            )
            return schemas.model_validate(user_schema, user)
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    @router.post(
        "/me/upload_photo",
        name="users:upload_photo",
    )
    async def upload_user_photo(
        file: UploadFile = File(...),
        user: models.UP = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session),
    ):
        if file.size >= 1000000:
            return {"detail": "UNSUPPORTED_FILE_SIZE"}

        filename = file.filename
        extension = filename.split(".")[1]

        if extension not in ["jpg", "png", "jpeg", "svg"]:
            return {"detail": "FILE_EXTENSION_NOT_ALLOWED"}

        token_name = f"{uuid.uuid4()}.{extension}"
        generated_name = f"{BASE_DIR}/static/images/{token_name}"
        file_content = await file.read()

        with open(generated_name, "wb") as f:
            f.write(file_content)

        # Pillow
        img = Image.open(generated_name)
        img.save(generated_name, optimize=True)

        user.photo = token_name
        session.add(user)
        await session.commit()

    @router.get(
        "/all",
        name="get_users",
        response_model=Page[UserRead],
        dependencies=[Depends(get_current_active_user)],
    )
    async def get_users(
        full_name: str = Query(None, description="Filter users by full name"),
        email: str = Query(None, description="Filter users by email"),
        position: Position = Query(None, description="Filter users by position"),
        session: AsyncSession = Depends(get_async_session),
    ) -> Page[UserRead]:
        query = select(User)
        if full_name:
            parts = full_name.split()
            if len(parts) == 2:
                first_name, last_name = parts
                if first_name:
                    query = query.filter(User.first_name.contains(first_name))
                if last_name:
                    query = query.filter(User.last_name.contains(last_name))
            elif len(parts) == 1:
                name = parts[0]
                query = query.filter(
                    or_(User.first_name.contains(name), User.last_name.contains(name))
                )
        if email:
            query = query.filter(User.email.contains(email))
        if position:
            query = query.filter(User.position.contains(position))

        return await paginate(session, query)

    # @router.get(
    #     "/{id}",
    #     response_model=user_schema,
    #     dependencies=[Depends(get_current_superuser)],
    #     name="users:user",
    #     responses={
    #         status.HTTP_401_UNAUTHORIZED: {
    #             "description": "Missing token or inactive user.",
    #         },
    #         status.HTTP_403_FORBIDDEN: {
    #             "description": "Not a superuser.",
    #         },
    #         status.HTTP_404_NOT_FOUND: {
    #             "description": "The user does not exist.",
    #         },
    #     },
    # )
    # async def get_user(user=Depends(get_user_or_404)):
    #     return schemas.model_validate(user_schema, user)
    #
    # @router.patch(
    #     "/{id}",
    #     response_model=user_schema,
    #     dependencies=[Depends(get_current_superuser)],
    #     name="users:patch_user",
    #     responses={
    #         status.HTTP_401_UNAUTHORIZED: {
    #             "description": "Missing token or inactive user.",
    #         },
    #         status.HTTP_403_FORBIDDEN: {
    #             "description": "Not a superuser.",
    #         },
    #         status.HTTP_404_NOT_FOUND: {
    #             "description": "The user does not exist.",
    #         },
    #         status.HTTP_400_BAD_REQUEST: {
    #             "model": ErrorModel,
    #             "content": {
    #                 "application/json": {
    #                     "examples": {
    #                         ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
    #                             "summary": "A user with this email already exists.",
    #                             "value": {
    #                                 "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
    #                             },
    #                         },
    #                         ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
    #                             "summary": "Password validation failed.",
    #                             "value": {
    #                                 "detail": {
    #                                     "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
    #                                     "reason": "Password should be"
    #                                     "at least 3 characters",
    #                                 }
    #                             },
    #                         },
    #                     }
    #                 }
    #             },
    #         },
    #     },
    # )
    # async def update_user(
    #     user_update: user_update_schema,  # type: ignore
    #     request: Request,
    #     user=Depends(get_user_or_404),
    #     user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    # ):
    #     try:
    #         user = await user_manager.update(
    #             user_update, user, safe=False, request=request
    #         )
    #         return schemas.model_validate(user_schema, user)
    #     except exceptions.InvalidPasswordException as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail={
    #                 "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
    #                 "reason": e.reason,
    #             },
    #         )
    #     except exceptions.UserAlreadyExists:
    #         raise HTTPException(
    #             status.HTTP_400_BAD_REQUEST,
    #             detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
    #         )
    #
    # @router.delete(
    #     "/{id}",
    #     status_code=status.HTTP_204_NO_CONTENT,
    #     response_class=Response,
    #     dependencies=[Depends(get_current_superuser)],
    #     name="users:delete_user",
    #     responses={
    #         status.HTTP_401_UNAUTHORIZED: {
    #             "description": "Missing token or inactive user.",
    #         },
    #         status.HTTP_403_FORBIDDEN: {
    #             "description": "Not a superuser.",
    #         },
    #         status.HTTP_404_NOT_FOUND: {
    #             "description": "The user does not exist.",
    #         },
    #     },
    # )
    # async def delete_user(
    #     request: Request,
    #     user=Depends(get_user_or_404),
    #     user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    # ):
    #     await user_manager.delete(user, request=request)
    #     return None

    return router

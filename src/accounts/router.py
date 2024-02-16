from fastapi import APIRouter

from src.accounts.config import auth_backend
from src.accounts.manager import fastapi_users
from src.accounts.schemas import User, UserCreate, UserUpdate, UserRead

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(backend=auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(User, UserUpdate),
    prefix="/users",
    tags=["users"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

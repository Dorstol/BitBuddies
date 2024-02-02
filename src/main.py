from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from src.accounts.models import User
from src.accounts.config import auth_backend
from src.accounts.manager import get_user_manager
from src.accounts.schemas import UserRead, UserCreate, UserUpdate

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(title="BitBuddies")

app.include_router(
    fastapi_users.get_auth_router(backend=auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

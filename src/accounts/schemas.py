from typing import Optional

from fastapi_users import models
from fastapi_users.schemas import CreateUpdateDictModel, BaseUser
from pydantic import EmailStr, Field

from src.accounts.models import Position


class UserRead(BaseUser[int]):
    """Base User model."""

    id: models.ID
    email: EmailStr
    position: Optional[Position]
    contact: Optional[str]
    is_active: bool = Field(exclude=True)
    is_superuser: bool = Field(exclude=True)
    is_verified: bool = Field(exclude=True)


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str


class UserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[Position] = None
    contact: Optional[str] = None


class User(UserRead):
    pass

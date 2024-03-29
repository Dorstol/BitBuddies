from typing import Optional

from fastapi_users import models
from fastapi_users.schemas import CreateUpdateDictModel, BaseUser
from pydantic import EmailStr, Field, BaseModel

from src.accounts.models import Position


class UserRead(BaseUser[int]):
    """Base User model."""

    id: models.ID
    first_name: str
    last_name: str
    email: EmailStr
    position: Position
    contact: str
    photo: str
    is_active: bool = Field(exclude=True)
    is_superuser: bool = Field(exclude=True)
    is_verified: bool = Field(exclude=True)


class UserCreate(CreateUpdateDictModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserUpdate(CreateUpdateDictModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    position: Optional[Position] = None
    contact: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class User(UserRead):
    pass

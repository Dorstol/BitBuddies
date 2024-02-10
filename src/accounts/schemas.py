from typing import Optional

from fastapi_users import models
from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr

from src.accounts.models import Position


class UserRead(schemas.BaseUser[int]):
    id: models.ID
    email: EmailStr
    position: Optional[Position]
    contact: Optional[str]


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

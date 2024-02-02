from typing import Optional

from fastapi_users import models
from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr
from src.accounts.models import Role


class UserRead(schemas.BaseUser[int]):
    id: models.ID
    email: EmailStr
    role: Optional[Role]
    contact: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str


class UserUpdate(CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    contact: Optional[str] = None

from enum import Enum, unique
from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


@unique
class Role(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DESIGNER = "Designer"
    PM = "Project Manager"
    QA = "QA"


class User(SQLAlchemyBaseUserTable[int], Base):
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role: Mapped[Optional[Role]]
    contact: Mapped[str] = mapped_column(Text(), nullable=True)
    # photo
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

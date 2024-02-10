from enum import Enum
from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Position(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DESIGNER = "Designer"
    PM = "Project Manager"
    QA = "QA"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    # first_name
    # last_name
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    position: Mapped[Optional[Position]]
    contact: Mapped[str] = mapped_column(Text(), nullable=True)
    # photo
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    teams: Mapped[list["Team"]] = relationship(
        back_populates="members",
        secondary="users_teams",
    )

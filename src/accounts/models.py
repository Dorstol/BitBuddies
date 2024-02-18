from enum import Enum

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Position(str, Enum):
    DEFAULT = ""
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DESIGNER = "Designer"
    PM = "Project Manager"
    QA = "QA"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(length=128),
        server_default="",
        default="",
    )
    last_name: Mapped[str] = mapped_column(
        String(length=128),
        server_default="",
        default="",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False,
    )
    position: Mapped[Position] = mapped_column(
        server_default=Position.DEFAULT,
        default=Position.DEFAULT,
    )
    contact: Mapped[str] = mapped_column(
        Text(),
        server_default="",
        default="",
    )
    photo: Mapped[str] = mapped_column(
        String(length=256),
        server_default="",
        default="",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    teams: Mapped[list["Team"]] = relationship(
        back_populates="members",
        secondary="users_teams",
    )

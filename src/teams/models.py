from enum import Enum

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class StatusChoices(str, Enum):
    INITIATION = "Initiation"
    PLANNING = "Planning"
    DESIGN = "Design"
    DEVELOPMENT = "Development"
    TESTING = "Testing"
    READY = "Ready"


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(
        String(length=256),
        nullable=False,
        index=True,
    )
    project_name: Mapped[str] = mapped_column(String(length=256))
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[StatusChoices] = mapped_column(
        default=StatusChoices.INITIATION,
        server_default=StatusChoices.INITIATION,
    )
    members: Mapped[list["User"]] = relationship(
        back_populates="teams",
        secondary="users_teams",
    )


class UserTeam(Base):
    __tablename__ = "users_teams"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )

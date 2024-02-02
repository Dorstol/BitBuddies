from enum import Enum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class StatusChoices(str, Enum):
    INITIATION = "Initiation"
    PLANNING = "Planning"
    DESIGN = "Design"
    DEVELOPMENT = "Development"
    TESTING = "Testing"
    READY = "Ready"


class Team(Base):
    title: Mapped[str] = mapped_column(
        String(length=256),
        nullable=False,
        index=True,
    )
    project_name: Mapped[str] = mapped_column(String(length=256))
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[StatusChoices] = mapped_column(
        server_default=StatusChoices.INITIATION
    )
    # user

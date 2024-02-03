from pydantic import BaseModel

from src.accounts.schemas import UserRead
from src.teams.models import StatusChoices


class TeamRead(BaseModel):
    id: int
    title: str
    project_name: str
    description: str
    status: StatusChoices
    members: list[UserRead]

    class Config:
        from_attributes = True

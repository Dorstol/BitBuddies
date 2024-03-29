from pydantic import BaseModel, ConfigDict

from src.accounts.schemas import UserRead
from src.teams.models import StatusChoices


class TeamBase(BaseModel):
    title: str
    project_name: str
    description: str
    owner_id: int
    status: StatusChoices
    members: list[UserRead]


class TeamCreate(BaseModel):
    title: str
    project_name: str
    description: str


class TeamUpdate(TeamCreate):
    pass


class TeamUpdatePartial(TeamCreate):
    title: str | None = None
    project_name: str | None = None
    description: str | None = None
    status: StatusChoices | None = None


class Team(TeamBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.crud import get_user_by_id
from src.accounts.models import User
from src.database import get_async_session
from src.teams import crud
from src.teams.dependencies import team_by_id
from src.teams.schemas import Team, TeamCreate, TeamUpdatePartial

router = APIRouter()


@router.get("/", response_model=list[Team])
async def get_teams(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_teams(session=session)


@router.get("/{team_id}/", response_model=Team)
async def get_team(team: Team = Depends(team_by_id)):
    return team


@router.post(
    "/",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_in: TeamCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.create_team(
        session=session,
        team_in=team_in,
    )


@router.patch("/{team_id}/")
async def update_team_partial(
    team_update: TeamUpdatePartial,
    team: Team = Depends(team_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update_team(
        session=session,
        team=team,
        team_update=team_update,
    )


@router.delete("/{team_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team: Team = Depends(team_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    await crud.delete_team(session=session, team=team)

from fastapi import APIRouter, Depends, status, Query
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.dependencies import get_user_by_id
from src.accounts.manager import fastapi_users
from src.accounts.schemas import User
from src.database import get_async_session
from src.teams import crud
from src.teams.dependencies import team_by_id
from src.teams.models import StatusChoices
from src.teams.schemas import Team, TeamCreate, TeamUpdatePartial

router = APIRouter()

current_active_verified_user = fastapi_users.current_user()


@router.get(
    "",
    response_model=Page[Team],
    dependencies=[
        Depends(current_active_verified_user),
    ],
)
async def get_teams(
    title: str = Query(None, description="filter teams by title"),
    project_name: str = Query(None, description="filter teams by project name."),
    status: StatusChoices = Query(None, description="filter teams by status"),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.get_teams(
        title=title, project_name=project_name, status=status, session=session
    )


@router.get(
    "/{team_id}",
    response_model=Team,
    dependencies=[
        Depends(current_active_verified_user),
    ],
)
async def get_team(team: Team = Depends(team_by_id)):
    return team


@router.post(
    "",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_in: TeamCreate,
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.create_team(
        team_in=team_in,
        user_id=user.id,
        session=session,
    )


@router.patch(
    "/{team_id}",
    response_model=Team,
    status_code=status.HTTP_200_OK,
)
async def update_team_partial(
    team_update: TeamUpdatePartial,
    team: Team = Depends(team_by_id),
    user: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.update_team(
        session=session,
        user_id=user.id,
        team=team,
        team_update=team_update,
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_team(
    user: User = Depends(current_active_verified_user),
    team: Team = Depends(team_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.delete_team(
        session=session,
        team=team,
        user=user,
    )


@router.post(
    "/join/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=Team,
)
async def join_team(
    user: User = Depends(current_active_verified_user),
    team: Team = Depends(team_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.join_team(
        team=team,
        user=user,
        session=session,
    )


@router.delete(
    "/leave/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=Team,
)
async def leave_team(
    user: User = Depends(current_active_verified_user),
    team: Team = Depends(team_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    return await crud.leave_team(
        user=user,
        team=team,
        session=session,
    )


@router.delete(
    "/remove_member/{team_id}/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Team,
)
async def remove_member_by_owner(
    team_id: int,
    user_id: int,
    owner: User = Depends(current_active_verified_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_user_by_id(user_id=user_id, session=session)
    team = await team_by_id(team_id=team_id, session=session)
    return await crud.remove_member(
        member=user,
        team=team,
        owner=owner,
        session=session,
    )

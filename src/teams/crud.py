from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.accounts.models import User
from src.teams.models import Team, UserTeam
from src.teams.schemas import TeamCreate, TeamUpdatePartial


async def get_teams(session: AsyncSession) -> list[Team]:
    stmt = select(Team).options(joinedload(Team.members))
    result: Result = await session.execute(stmt)
    teams = result.unique().scalars().all()
    return list(teams)


async def get_team(session: AsyncSession, team_id: int) -> Team | None:
    stmt = select(Team).where(Team.id == team_id).options(joinedload(Team.members))
    result: Result = await session.execute(stmt)
    team = result.unique().scalar_one()
    return team


async def create_team(session: AsyncSession, team_in: TeamCreate) -> Team:
    team = Team(
        title=team_in.title,
        project_name=team_in.project_name,
        description=team_in.description,
    )
    session.add(team)
    await session.flush()
    user_team = UserTeam(user_id=team_in.owner_id, team_id=team.id)
    session.add(user_team)
    await session.commit()
    return await get_team(session=session, team_id=team.id)


async def update_team(
    session: AsyncSession,
    team: Team,
    team_update: TeamUpdatePartial,
):
    for name, value in team_update.model_dump(exclude_unset=True).items():
        setattr(team, name, value)
    await session.commit()
    return team


async def delete_team(session: AsyncSession, team: Team) -> None:
    await session.delete(team)
    await session.commit()


async def join_team(
    team: Team,
    user_id: int,
    session: AsyncSession,
):
    if len(team.members) == team.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Max team members!"
        )
    user_team = UserTeam(user_id=user_id, team_id=team.id)
    session.add(user_team)
    await session.commit()
    return user_team


async def leave_team(
    team: Team,
    user: User,
    session: AsyncSession,
) -> None:
    if user and team:
        team.members.remove(user)
    await session.commit()

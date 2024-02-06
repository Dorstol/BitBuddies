from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.teams.models import Team
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
    team = Team(**team_in.model_dump())
    session.add(team)
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

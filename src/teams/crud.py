from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.teams.models import Team


async def get_teams(session: AsyncSession) -> list[Team]:
    stmt = select(Team).options(joinedload(Team.members))
    result: Result = await session.execute(stmt)
    teams = result.unique().scalars().all()
    return list(teams)

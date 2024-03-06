from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import User
from src.teams.models import UserTeam, Team


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    user: User | None = await session.scalar(stmt)
    return user


async def get_user_by_email(user_email: str, session: AsyncSession):
    stmt = select(User).where(User.email == user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_teams(user_id: int, session: AsyncSession):
    stmt = select(Team).join(UserTeam).where(UserTeam.user_id == user_id)
    result = await session.execute(stmt)
    teams = result.scalars().all()
    return teams

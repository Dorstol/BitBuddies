from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import User
from src.teams.models import UserTeam, Team, StatusChoices


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    user: User | None = await session.scalar(stmt)
    return user


async def get_user_by_email(user_email: str, session: AsyncSession):
    stmt = select(User).where(User.email == user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_teams(
    is_paginate: bool,
    user_id: int,
    session: AsyncSession,
    title: str = None,
    project_name: str = None,
    status: StatusChoices = None,
):
    query = select(Team).join(UserTeam).where(UserTeam.user_id == user_id)

    if is_paginate:
        if title:
            query = query.filter(Team.title.contains(title))
        if project_name:
            query = query.filter(Team.project_name.contains(project_name))
        if status:
            query = query.filter(Team.status.contains(status))

        return await paginate(session, query)
    else:
        result = await session.execute(query)
        teams = result.scalars().all()
        return teams

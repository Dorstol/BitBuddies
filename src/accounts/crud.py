from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import User


async def get_user(session: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    user: User | None = await session.scalar(stmt)
    return user


async def get_user_by_email(user_email: str, session: AsyncSession):
    stmt = select(User).where(User.email == user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user

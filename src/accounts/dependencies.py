from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.accounts.models import User
from src.accounts.crud import get_user
from typing import Optional

from src.database import get_async_session


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """
    Dependency function to retrieve a user by their ID.

    Args:
    - user_id (int): The ID of the user to retrieve.
    - session (AsyncSession): The asynchronous database session.

    Returns:
    - Optional[User]: The user if found, otherwise None.
    """
    user = await get_user(session=session, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

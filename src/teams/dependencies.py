from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.teams import crud
from src.teams.models import Team


async def team_by_id(
    team_id: Annotated[int, Path],
    session: AsyncSession = Depends(get_async_session),
) -> Team:
    team = await crud.get_team(session=session, team_id=team_id)
    if team is not None:
        return team
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Team {team_id} not found!",
    )

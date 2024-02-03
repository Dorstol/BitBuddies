from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.teams import crud
from src.teams.schemas import TeamRead

router = APIRouter()


@router.get("/", response_model=list[TeamRead])
async def get_teams(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_teams(session=session)

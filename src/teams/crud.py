from fastapi import HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.accounts.crud import get_user_teams
from src.accounts.models import User
from src.teams.models import Team, UserTeam, StatusChoices
from src.teams.schemas import TeamCreate, TeamUpdatePartial


async def get_teams(
    session: AsyncSession,
    title: str,
    project_name: str,
    status: StatusChoices,
):
    query = select(Team).options(joinedload(Team.members))
    if title:
        query = query.filter(Team.title.contains(title))
    if project_name:
        query = query.filter(Team.project_name.contains(project_name))
    if status:
        query = query.filter(Team.status.contains(status))

    return await paginate(session, query)


async def get_team(session: AsyncSession, team_id: int, join: bool = None):
    try:
        stmt = select(Team).where(Team.id == team_id).options(joinedload(Team.members))
        result: Result = await session.execute(stmt)
        team = result.unique().scalar_one()
        if join:
            await session.refresh(team)
        return team
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DOES_NOT_EXIST",
        )


async def create_team(
    team_in: TeamCreate,
    user_id: int,
    session: AsyncSession,
):
    teams = await get_user_teams(user_id=user_id, session=session, is_paginate=False)
    for team in teams:
        if team.owner_id == user_id and team.status != "Ready":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CANNOT_CREATE_TEAM",
            )
    team = Team(
        title=team_in.title,
        project_name=team_in.project_name,
        description=team_in.description,
    )
    team.owner_id = user_id
    session.add(team)
    await session.flush()
    user_team = UserTeam(user_id=user_id, team_id=team.id)
    session.add(user_team)
    await session.commit()
    return await get_team(session=session, team_id=team.id)


async def update_team(
    session: AsyncSession,
    team: Team,
    user_id: int,
    team_update: TeamUpdatePartial,
):
    if team.owner_id == user_id:
        for name, value in team_update.model_dump(exclude_unset=True).items():
            setattr(team, name, value)
        await session.commit()
        return team
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NOT_OWNER",
        )


async def delete_team(
    session: AsyncSession,
    team: Team,
    user: User,
):
    if team.owner_id == user.id:
        await session.delete(team)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NOT_OWNER",
        )


async def join_team(
    team: Team,
    user: User,
    session: AsyncSession,
):
    if len(team.members) == team.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MAX_MEMBERS",
        )
    if user in team.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ALREADY_IN_TEAM",
        )
    user_team = UserTeam(user_id=user.id, team_id=team.id)
    session.add(user_team)
    await session.commit()
    return await get_team(session=session, team_id=team.id, join=True)


async def leave_team(
    team: Team,
    user: User,
    session: AsyncSession,
):
    if user and team:
        if team.owner_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OWNER_CANNOT_LEAVE",
            )
        if user in team.members:
            team.members.remove(user)
            await session.commit()
            return await get_team(session=session, team_id=team.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NOT_TEAM_MEMBER",
            )


async def remove_member(
    member: User,
    team: Team,
    owner: User,
    session: AsyncSession,
):
    try:
        if None not in (member, team, owner):
            if team.owner_id == member.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OWNER_CANNOT_LEAVE",
                )
            if team.owner_id == owner.id:
                team.members.remove(member)
                await session.commit()
                return await get_team(session=session, team_id=team.id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="NOT_OWNER",
                )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="BAD_REQUEST"
        )

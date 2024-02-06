from fastapi import FastAPI

from src.accounts.router import router as accounts_router
from src.teams.router import router as teams_router

app = FastAPI(title="BitBuddies")

app.include_router(accounts_router)


app.include_router(
    teams_router,
    prefix="/teams",
    tags=["teams"],
)

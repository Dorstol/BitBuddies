from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.accounts.router import router as accounts_router
from src.teams.router import router as teams_router

app = FastAPI(title="BitBuddies")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router)


app.include_router(
    teams_router,
    prefix="/teams",
    tags=["teams"],
)

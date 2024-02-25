from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from src.config import BASE_DIR

from src.accounts.router import router as accounts_router
from src.teams.router import router as teams_router

app = FastAPI(title="BitBuddies")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")
add_pagination(app)

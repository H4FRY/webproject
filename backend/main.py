from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routes.auth import router as auth_router
from api.routes.oauth import router as oauth_router
from core.config import settings

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(oauth_router)


@app.get("/")
async def root():
    return {"message": "Backend is running"}
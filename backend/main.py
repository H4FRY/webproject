import os
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from pwdlib import PasswordHash
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth

from bd.config import SessionLocal
from bd.modeldb import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

password_hash = PasswordHash.recommended()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)

LOGIN_REGEX = re.compile(r"^[A-Za-z0-9._-]{3,32}$")
PASSWORD_UPPER_REGEX = re.compile(r"[A-Z]")
PASSWORD_LOWER_REGEX = re.compile(r"[a-z]")
PASSWORD_DIGIT_REGEX = re.compile(r"\d")
PASSWORD_SPECIAL_REGEX = re.compile(r"[^\w\s]")


class RegisterRequest(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        if not LOGIN_REGEX.fullmatch(value):
            raise ValueError(
                "Логин: длина 3–32, только латиница, цифры, '.', '_', '-'"
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not PASSWORD_UPPER_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 заглавную букву")
        if not PASSWORD_LOWER_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 строчную букву")
        if not PASSWORD_DIGIT_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 цифру")
        if not PASSWORD_SPECIAL_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 спецсимвол")
        return value


class LoginRequest(BaseModel):
    login: str
    password: str


@app.get("/")
async def root():
    return {"message": "Backend is running"}


@app.post("/register")
async def register(user: RegisterRequest):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.login == user.login)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Такой логин уже существует")

        hashed_password = password_hash.hash(user.password)

        new_user = User(
            login=user.login,
            password_hash=hashed_password
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return {
            "message": "Пользователь успешно зарегистрирован",
            "id": new_user.id,
            "login": new_user.login
        }


@app.post("/login")
async def login(user: LoginRequest):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.login == user.login)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            raise HTTPException(status_code=400, detail="Неверный логин или пароль")

        if not db_user.password_hash:
            raise HTTPException(
                status_code=400,
                detail="Для этого аккаунта используйте вход через GitHub"
            )

        if not password_hash.verify(user.password, db_user.password_hash):
            raise HTTPException(status_code=400, detail="Неверный логин или пароль")

        return {
            "message": "Вход выполнен успешно",
            "id": db_user.id,
            "login": db_user.login
        }


@app.get("/auth/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth/github/callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    github_user = resp.json()

    github_id = str(github_user["id"])
    github_login = github_user["login"]
    avatar_url = github_user.get("avatar_url")

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.github_id == github_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            # если хочешь, можно ещё проверить, не занят ли login
            user = User(
                github_id=github_id,
                github_login=github_login,
                login=github_login,
                password_hash=None,
                avatar_url=avatar_url,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return {
            "message": "Вход через GitHub выполнен успешно",
            "id": user.id,
            "login": user.login,
            "github_login": user.github_login,
            "avatar_url": user.avatar_url,
        }
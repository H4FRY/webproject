import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from pwdlib import PasswordHash
from fastapi.middleware.cors import CORSMiddleware

from bd.config import SessionLocal
from bd.modeldb import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

password_hash = PasswordHash.recommended()

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

        if not password_hash.verify(user.password, db_user.password_hash):
            raise HTTPException(status_code=400, detail="Неверный логин или пароль")

        return {
            "message": "Вход выполнен успешно",
            "id": db_user.id,
            "login": db_user.login
        }
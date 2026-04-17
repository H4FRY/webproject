import re
import io
import base64
import secrets

import pyotp
import qrcode

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from pwdlib import PasswordHash
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from urllib.parse import urlencode

from bd.config import SessionLocal
from bd.modeldb import User

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="Qw8L7mYgT3rP0xK9nV2cA5uH1jD6sF4zB8wR2tN7"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
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

# Временно захардкожено для локальной проверки
GITHUB_CLIENT_ID = "Ov23liQf2xLci0jwiHAc"
GITHUB_CLIENT_SECRET = "5e5247a749e2bd8d605adcfcc3e6ff9333236500"

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


def make_qr_base64(data: str) -> str:
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


async def generate_unique_login(session, base_login: str) -> str:
    candidate = (base_login or "github_user")[:32]

    result = await session.execute(select(User).where(User.login == candidate))
    existing = result.scalar_one_or_none()
    if existing is None:
        return candidate

    for _ in range(100):
        suffix = secrets.token_hex(2)
        candidate = f"{base_login[:27]}_{suffix}"[:32]
        result = await session.execute(select(User).where(User.login == candidate))
        existing = result.scalar_one_or_none()
        if existing is None:
            return candidate

    raise HTTPException(
        status_code=500,
        detail="Не удалось сгенерировать уникальный логин"
    )


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


class RegisterConfirm2FARequest(BaseModel):
    login: str
    otp_code: str


class LoginRequest(BaseModel):
    login: str
    password: str


class Verify2FARequest(BaseModel):
    login: str
    otp_code: str


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

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        provisioning_uri = totp.provisioning_uri(
            name=user.login,
            issuer_name="POAIBOT"
        )

        qr_code_base64 = make_qr_base64(provisioning_uri)

        new_user = User(
            login=user.login,
            password_hash=hashed_password,
            totp_secret=secret,
            is_2fa_enabled=False,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return {
            "message": "Пользователь создан. Подтвердите 2FA-код",
            "id": new_user.id,
            "login": new_user.login,
            "qr_code_base64": qr_code_base64,
            "otpauth_url": provisioning_uri,
        }


@app.post("/register/confirm-2fa")
async def register_confirm_2fa(data: RegisterConfirm2FARequest):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.login == data.login)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if not user.totp_secret:
            raise HTTPException(status_code=400, detail="2FA не настроен")

        totp = pyotp.TOTP(user.totp_secret)

        if not totp.verify(data.otp_code):
            raise HTTPException(status_code=400, detail="Неверный код подтверждения")

        user.is_2fa_enabled = True
        await session.commit()

        return {
            "message": "Регистрация завершена, 2FA успешно включен"
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

        if db_user.is_2fa_enabled:
            return {
                "requires_2fa": True,
                "login": db_user.login,
                "message": "Введите код из приложения-аутентификатора"
            }

        return {
            "requires_2fa": False,
            "message": "Вход выполнен успешно",
            "id": db_user.id,
            "login": db_user.login
        }


@app.post("/login/verify-2fa")
async def login_verify_2fa(data: Verify2FARequest):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.login == data.login)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            raise HTTPException(status_code=400, detail="Пользователь не найден")

        if not db_user.is_2fa_enabled or not db_user.totp_secret:
            raise HTTPException(status_code=400, detail="2FA не включен")

        totp = pyotp.TOTP(db_user.totp_secret)

        if not totp.verify(data.otp_code):
            raise HTTPException(status_code=400, detail="Неверный одноразовый код")

        return {
            "message": "Вход выполнен успешно",
            "id": db_user.id,
            "login": db_user.login
        }


@app.get("/auth/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


from urllib.parse import urlencode

@app.get("/auth/github/callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)

    resp = await oauth.github.get("user", token=token)
    github_user = resp.json()

    github_id = str(github_user["id"])
    github_login = github_user.get("login") or f"github_{github_id}"
    github_email = github_user.get("email")

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.github_id == github_id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            unique_login = await generate_unique_login(session, github_login)

            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=unique_login,
                issuer_name="POAIBOT"
            )
            qr_code_base64 = make_qr_base64(provisioning_uri)

            db_user = User(
                login=unique_login,
                password_hash=None,
                github_id=github_id,
                github_login=github_login,
                github_email=github_email,
                totp_secret=secret,
                is_2fa_enabled=False,
            )

            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            params = urlencode({
                "login": db_user.login,
                "qr": qr_code_base64,
                "otpauth": provisioning_uri,
            })

            return RedirectResponse(
                url=f"http://localhost:5173/register/confirm-2fa?{params}"
            )

        if not db_user.is_2fa_enabled:
            if not db_user.totp_secret:
                secret = pyotp.random_base32()
                db_user.totp_secret = secret
                await session.commit()

            totp = pyotp.TOTP(db_user.totp_secret)
            provisioning_uri = totp.provisioning_uri(
                name=db_user.login,
                issuer_name="POAIBOT"
            )
            qr_code_base64 = make_qr_base64(provisioning_uri)

            params = urlencode({
                "login": db_user.login,
                "qr": qr_code_base64,
                "otpauth": provisioning_uri,
            })

            return RedirectResponse(
                url=f"http://localhost:5173/register/confirm-2fa?{params}"
            )

        params = urlencode({
            "login": db_user.login,
        })

        return RedirectResponse(
            url=f"http://localhost:5173/login/verify-2fa?{params}"
        )
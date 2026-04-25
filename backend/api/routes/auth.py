from fastapi import APIRouter, Depends, Request, Response

from api.deps import get_current_user, get_session
from core.config import settings
from core.cookie import clear_auth_cookies, set_auth_cookies
from schemas.auth import (
    LoginRequest,
    RegisterConfirm2FARequest,
    RegisterRequest,
    Verify2FARequest,
)
from services.auth_service import AuthService
from services.session_service import SessionService

router = APIRouter()


@router.post("/register")
async def register(user: RegisterRequest, session=Depends(get_session)):
    service = AuthService(session)
    return await service.register(user.login, user.email, user.password)


@router.post("/register/confirm-2fa")
async def register_confirm_2fa(
    data: RegisterConfirm2FARequest,
    response: Response,
    session=Depends(get_session),
):
    auth_service = AuthService(session)
    session_service = SessionService()

    db_user = await auth_service.confirm_register_2fa(data.email, data.otp_code)

    tokens = await session_service.create_auth_tokens(
        user_id=db_user.id,
        email=db_user.email,
    )

    set_auth_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {
        "message": "Регистрация завершена, 2FA успешно включен",
        "id": db_user.id,
        "login": db_user.login,
        "email": db_user.email,
    }


@router.post("/login")
async def login(user: LoginRequest, response: Response, session=Depends(get_session)):
    auth_service = AuthService(session)
    session_service = SessionService()

    result = await auth_service.login(user.email, user.password)

    if result["requires_2fa"]:
        return result

    db_user = result["user"]

    tokens = await session_service.create_auth_tokens(
        user_id=db_user.id,
        email=db_user.email,
    )

    set_auth_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {
        "requires_2fa": False,
        "message": "Вход выполнен успешно",
        "id": db_user.id,
        "login": db_user.login,
        "email": db_user.email,
    }


@router.post("/login/verify-2fa")
async def login_verify_2fa(data: Verify2FARequest, response: Response, session=Depends(get_session)):
    auth_service = AuthService(session)
    session_service = SessionService()

    db_user = await auth_service.verify_login_2fa(data.email, data.otp_code)

    tokens = await session_service.create_auth_tokens(
        user_id=db_user.id,
        email=db_user.email,
    )

    set_auth_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {
        "message": "Вход выполнен успешно",
        "id": db_user.id,
        "login": db_user.login,
        "email": db_user.email,
    }


@router.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    session_service = SessionService()

    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token отсутствует")

    tokens = await session_service.refresh_tokens(refresh_token)

    set_auth_cookies(
        response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )

    return {"message": "Сессия обновлена"}


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_service = SessionService()

    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    await session_service.logout(refresh_token)

    clear_auth_cookies(response)
    return {"message": "Выход выполнен успешно"}


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "login": current_user.login,
        "email": current_user.email,
        "github_login": current_user.github_login,
    }


@router.get("/protected")
async def protected(current_user=Depends(get_current_user)):
    return {
        "message": "Доступ разрешен",
        "user": current_user.email,
    }
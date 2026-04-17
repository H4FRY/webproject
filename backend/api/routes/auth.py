from fastapi import APIRouter, Depends

from api.deps import get_session
from schemas.auth import (
    RegisterRequest,
    RegisterConfirm2FARequest,
    LoginRequest,
    Verify2FARequest,
)
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register")
async def register(user: RegisterRequest, session=Depends(get_session)):
    service = AuthService(session)
    return await service.register(user.login, user.email, user.password)


@router.post("/register/confirm-2fa")
async def register_confirm_2fa(data: RegisterConfirm2FARequest, session=Depends(get_session)):
    service = AuthService(session)
    return await service.confirm_register_2fa(data.email, data.otp_code)


@router.post("/login")
async def login(user: LoginRequest, session=Depends(get_session)):
    service = AuthService(session)
    return await service.login(user.email, user.password)


@router.post("/login/verify-2fa")
async def login_verify_2fa(data: Verify2FARequest, session=Depends(get_session)):
    service = AuthService(session)
    return await service.verify_login_2fa(data.email, data.otp_code)
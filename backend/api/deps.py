from fastapi import Depends, HTTPException, Request, status

from bd.config import SessionLocal
from repositories.user_repository import UserRepository
from core.jwt import decode_token
from core.config import settings


async def get_session():
    async with SessionLocal() as session:
        yield session


async def get_current_user(request: Request, session=Depends(get_session)):
    token = request.cookies.get(settings.access_cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token отсутствует",
        )

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный access token",
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный access token payload",
        )

    repo = UserRepository(session)
    user = await repo.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    return user
import secrets

from fastapi import HTTPException, Request, status

from core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self):
        self.repo = SessionRepository()

    async def create_auth_tokens(self, user_id: int, email: str) -> dict:
        session_id = secrets.token_urlsafe(32)

        await self.repo.create_session(
            session_id=session_id,
            user_id=user_id,
            email=email,
        )

        access_token = create_access_token(user_id, email, session_id)
        refresh_token = create_refresh_token(user_id, email, session_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id,
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный refresh token",
            )

        session_id = payload.get("sid")
        user_id = payload.get("uid")
        email = payload.get("sub")

        if not session_id or not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный refresh token payload",
            )

        session = await self.repo.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия не найдена или истекла",
            )

        await self.repo.refresh_session_ttl(session_id)

        new_access_token = create_access_token(user_id, email, session_id)
        new_refresh_token = create_refresh_token(user_id, email, session_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        try:
            payload = decode_token(refresh_token)
        except HTTPException:
            return

        session_id = payload.get("sid")
        if session_id:
            await self.repo.delete_session(session_id)
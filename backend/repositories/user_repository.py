import secrets

from fastapi import HTTPException
from sqlalchemy import select

from bd.modeldb import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_github_id(self, github_id: str):
        result = await self.session.execute(
            select(User).where(User.github_id == github_id)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str):
        result = await self.session.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str):
        result = await self.session.execute(
            select(User).where(User.login == login)
        )
        return result.scalar_one_or_none()

    async def create_user(self, **kwargs):
        user = User(**kwargs)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def commit(self):
        await self.session.commit()

    async def generate_unique_login(self, base_login: str) -> str:
        candidate = (base_login or "github_user")[:32]

        existing = await self.get_by_login(candidate)
        if existing is None:
            return candidate

        for _ in range(100):
            suffix = secrets.token_hex(2)
            candidate = f"{base_login[:27]}_{suffix}"[:32]
            existing = await self.get_by_login(candidate)
            if existing is None:
                return candidate

        raise HTTPException(
            status_code=500,
            detail="Не удалось сгенерировать уникальный логин"
        )
from sqlalchemy import select
from bd.modeldb import Chat


class ChatRepository:
    def __init__(self, session):
        self.session = session

    async def create_chat(self, user_id: int, title: str):
        chat = Chat(user_id=user_id, title=title or "Новый чат")
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_user_chats(self, user_id: int):
        result = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()

    async def get_chat_by_id(self, chat_id: int, user_id: int):
        result = await self.session.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_chat(self, chat):
        await self.session.delete(chat)
        await self.session.commit()

    async def commit(self):
        await self.session.commit()
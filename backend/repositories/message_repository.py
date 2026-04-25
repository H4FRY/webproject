from sqlalchemy import select
from bd.modeldb import Message


class MessageRepository:
    def __init__(self, session):
        self.session = session

    async def create_message(self, chat_id: int, role: str, content: str):
        message = Message(chat_id=chat_id, role=role, content=content)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_chat_messages(self, chat_id: int):
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
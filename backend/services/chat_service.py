from fastapi import HTTPException

from repositories.chat_repository import ChatRepository
from repositories.message_repository import MessageRepository
from services.llm_service import LLMService


class ChatService:
    def __init__(self, session):
        self.chat_repo = ChatRepository(session)
        self.message_repo = MessageRepository(session)
        self.llm_service = LLMService()

    async def create_chat(self, user_id: int, title: str | None):
        return await self.chat_repo.create_chat(user_id=user_id, title=title or "Новый чат")

    async def list_chats(self, user_id: int):
        return await self.chat_repo.get_user_chats(user_id)

    async def get_chat(self, user_id: int, chat_id: int):
        chat = await self.chat_repo.get_chat_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")

        messages = await self.message_repo.get_chat_messages(chat_id)
        return chat, messages

    async def send_message(self, user_id: int, chat_id: int, content: str):
        chat = await self.chat_repo.get_chat_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")

        await self.message_repo.create_message(chat_id=chat_id, role="user", content=content)

        messages = await self.message_repo.get_chat_messages(chat_id)
        llm_messages = [{"role": m.role, "content": m.content} for m in messages if m.role in {"user", "assistant"}]

        answer = self.llm_service.generate_answer(llm_messages)

        assistant_message = await self.message_repo.create_message(
            chat_id=chat_id,
            role="assistant",
            content=answer,
        )

        return assistant_message

    async def delete_chat(self, user_id: int, chat_id: int):
        chat = await self.chat_repo.get_chat_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")

        await self.chat_repo.delete_chat(chat)
from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_session
from schemas.chat import (
    CreateChatRequest,
    SendMessageRequest,
    ChatResponse,
    MessageResponse,
)
from services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", response_model=ChatResponse)
async def create_chat(data: CreateChatRequest, session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    return await service.create_chat(current_user.id, data.title)


@router.get("", response_model=list[ChatResponse])
async def list_chats(session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    return await service.list_chats(current_user.id)


@router.get("/{chat_id}")
async def get_chat(chat_id: int, session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    chat, messages = await service.get_chat(current_user.id, chat_id)

    return {
        "id": chat.id,
        "title": chat.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(chat_id: int, data: SendMessageRequest, session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    return await service.send_message(current_user.id, chat_id, data.content)


@router.delete("/{chat_id}")
async def delete_chat(chat_id: int, session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    await service.delete_chat(current_user.id, chat_id)
    return {"message": "Чат удалён"}
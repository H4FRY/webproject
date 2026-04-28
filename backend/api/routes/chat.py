import asyncio
import threading

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

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
async def create_chat(
    data: CreateChatRequest,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
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
async def send_message(
    chat_id: int,
    data: SendMessageRequest,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = ChatService(session)
    return await service.send_message(current_user.id, chat_id, data.content)


@router.post("/{chat_id}/messages/stream")
async def send_message_stream(
    chat_id: int,
    data: SendMessageRequest,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    service = ChatService(session)

    llm_messages = await service.build_stream_context(
        current_user.id,
        chat_id,
        data.content,
    )

    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    collected_chunks: list[str] = []
    sentinel = object()

    def producer():
        try:
            for chunk in service.llm_service.stream_answer(llm_messages):
                collected_chunks.append(chunk)
                asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
        except Exception as exc:
            asyncio.run_coroutine_threadsafe(queue.put(exc), loop)
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(sentinel), loop)

    threading.Thread(target=producer, daemon=True).start()

    async def generate():
        while True:
            item = await queue.get()

            if item is sentinel:
                break

            if isinstance(item, Exception):
                raise item

            yield item

        full_answer = "".join(collected_chunks).strip()
        if full_answer:
            await service.save_assistant_message(chat_id, full_answer)

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/{chat_id}")
async def delete_chat(chat_id: int, session=Depends(get_session), current_user=Depends(get_current_user)):
    service = ChatService(session)
    await service.delete_chat(current_user.id, chat_id)
    return {"message": "Чат удалён"}
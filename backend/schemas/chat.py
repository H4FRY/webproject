from pydantic import BaseModel, Field
from datetime import datetime


class CreateChatRequest(BaseModel):
    title: str | None = "Новый чат"


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatDetailResponse(BaseModel):
    id: int
    title: str
    messages: list[MessageResponse]

    class Config:
        from_attributes = True
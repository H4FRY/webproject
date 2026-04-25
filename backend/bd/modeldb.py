from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from bd.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(32), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)

    password_hash = Column(String(255), nullable=True)

    github_id = Column(String(64), unique=True, nullable=True, index=True)
    github_login = Column(String(255), nullable=True)
    github_email = Column(String(255), nullable=True)

    totp_secret = Column(String(64), nullable=True)
    is_2fa_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    google_id = Column(String(128), unique=True, nullable=True, index=True)
    google_email = Column(String(255), nullable=True)
    google_name = Column(String(255), nullable=True)
    google_picture = Column(String(500), nullable=True)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="Новый чат")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(32), nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
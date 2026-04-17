from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
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
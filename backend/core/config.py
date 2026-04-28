import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    session_secret_key = os.getenv(
        "SESSION_SECRET_KEY",
        "change-me-session-secret",
    )
    cors_origins = parse_list(
        os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174")
    )

    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_scope = os.getenv("GOOGLE_SCOPE", "openid email profile")

    github_client_id = os.getenv("GITHUB_CLIENT_ID", "")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
    github_scope = os.getenv("GITHUB_SCOPE", "read:user user:email")

    issuer_name = os.getenv("ISSUER_NAME", "POAIBOT")

    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    access_cookie_name = os.getenv("ACCESS_COOKIE_NAME", "access_token")
    refresh_cookie_name = os.getenv("REFRESH_COOKIE_NAME", "refresh_token")

    cookie_secure = str_to_bool(os.getenv("COOKIE_SECURE"), False)
    cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax")




settings = Settings()
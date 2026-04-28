import os
from pathlib import Path

from dotenv import load_dotenv
import redis.asyncio as redis


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
)
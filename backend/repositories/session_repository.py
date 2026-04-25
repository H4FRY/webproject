import json

from core.redis_config import redis_client


class SessionRepository:
    def _key(self, session_id: str) -> str:
        return f"refresh_session:{session_id}"

    async def create_session(self, session_id: str, user_id: int, email: str) -> None:
        value = json.dumps({
            "session_id": session_id,
            "user_id": user_id,
            "email": email,
        })

        await redis_client.set(
            self._key(session_id),
            value,
            ex=30 * 24 * 60 * 60,
        )

    async def get_session(self, session_id: str):
        raw = await redis_client.get(self._key(session_id))
        if not raw:
            return None
        return json.loads(raw)

    async def delete_session(self, session_id: str) -> None:
        await redis_client.delete(self._key(session_id))

    async def refresh_session_ttl(self, session_id: str) -> None:
        await redis_client.expire(
            self._key(session_id),
            30 * 24 * 60 * 60,
        )
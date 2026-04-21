# パスとファイル名: wiwa/db/sessions_repository.py
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from wiwa.config import CSRF_TOKEN_BYTES
from wiwa.db.mongo import get_collection


class SessionsRepository:
    def __init__(self):
        self.collection = get_collection("sessions")

    def create(self, username: str, expires_days: int = 7) -> str:
        session_id = token_urlsafe(32)
        csrf_token = token_urlsafe(CSRF_TOKEN_BYTES)
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=expires_days)

        self.collection.insert_one({
            "session_id": session_id,
            "username": username,
            "csrf_token": csrf_token,
            "created_at": now,
            "expires_at": expires_at,
        })

        return session_id

    def find_by_session_id(self, session_id: str):
        if not session_id:
            return None

        session = self.collection.find_one({"session_id": session_id})
        if not session:
            return None

        expires_at = session.get("expires_at")
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)

            if expires_at < datetime.now(UTC):
                self.delete(session_id)
                return None

        return session

    def touch(self, session_id: str, expires_days: int = 7) -> None:
        if not session_id:
            return

        now = datetime.now(UTC)
        expires_at = now + timedelta(days=expires_days)

        self.collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "expires_at": expires_at,
                }
            }
        )

    def delete(self, session_id: str) -> None:
        if not session_id:
            return

        self.collection.delete_one({"session_id": session_id})

    def delete_expired(self) -> None:
        now = datetime.now(UTC)
        self.collection.delete_many({
            "expires_at": {"$lt": now}
        })
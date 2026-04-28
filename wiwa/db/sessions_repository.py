# パスとファイル名: wiwa/db/sessions_repository.py
# Path and filename: wiwa/db/sessions_repository.py

# セッションリポジトリ
# Session repository
#
# 概要
# Summary
#   セッションの作成・検証・更新・削除を管理する
#   Manage session creation, validation, update, and deletion
#
# 処理の流れ
# Flow
#   1. セッション生成
#      Create session
#   2. セッション取得・検証
#      Fetch and validate session
#   3. 有効期限更新
#      Update expiration
#   4. セッション削除
#      Delete session

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from wiwa.config import CSRF_TOKEN_BYTES
from wiwa.db.mongo import get_collection


class SessionsRepository:
    def __init__(self):
        """
        リポジトリ初期化
        Initialize repository
        """
        self.collection = get_collection("sessions")

    def create(self, username: str, expires_days: int = 7) -> str:
        """
        セッション作成
        Create session
        """
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
        """
        セッション取得・検証
        Fetch and validate session
        """
        if not session_id:
            return None

        session = self.collection.find_one({"session_id": session_id})
        if not session:
            return None

        expires_at = session.get("expires_at")

        # タイムゾーン補正
        # Normalize timezone
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)

            # 有効期限切れチェック
            # Expiration check
            if expires_at < datetime.now(UTC):
                self.delete(session_id)
                return None

        return session

    def touch(self, session_id: str, expires_days: int = 7) -> None:
        """
        セッション延命
        Refresh session expiration
        """
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
        """
        セッション削除
        Delete session
        """
        if not session_id:
            return

        self.collection.delete_one({"session_id": session_id})

    def delete_expired(self) -> None:
        """
        期限切れセッション削除
        Delete expired sessions
        """
        now = datetime.now(UTC)

        self.collection.delete_many({
            "expires_at": {"$lt": now}
        })
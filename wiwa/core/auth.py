# パスとファイル名: wiwa/core/auth.py
import secrets
from datetime import UTC, datetime, timedelta

from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository

SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRES_DAYS = 7

sessions_repository = SessionsRepository()
users_repository = UsersRepository()


def create_session(username: str) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=SESSION_EXPIRES_DAYS)
    csrf_token = secrets.token_urlsafe(32)

    sessions_repository.create(
        session_id=session_id,
        username=username,
        expires_at=expires_at,
        csrf_token=csrf_token,
    )
    return session_id


def get_current_user_by_session_id(session_id: str) -> dict | None:
    if not session_id:
        return None

    session = sessions_repository.find_active_by_session_id(session_id)
    if not session:
        return None

    username = session.get("username", "")
    if not username:
        return None

    user = users_repository.find_by_username(username)
    if not user:
        return None

    user["_id"] = str(user.get("_id", ""))
    user["csrf_token"] = session.get("csrf_token", "") or ""
    return user


def is_authenticated(request) -> bool:
    return bool(request.user)


def is_admin(request) -> bool:
    user = request.user or {}
    return user.get("role") == "admin"


def authorize_path(request) -> bool:
    path = request.path or ""

    # /admin は admin のみ
    if path == "/admin" or path.startswith("/admin/"):
        return is_admin(request)

    # /mypage はログイン済みユーザーなら可
    if path == "/mypage" or path.startswith("/mypage/"):
        return is_authenticated(request)

    return True
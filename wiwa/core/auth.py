# パスとファイル名: wiwa/core/auth.py
# Path and filename: wiwa/core/auth.py

# 認証・認可ユーティリティ
# Authentication and authorization utilities
#
# 概要
# Summary
#   セッションからユーザーを解決し、認証・認可判定を行う
#   Resolve user from session and perform auth checks
#
# 処理の流れ
# Flow
#   1. セッションID取得
#      Get session id
#   2. セッション検証
#      Validate session
#   3. ユーザー取得
#      Fetch user
#   4. 認証判定
#      Check authentication
#   5. 認可判定
#      Check authorization

from datetime import UTC, datetime

from wiwa.config import SESSION_COOKIE_NAME
from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository


sessions_repository = SessionsRepository()
users_repository = UsersRepository()


def get_current_user_by_session_id(session_id: str) -> dict | None:
    """
    セッションIDから現在のユーザーを取得
    Get the current user from the session ID
    """
    if not session_id:
        return None

    session = sessions_repository.find_by_session_id(session_id)
    if not session:
        return None

    expires_at = session.get("expires_at")
    if expires_at and isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        if expires_at <= datetime.now(UTC):
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


def get_current_user(request):
    """
    リクエストから現在のユーザーを取得
    Get the current user from the request
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME, "")
    return get_current_user_by_session_id(session_id)


def is_authenticated(request) -> bool:
    """
    ログイン済みか判定
    Check whether the request is authenticated
    """
    return bool(request.user)


def is_admin(request) -> bool:
    """
    管理者か判定
    Check whether the current user is an admin
    """
    user = request.user or {}
    return user.get("role") == "admin"


def authorize_path(request) -> bool:
    """
    パスに対するアクセス権限を判定
    Check whether the request is authorized for the path
    """
    path = request.path or ""

    if path == "/admin" or path.startswith("/admin/"):
        if not is_admin(request):
            return "forbidden"
        return None

    if path == "/mypage" or path.startswith("/mypage/"):
        if not is_authenticated(request):
            return "login_required"
        return None

    return None
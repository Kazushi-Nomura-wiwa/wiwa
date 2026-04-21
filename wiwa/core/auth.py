# パスとファイル名: wiwa/core/auth.py
from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository


SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRES_DAYS = 7


class Auth:
    def __init__(self):
        self.sessions_repository = SessionsRepository()
        self.users_repository = UsersRepository()

    def get_session_id(self, request) -> str | None:
        return request.cookies.get(SESSION_COOKIE_NAME)

    def get_session(self, request):
        session_id = self.get_session_id(request)
        if not session_id:
            return None

        session = self.sessions_repository.find_by_session_id(session_id)
        if not session:
            return None

        request.session_id = session_id

        if not getattr(request, "_session_touched", False):
            self.sessions_repository.touch(
                session_id=session_id,
                expires_days=SESSION_EXPIRES_DAYS,
            )
            request._session_touched = True
            request.session_cookie_needs_refresh = True

        return session

    def get_current_user(self, request):
        if getattr(request, "_current_user_loaded", False):
            return request.user

        session = self.get_session(request)
        if not session:
            request.user = None
            request._current_user_loaded = True
            return None

        username = session.get("username")
        if not username:
            request.user = None
            request._current_user_loaded = True
            return None

        user = self.users_repository.find_by_username(username)
        if not user:
            request.user = None
            request._current_user_loaded = True
            return None

        if not user.get("is_active", True):
            request.user = None
            request._current_user_loaded = True
            return None

        user["csrf_token"] = session.get("csrf_token", "")

        request.user = user
        request._current_user_loaded = True
        return user

    def is_authenticated(self, request) -> bool:
        return self.get_current_user(request) is not None

    def has_role(self, request, allowed_roles: list[str]) -> bool:
        user = self.get_current_user(request)
        if not user:
            return False

        if not allowed_roles:
            return True

        user_role = user.get("role")
        if not user_role:
            return False

        return user_role in allowed_roles

    def authorize_path(self, request) -> str | None:
        path = request.path

        if path.startswith("/admin"):
            if not self.is_authenticated(request):
                return "login_required"
            if not self.has_role(request, ["admin"]):
                return "forbidden"

        if path.startswith("/mypage"):
            if not self.is_authenticated(request):
                return "login_required"
            if not self.has_role(request, ["admin", "author"]):
                return "forbidden"

        return None


_auth = Auth()


def get_current_user(request):
    return _auth.get_current_user(request)


def is_authenticated(request) -> bool:
    return _auth.is_authenticated(request)


def has_role(request, allowed_roles: list[str]) -> bool:
    return _auth.has_role(request, allowed_roles)


def authorize_path(request) -> str | None:
    return _auth.authorize_path(request)
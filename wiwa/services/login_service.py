# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.auth import authorize_path, get_current_user
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect
from wiwa.db.sessions_repository import SessionsRepository

sessions_repository = SessionsRepository()


def check_access(request: Request, route: dict):
    path_access = authorize_path(request)
    if path_access == "login_required":
        return redirect(LOGIN_URL)

    if path_access == "forbidden":
        return forbidden()

    user = get_current_user(request)

    session_id = request.cookies.get("session_id", "")
    if session_id:
        session = sessions_repository.find_by_session_id(session_id)
        if session:
            if user is None:
                user = {}

            user["csrf_token"] = session.get("csrf_token", "")
            request.user = user
    else:
        request.user = user

    if route.get("auth_required") and user is None:
        return redirect(LOGIN_URL)

    allowed_roles = route.get("roles", [])
    if allowed_roles:
        if user is None:
            return forbidden()

        if user.get("role") not in allowed_roles:
            return forbidden()

    return None
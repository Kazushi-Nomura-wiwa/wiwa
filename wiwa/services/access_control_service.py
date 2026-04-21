# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.auth import authorize_path, get_current_user
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
    path_access = authorize_path(request)
    if path_access == "login_required":
        return redirect(LOGIN_URL)

    if path_access == "forbidden":
        return forbidden()

    user = get_current_user(request)

    if route.get("auth_required") and user is None:
        return redirect(LOGIN_URL)

    allowed_roles = route.get("roles", [])
    if allowed_roles:
        if user is None:
            return forbidden()

        if user.get("role") not in allowed_roles:
            return forbidden()

    return None
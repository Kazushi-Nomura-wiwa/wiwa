# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.auth import authorize_path
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
    user = request.user

    path_access = authorize_path(request)
    if path_access == "login_required":
        return redirect(LOGIN_URL)

    if path_access == "forbidden":
        return forbidden()

    if route.get("auth_required") and user is None:
        return redirect(LOGIN_URL)

    allowed_roles = route.get("roles", [])
    if not allowed_roles:
        return None

    if user is None:
        return forbidden()

    if user.get("role") not in allowed_roles:
        return forbidden()

    return None
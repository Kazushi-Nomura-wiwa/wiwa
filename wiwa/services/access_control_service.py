# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.auth import get_current_user
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
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
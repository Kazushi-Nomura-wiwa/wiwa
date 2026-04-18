# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
    # 認証チェック
    if route.get("auth_required") and request.user is None:
        return redirect(LOGIN_URL)

    # 権限チェック
    allowed_roles = route.get("roles", [])
    if allowed_roles:
        user = request.user

        if user is None:
            return forbidden()

        if user.get("role") not in allowed_roles:
            return forbidden()

    return None
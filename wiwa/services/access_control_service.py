# パスとファイル名: wiwa/services/access_control_service.py
from wiwa.config import LOGIN_URL
from wiwa.core.auth import authorize_path, get_current_user
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
    # 1. 旧来の path ベース認可
    path_access = authorize_path(request)
    if path_access == "login_required":
        return redirect(LOGIN_URL)

    if path_access == "forbidden":
        return forbidden()

    # 2. route ベース判定のために current user を取得
    user = get_current_user(request)

    # 3. route ベースのログイン必須判定
    if route.get("auth_required") and user is None:
        return redirect(LOGIN_URL)

    # 4. route ベースの role 判定
    allowed_roles = route.get("roles", [])
    if not allowed_roles:
        return None

    if user is None:
        return forbidden()

    if user.get("role") not in allowed_roles:
        return forbidden()

    return None
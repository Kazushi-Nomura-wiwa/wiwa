# パスとファイル名: wiwa/services/access_control_service.py
# Path and filename: wiwa/services/access_control_service.py

# アクセス制御サービス
# Access control service
#
# 概要
# Summary
#   リクエストとルート情報から認証・認可を判定し、必要に応じてレスポンスを返す
#   Evaluate authentication and authorization and return response if needed
#
# 処理の流れ
# Flow
#   1. パス単位の認証チェック
#      Check path-level authorization
#   2. 認証必須チェック
#      Check authentication requirement
#   3. ロールチェック
#      Check role permissions
#   4. 結果返却
#      Return response or allow

from wiwa.config import LOGIN_URL
from wiwa.core.auth import authorize_path
from wiwa.core.request import Request
from wiwa.core.response import forbidden, redirect


def check_access(request: Request, route: dict):
    """
    アクセス制御判定
    Check access control
    """
def check_access(request: Request, route: dict):
    user = request.user

    print("ACCESS CHECK PATH:", request.path, flush=True)
    print("ACCESS CHECK ROUTE:", route, flush=True)
    print("ACCESS CHECK USER:", user, flush=True)

    path_access = authorize_path(request)

    print("ACCESS CHECK PATH_ACCESS:", path_access, flush=True)

    if path_access == "login_required":
        print("ACCESS DENY: login_required", flush=True)
        return redirect(LOGIN_URL)

    if path_access == "forbidden":
        print("ACCESS DENY: path forbidden", flush=True)
        return forbidden()

    if route.get("auth_required") and user is None:
        print("ACCESS DENY: route login_required", flush=True)
        return redirect(LOGIN_URL)

    allowed_roles = route.get("roles", [])

    print("ACCESS CHECK ALLOWED_ROLES:", allowed_roles, flush=True)

    if not allowed_roles:
        print("ACCESS OK: no role restriction", flush=True)
        return None

    if user is None:
        print("ACCESS DENY: role required but no user", flush=True)
        return forbidden()

    if user.get("role") not in allowed_roles:
        print("ACCESS DENY: role mismatch", flush=True)
        return forbidden()

    print("ACCESS OK", flush=True)
    return None
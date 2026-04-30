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
    user = request.user

    # パス単位の認証チェック
    # Path-level authorization check
    path = request.path

    # upload系は許可
    # Allow upload endpoints
    if path.startswith("/upload/"):
        path_access = None
    else:
        path_access = authorize_path(request)

    if path_access is False:
        if user is None:
            return redirect(LOGIN_URL)
        return forbidden()

    # ルート単位の認証チェック
    # Route-level authentication check
    if route.get("auth_required") and user is None:
        return redirect(LOGIN_URL)

    # ロールチェック
    # Role-based authorization
    allowed_roles = route.get("roles", [])

    if not allowed_roles:
        return None

    if user is None:
        return forbidden()

    if user.get("role") not in allowed_roles:
        return forbidden()

    return None
# パスとファイル名: wiwa/utils/csrf.py
from hmac import compare_digest


def get_csrf_token(request) -> str:
    user = request.user or {}
    return user.get("csrf_token", "") or ""


def validate_csrf(request) -> bool:
    session_token = get_csrf_token(request)
    form_token = request.get_form("csrf_token")

    if not session_token or not form_token:
        return False

    return compare_digest(session_token, form_token)
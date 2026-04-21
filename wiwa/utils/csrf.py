# パスとファイル名: wiwa/utils/csrf.py

from hmac import compare_digest


def validate_csrf(request) -> bool:
    user = request.user or {}

    session_token = user.get("csrf_token")
    form_token = request.get_form("csrf_token")

    if not session_token or not form_token:
        return False

    return compare_digest(session_token, form_token)
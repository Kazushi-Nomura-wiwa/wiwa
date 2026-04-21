# パスとファイル名: wiwa/utils/csrf.py
from hmac import compare_digest

from wiwa.core.auth import SESSION_COOKIE_NAME


def get_csrf_token(request) -> str:
    return request.cookies.get(SESSION_COOKIE_NAME, "") or ""


def validate_csrf(request) -> bool:
    cookie_token = get_csrf_token(request)
    form_token = request.get_form("csrf_token")

    if not cookie_token or not form_token:
        return False

    return compare_digest(cookie_token, form_token)
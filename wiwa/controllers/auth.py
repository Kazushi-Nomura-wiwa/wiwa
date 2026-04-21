# パスとファイル名: wiwa/controllers/auth.py
import secrets
from wiwa.core.auth import SESSION_COOKIE_NAME, SESSION_EXPIRES_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, redirect
from wiwa.db.users_repository import UsersRepository
from wiwa.services.login_service import LoginService

renderer = TemplateRenderer()
login_service = LoginService()
users_repository = UsersRepository()


def login(request, route=None, **kwargs):
    if request.method == "POST":
        return _login_submit(request)

    body = renderer.render(
        "html/auth/login.html",
        {
            "error_message": "",
            "username": "",
        },
        request=request,
    )
    return html(body)


def _login_submit(request):
    username = request.get_form("username", "").strip()
    password = request.get_form("password", "")

    result = login_service.login(username=username, password=password)

    if not result.ok:
        body = renderer.render(
            "html/auth/login.html",
            {
                "error_message": result.message,
                "username": username,
            },
            request=request,
        )
        return html(body)

    user = users_repository.find_by_username(username)

    # ★ここ追加
    if user is not None:
        user["csrf_token"] = secrets.token_urlsafe(32)

    location = "/mypage"
    if user and user.get("role") == "admin":
        location = "/admin"

    response = redirect(location)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=result.session_id,
        path="/",
        http_only=True,
        secure=False,
        same_site="Lax",
        max_age=60 * 60 * 24 * SESSION_EXPIRES_DAYS,
    )
    return response
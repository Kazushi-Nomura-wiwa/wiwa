# パスとファイル名: wiwa/controllers/auth.py
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
    template_name = (route or {}).get("template", "html/auth/login.html")
    body = renderer.render(
        template_name,
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
        html_template = (route or {}).get("template", "html/auth/login.html")
        body = renderer.render(
            html_template,
            {
                "error_message": result.message,
                "username": username,
            },
            request=request,
        )
        return html(body)

    user = users_repository.find_by_username(username)

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


def logout(request, route=None, **kwargs):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        login_service.logout(session_id)

    response = redirect("/auth/login")
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )
    return response
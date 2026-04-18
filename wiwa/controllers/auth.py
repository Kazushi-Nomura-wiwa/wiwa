# パスとファイル名: wiwa/controllers/auth.py
from wiwa.core.auth import SESSION_COOKIE_NAME
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.services.login_service import LoginService

renderer = TemplateRenderer()
login_service = LoginService()


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
    return Response(body=body)


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
        return Response(body=body)

    response = Response(
        body="",
        status="302 Found",
        headers=[("Location", "/admin")],
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=result.session_id,
        path="/",
        http_only=True,
        secure=False,
        same_site="Lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


def logout(request, route=None, **kwargs):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        login_service.logout(session_id)

    response = Response(
        body="",
        status="302 Found",
        headers=[("Location", "/auth/login")],
    )
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )
    return response
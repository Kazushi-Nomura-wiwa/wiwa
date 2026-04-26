# パスとファイル名: wiwa/app.py

import traceback

from wiwa.config import SESSION_COOKIE_NAME, SESSION_EXPIRES_DAYS
from wiwa.core.auth import get_current_user_by_session_id
from wiwa.core.dispatcher import Dispatcher
from wiwa.core.request import Request
from wiwa.core.resolver import Resolver
from wiwa.core.response import internal_server_error, not_found
from wiwa.db.mongo import ensure_indexes
from wiwa.db.sessions_repository import SessionsRepository
from wiwa.extensions.loader import ExtensionLoader
from wiwa.services.access_control_service import check_access
from wiwa.services.access_log_service import save_access_log
from wiwa.services.static_files_service import serve_static
from wiwa.services.theme_files_service import serve_theme_file


# 初期化
ensure_indexes()
resolver = Resolver()
dispatcher = Dispatcher()
extension_loader = ExtensionLoader()
extension_routes = extension_loader.load_routes()


# --- ヘルパー --------------------------------------------------

def make_start_response(start_response, status_holder: dict):
    def custom_start_response(status, headers, exc_info=None):
        try:
            status_holder["status_code"] = int(status.split(" ", 1)[0])
        except (ValueError, IndexError):
            status_holder["status_code"] = 500
        return start_response(status, headers, exc_info)

    return custom_start_response


def refresh_session_cookie(response, request) -> None:
    session_id = getattr(request, "session_id", None)
    if not session_id:
        return

    if not getattr(request, "session_cookie_needs_refresh", False):
        return

    if response.has_cookie(SESSION_COOKIE_NAME):
        return

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        path="/",
        http_only=True,
        secure=False,
        same_site="Lax",
        max_age=60 * 60 * 24 * SESSION_EXPIRES_DAYS,
    )


def finish_response(response, environ, start_response, request, status_holder: dict):
    refresh_session_cookie(response, request)
    result = response(environ, start_response)
    save_access_log(request, status_holder["status_code"])
    return result


def resolve_extension_route(path: str, method: str) -> dict | None:
    normalized_method = method.upper()

    for route in extension_routes:
        if route.get("url") != path:
            continue

        if (route.get("method") or "").upper() != normalized_method:
            continue

        resolved = dict(route)
        resolved.setdefault("params", {})
        resolved.setdefault("auth_required", False)
        resolved.setdefault("roles", [])
        return resolved

    return None


def attach_request_user(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME, "")
    request.session_id = session_id or None
    request.user = get_current_user_by_session_id(session_id)

    if request.user and session_id:
        SessionsRepository().touch(session_id)


def handle_static(request):
    if request.path.startswith("/static/"):
        return serve_static(request)

    if request.path.startswith("/themes/"):
        return serve_theme_file(request)

    return None


def resolve_route(request):
    resolved = resolve_extension_route(request.path, request.method)

    if resolved is None:
        resolved = resolver.resolve(request.path, request.method)

    return resolved


# --- WSGI Entry --------------------------------------------------

def application(environ, start_response):
    request = Request(environ)
    attach_request_user(request)

    status_holder = {"status_code": 500}
    wrapped_start_response = make_start_response(start_response, status_holder)

    print(
        f'{request.remote_addr} "{request.user_agent}" "{request.method} {request.path}"',
        flush=True,
    )

    try:
        # static / theme
        static_response = handle_static(request)
        if static_response:
            return static_response(environ, wrapped_start_response)

        # routing
        resolved = resolve_route(request)

        if resolved is None:
            return finish_response(
                not_found(),
                environ,
                wrapped_start_response,
                request,
                status_holder,
            )

        # access control
        access_response = check_access(request, resolved)
        if access_response is not None:
            return finish_response(
                access_response,
                environ,
                wrapped_start_response,
                request,
                status_holder,
            )

        # dispatch
        response = dispatcher.dispatch(resolved, request)

        return finish_response(
            response,
            environ,
            wrapped_start_response,
            request,
            status_holder,
        )

    except Exception:
        error_text = traceback.format_exc()
        print(error_text, flush=True)

        return finish_response(
            internal_server_error(error_text),
            environ,
            wrapped_start_response,
            request,
            status_holder,
        )
# パスとファイル名: wiwa/app.py
# Path and filename: wiwa/app.py

# WiWA WSGIアプリケーション本体
# Core WSGI application for WiWA
#
# 概要
# Summary
#   リクエストのライフサイクルを管理する
#   Manage the full request lifecycle
#
# 処理の流れ
# Flow
#   1. Request生成
#      Build request
#   2. セッションとユーザーを付与
#      Attach session and user
#   3. 静的ファイル処理
#      Handle static files
#   4. ルーティング解決
#      Resolve route
#   5. 認可チェック
#      Check access control
#   6. ハンドラ実行
#      Execute handler
#   7. レスポンス最終処理
#      Finalize response

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


# ------------------------------
# 初期化
# Initialization
# ------------------------------

# DBインデックスを保証
# Ensure MongoDB indexes
ensure_indexes()

# ルーティング関連
# Routing components
resolver = Resolver()
dispatcher = Dispatcher()

# 拡張機能ルート読み込み
# Load extension routes
extension_loader = ExtensionLoader()
extension_routes = extension_loader.load_routes()


# ------------------------------
# ヘルパー
# Helpers
# ------------------------------

def make_start_response(start_response, status_holder: dict):
    """
    ステータスコードを取得するラッパー
    Wrap start_response to capture status code
    """
    def custom_start_response(status, headers, exc_info=None):
        try:
            status_holder["status_code"] = int(status.split(" ", 1)[0])
        except (ValueError, IndexError):
            status_holder["status_code"] = 500
        return start_response(status, headers, exc_info)

    return custom_start_response


def refresh_session_cookie(response, request) -> None:
    """
    セッションCookieを延長する
    Refresh session cookie if needed
    """
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
    """
    レスポンスの最終処理
    Finalize response
    """
    # セッションCookie更新
    # Refresh session cookie
    refresh_session_cookie(response, request)

    result = response(environ, start_response)

    # アクセスログ保存
    # Save access log
    save_access_log(request, status_holder["status_code"])

    return result


def resolve_extension_route(path: str, method: str) -> dict | None:
    """
    拡張機能ルートの解決
    Resolve extension route
    """
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
    """
    Requestにユーザー情報を付与
    Attach user to request
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME, "")
    request.session_id = session_id or None
    request.user = get_current_user_by_session_id(session_id)

    # セッション延命（スライディング方式）
    # Sliding session expiration
    if request.user and session_id:
        SessionsRepository().touch(session_id)


def handle_static(request):
    """
    静的ファイルの処理
    Handle static and theme files
    """
    if request.path.startswith("/static/"):
        return serve_static(request)

    if request.path.startswith("/themes/"):
        return serve_theme_file(request)

    return None


def resolve_route(request):
    """
    ルーティング解決
    Resolve route (extension → core)
    """
    resolved = resolve_extension_route(request.path, request.method)

    if resolved is None:
        resolved = resolver.resolve(request.path, request.method)

    return resolved


# ------------------------------
# WSGIエントリーポイント
# WSGI Entry
# ------------------------------

def application(environ, start_response):
    """
    WSGIエントリーポイント
    WSGI application entry point
    """

    # Request生成
    # Build request object
    request = Request(environ)

    # ユーザー情報付与
    # Attach user/session
    attach_request_user(request)

    # ステータス保持
    # Status tracking
    status_holder = {"status_code": 500}
    wrapped_start_response = make_start_response(start_response, status_holder)

    # 簡易アクセスログ
    # Simple access log
    print(
        f'{request.remote_addr} "{request.user_agent}" "{request.method} {request.path}"',
        flush=True,
    )

    try:
        # 静的ファイル処理
        # Handle static
        static_response = handle_static(request)
        if static_response:
            return static_response(environ, wrapped_start_response)

        # ルーティング
        # Routing
        resolved = resolve_route(request)

        if resolved is None:
            return finish_response(
                not_found(),
                environ,
                wrapped_start_response,
                request,
                status_holder,
            )

        # 認可チェック
        # Access control
        access_response = check_access(request, resolved)
        if access_response is not None:
            return finish_response(
                access_response,
                environ,
                wrapped_start_response,
                request,
                status_holder,
            )

        # ハンドラ実行
        # Dispatch handler
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
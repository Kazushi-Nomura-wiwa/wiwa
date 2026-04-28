# パスとファイル名: wiwa/controllers/auth.py

# 認証コントローラ
# Authentication controller
#
# URL:
#   /auth/login   (GET, POST)
#   /auth/logout  (GET)
#
# Flow (login):
#   1. フォーム表示 / Render login form
#   2. 入力受信 / Receive credentials
#   3. 認証処理 / Authenticate user
#   4. セッション発行 / Create session
#   5. リダイレクト / Redirect

from wiwa.config import SESSION_COOKIE_NAME, SESSION_EXPIRES_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, redirect
from wiwa.db.users_repository import UsersRepository
from wiwa.services.login_service import LoginService


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# ログインサービス
# Login service
login_service = LoginService()

# ユーザーリポジトリ
# User repository
users_repository = UsersRepository()


def login(request, route=None, **kwargs):
    """
    ログイン画面およびログイン処理
    Login page and login handler
    """

    # POST時はログイン処理へ
    # On POST, handle login submission
    if request.method == "POST":
        return _login_submit(request, route)

    # 初期表示
    # Initial form render
    body = renderer.render_route(
        route,
        "html/auth/login.html",
        {
            "error_message": "",
            "username": "",
        },
        request=request,
    )
    return html(body)


def _login_submit(request, route):
    """
    ログイン送信処理
    Handle login submission
    """

    # 入力値取得
    # Get form inputs
    username = request.get_form("username", "").strip()
    password = request.get_form("password", "")

    # 認証処理
    # Authenticate user
    result = login_service.login(username=username, password=password)

    # 認証失敗
    # Authentication failed
    if not result.ok:
        body = renderer.render_route(
            route,
            "html/auth/login.html",
            {
                "error_message": result.message,
                "username": username,
            },
            request=request,
        )
        return html(body)

    # ユーザー取得
    # Fetch user
    user = users_repository.find_by_username(username)

    # リダイレクト先決定
    # Determine redirect destination
    location = "/mypage"
    if user and user.get("role") == "admin":
        location = "/admin"

    # レスポンス作成
    # Create redirect response
    response = redirect(location)

    # セッションCookie設定
    # Set session cookie
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
    """
    ログアウト処理
    Logout handler
    """

    # セッション取得
    # Get session id from cookie
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    # セッション無効化
    # Invalidate session
    if session_id:
        login_service.logout(session_id)

    # ログイン画面へリダイレクト
    # Redirect to login page
    response = redirect("/auth/login")

    # Cookie削除
    # Delete session cookie
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )

    return response
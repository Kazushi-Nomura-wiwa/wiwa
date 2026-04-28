# パスとファイル名: wiwa/controllers/admin/assist.py
# Path and filename: wiwa/controllers/admin/assist.py

# アシスト機能（ルート一覧）
# Assist feature (route listing)
#
# URL
# URL
#   /admin/assist/routes
#
# 処理の流れ
# Flow
#   1. ルート情報を収集
#      Scan routes
#   2. テンプレート描画
#      Render template
#   3. HTMLレスポンス返却
#      Return HTML response

from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html
from wiwa.core.route_scanner import RouteScanner


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()


def routes(request, route=None):
    """
    ルート一覧を表示する
    Render route list
    """

    # ルートスキャナー生成
    # Initialize route scanner
    scanner = RouteScanner()

    # ルート情報取得
    # Get route definitions
    routes = scanner.get_routes()

    # テンプレート描画
    # Render admin routes template
    body = renderer.render_route(
        route,
        "html/admin/routes.html",
        {
            "title": t("admin_routes_title"),
            "routes": routes,
            "current_user": request.user,
        },
        request=request,
    )

    # HTMLレスポンス返却
    # Return HTML response
    return html(body)
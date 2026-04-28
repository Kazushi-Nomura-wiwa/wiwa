# パスとファイル名: wiwa/controllers/admin/index.py
# Path and filename: wiwa/controllers/admin/index.py

# 管理画面トップコントローラ
# Admin dashboard controller
#
# URL
# URL
#   /admin
#
# 処理の流れ
# Flow
#   1. テンプレート描画
#      Render template
#   2. HTMLレスポンス返却
#      Return HTML response

from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()


def index(request, route=None, **params):
    """
    管理画面トップを表示する
    Render admin dashboard
    """

    # 管理画面トップテンプレートを描画
    # Render admin dashboard template
    body = renderer.render_route(
        route,
        "html/admin/index.html",
        {
            "title": t("admin_title"),
        },
        request=request,
    )

    # HTMLレスポンス返却
    # Return HTML response
    return Response(body=body)
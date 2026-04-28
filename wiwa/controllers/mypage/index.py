# パスとファイル名: wiwa/controllers/mypage/index.py
# Path and filename: wiwa/controllers/mypage/index.py

# マイページトップコントローラ
# MyPage top controller
#
# URL
# URL
#   /mypage
#
# 処理の流れ
# Flow
#   1. 現在ユーザー取得
#      Get current user
#   2. テンプレート描画
#      Render template
#   3. HTMLレスポンス返却
#      Return HTML response

from wiwa.core.auth import get_current_user
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.core.i18n import t


renderer = TemplateRenderer()


def index(request, route=None, **kwargs):
    """
    マイページのトップ画面を表示する
    Display the mypage top screen
    """

    # 現在ユーザー取得
    # Get current user
    current_user = get_current_user(request)

    # テンプレート描画
    # Render template
    body = renderer.render_route(
        route,
        "html/mypage/index.html",
        {
            "title": t("mypage.title"),
            "current_user": current_user,
        },
        request=request,
    )

    # HTMLレスポンス返却
    # Return HTML response
    return Response(body=body)
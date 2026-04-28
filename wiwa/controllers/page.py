# パスとファイル名: wiwa/controllers/page.py
# Path and filename: wiwa/controllers/page.py

# 固定ページコントローラ
# Static page controller
#
# URL
# URL
#   /<path>
#
# 処理の流れ
# Flow
#   1. パスからページ取得
#      Resolve page by path
#   2. 存在チェック
#      Check existence
#   3. Editor.js JSONをHTMLへ変換
#      Convert Editor.js JSON to HTML
#   4. テンプレート描画
#      Render template
#   5. レスポンス返却
#      Return response

from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.services.editorjs_service import EditorJSService
from wiwa.services.page_service import PageService


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# Editor.js変換サービス
# Editor.js conversion service
editorjs_service = EditorJSService()


def slug(request, route=None, **params):
    """
    固定ページ表示
    Render static page by path
    """

    # ページサービス生成
    # Initialize page service
    service = PageService()

    # パスからページ取得
    # Fetch page by request path
    page = service.get_page_by_path(request.path)

    # ページが存在しない場合
    # If page not found
    if not page:
        return Response(
            body=t("page_not_found"),
            status="404 Not Found",
        )

    # Editor.js JSONをHTMLへ変換
    # Convert Editor.js JSON to HTML
    page["body_html"] = editorjs_service.build_html(
        page.get("body_json", "")
    )

    # テンプレート描画
    # Render page template
    body = renderer.render_route(
        route,
        "html/page/slug.html",
        {
            "title": page.get("title", ""),
            "page": page,
        },
        request=request,
    )

    # レスポンス返却
    # Return response
    return Response(body=body)
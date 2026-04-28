# パスとファイル名: wiwa/controllers/admin/page.py
# Path and filename: wiwa/controllers/admin/page.py

# 固定ページ管理コントローラ
# Admin page management controller
#
# URL
# URL
#   /admin/page/list
#   /admin/page/new
#   /admin/page/edit/<id>
#   /admin/page/delete/<id>
#
# 処理の流れ（一覧）
# Flow (list)
#   1. ページ一覧取得
#      Fetch pages
#   2. テンプレート描画
#      Render template
#
# 処理の流れ（作成）
# Flow (create)
#   1. フォーム初期化
#      Initialize form
#   2. POST時は作成処理
#      Handle POST submission
#   3. テンプレート描画
#      Render template
#
# 処理の流れ（編集）
# Flow (edit)
#   1. ページ取得
#      Fetch page
#   2. POST時は更新処理
#      Handle POST submission
#   3. Editor.js用に正規化
#      Normalize for Editor.js
#   4. テンプレート描画
#      Render template
#
# 処理の流れ（削除）
# Flow (delete)
#   1. POST時は削除実行
#      Execute delete
#   2. ページ取得
#      Fetch page
#   3. テンプレート描画
#      Render template

from urllib.parse import quote

from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.services.editorjs_service import EditorJSService
from wiwa.services.page_service import PageService


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# Editor.js変換サービス
# Editor.js service
editorjs_service = EditorJSService()


def _redirect_with_error(msg, path):
    """
    エラーメッセージ付きでリダイレクト
    Redirect with error message
    """
    return redirect(f"{path}?error=" + quote(msg))


def list(request, route=None, **params):
    """
    固定ページ一覧
    Render page list
    """

    service = PageService()

    body = renderer.render_route(
        route,
        "html/admin/page/list.html",
        {
            "title": t("admin_page_list_title"),
            "pages": service.list_pages(),
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def new(request, route=None, **params):
    """
    固定ページ作成
    Create page
    """

    service = PageService()

    # フォーム初期化
    # Initialize form data
    form_data = {
        "title": "",
        "slug": "",
        "body_json": editorjs_service.empty(),
        "status": "draft",
    }

    # POST処理
    # Handle POST
    if request.method == "POST":
        page_id, error = service.create_page({
            "title": request.get_form("title"),
            "slug": request.get_form("slug"),
            "body_json": request.get_form("body_json"),
            "status": request.get_form("status"),
        })

        if error:
            return _redirect_with_error(error, "/admin/page/new")

        return redirect("/admin/page/list")

    body = renderer.render_route(
        route,
        "html/admin/page/new.html",
        {
            "title": t("admin_page_new_title"),
            "form_data": form_data,
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def edit(request, route=None, **params):
    """
    固定ページ編集
    Edit page
    """

    service = PageService()
    page_id = (params.get("id") or "").strip()

    # ページ取得
    # Fetch page
    page = service.get_page_by_id(page_id)
    if not page:
        return Response(t("not_found"), 404)

    # POST処理
    # Handle POST
    if request.method == "POST":
        success, error = service.update_page(page_id, {
            "title": request.get_form("title"),
            "slug": request.get_form("slug"),
            "body_json": request.get_form("body_json"),
            "status": request.get_form("status"),
        })

        if error:
            return _redirect_with_error(error, f"/admin/page/edit/{page_id}")

        return redirect("/admin/page/list")

    # Editor.js用に正規化
    # Normalize for Editor.js
    page["body_json"] = editorjs_service.normalize(page.get("body_json"))

    body = renderer.render_route(
        route,
        "html/admin/page/edit.html",
        {
            "title": t("admin_page_edit_title"),
            "page": page,
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def delete(request, route=None, **params):
    """
    固定ページ削除
    Delete page
    """

    service = PageService()
    page_id = (params.get("id") or "").strip()

    # POST時は削除実行
    # Execute delete on POST
    if request.method == "POST":
        service.delete_page(page_id)
        return redirect("/admin/page/list")

    # ページ取得
    # Fetch page
    page = service.get_page_by_id(page_id)
    if not page:
        return Response(t("not_found"), 404)

    body = renderer.render_route(
        route,
        "html/admin/page/delete.html",
        {
            "title": t("delete_title"),
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
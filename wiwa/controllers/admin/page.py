# パスとファイル名: wiwa/controllers/admin/page.py

from urllib.parse import quote

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.db.connection import get_db
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()


def _redirect_with_error(message: str, path: str):
    return redirect(f"{path}?error=" + quote(message))


def list(request, route=None, **params):
    db = get_db()
    service = PageService(db)

    error_message = request.get_query("error", "")
    template_name = (route or {}).get("template", "html/admin/page/list.html")

    body = renderer.render(
        template_name,
        {
            "title": "固定ページ一覧",
            "pages": service.list_pages(),
            "error_message": error_message,
        },
        request=request,
    )

    return Response(body=body)


def new(request, route=None, **params):
    db = get_db()
    service = PageService(db)

    error_message = ""
    form_data = {
        "title": "",
        "slug": "",
        "body_json": "",
        "status": "draft",
    }

    if request.method == "POST":
        data = {
            "title": request.get_form("title"),
            "slug": request.get_form("slug"),
            "body_json": request.get_form("body_json"),
            "status": request.get_form("status") or "draft",
            "created_by": request.current_user.get("_id"),
            "updated_by": request.current_user.get("_id"),
        }

        page_id, error = service.create_page(data)

        if error:
            return _redirect_with_error(error, "/admin/page/new")

        return redirect("/admin/page/list")

    template_name = (route or {}).get("template", "html/admin/page/new.html")

    body = renderer.render(
        template_name,
        {
            "title": "固定ページ作成",
            "error_message": error_message,
            "form_data": form_data,
        },
        request=request,
    )

    return Response(body=body)


def edit(request, route=None, **params):
    db = get_db()
    service = PageService(db)

    page_id = (params.get("id") or "").strip()
    if not page_id:
        return _redirect_with_error("id が不正です。", "/admin/page/list")

    page = service.get_page_by_id(page_id)
    if not page:
        return _redirect_with_error("固定ページが見つかりません。", "/admin/page/list")

    if request.method == "POST":
        data = {
            "title": request.get_form("title"),
            "slug": request.get_form("slug"),
            "body_json": request.get_form("body_json"),
            "status": request.get_form("status") or "draft",
            "updated_by": request.current_user.get("_id"),
        }

        success, error = service.update_page(page_id, data)

        if error:
            return _redirect_with_error(error, f"/admin/page/edit/{page_id}")

        return redirect("/admin/page/list")

    template_name = (route or {}).get("template", "html/admin/page/edit.html")

    body = renderer.render(
        template_name,
        {
            "title": "固定ページ編集",
            "page": page,
        },
        request=request,
    )

    return Response(body=body)


def delete(request, route=None, **params):
    db = get_db()
    service = PageService(db)

    page_id = (params.get("id") or "").strip()
    if not page_id:
        return _redirect_with_error("id が不正です。", "/admin/page/list")

    page = service.get_page_by_id(page_id)
    if not page:
        return _redirect_with_error("固定ページが見つかりません。", "/admin/page/list")

    if request.method == "POST":
        service.delete_page(page_id)
        return redirect("/admin/page/list")

    template_name = (route or {}).get("template", "html/admin/page/delete.html")

    body = renderer.render(
        template_name,
        {
            "title": "固定ページ削除",
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
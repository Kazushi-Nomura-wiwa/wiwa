# パスとファイル名: wiwa/controllers/admin/page.py

from urllib.parse import quote

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.services.editorjs_service import EditorJSService
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()
editorjs_service = EditorJSService()


def _redirect_with_error(msg, path):
    return redirect(f"{path}?error=" + quote(msg))


def list(request, route=None, **params):
    service = PageService()

    body = renderer.render_route(
        route,
        "html/admin/page/list.html",
        {
            "title": "固定ページ一覧",
            "pages": service.list_pages(),
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def new(request, route=None, **params):
    service = PageService()

    form_data = {
        "title": "",
        "slug": "",
        "body_json": editorjs_service.empty(),
        "status": "draft",
    }

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
            "title": "固定ページ作成",
            "form_data": form_data,
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def edit(request, route=None, **params):
    service = PageService()
    page_id = (params.get("id") or "").strip()

    page = service.get_page_by_id(page_id)
    if not page:
        return Response("Not found", 404)

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

    page["body_json"] = editorjs_service.normalize(page.get("body_json"))

    body = renderer.render_route(
        route,
        "html/admin/page/edit.html",
        {
            "title": "固定ページ編集",
            "page": page,
            "error_message": request.get_query("error", ""),
        },
        request=request,
    )

    return Response(body=body)


def delete(request, route=None, **params):
    service = PageService()
    page_id = (params.get("id") or "").strip()

    if request.method == "POST":
        service.delete_page(page_id)
        return redirect("/admin/page/list")

    page = service.get_page_by_id(page_id)
    if not page:
        return Response("Not found", 404)

    body = renderer.render_route(
        route,
        "html/admin/page/delete.html",
        {
            "title": "削除",
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
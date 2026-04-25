# パスとファイル名: wiwa/controllers/admin/page.py

from urllib.parse import quote
import builtins
import json

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()


def _redirect_with_error(msg, path):
    return redirect(f"{path}?error=" + quote(msg))


def _normalize_body_json_for_editor(page):
    body_json = page.get("body_json", "")

    if isinstance(body_json, dict):
        page["body_json"] = json.dumps(body_json, ensure_ascii=False)
        return page

    if isinstance(body_json, builtins.list):
        page["body_json"] = json.dumps({"blocks": body_json}, ensure_ascii=False)
        return page

    if not isinstance(body_json, str):
        page["body_json"] = json.dumps({"blocks": []}, ensure_ascii=False)
        return page

    body_json = body_json.strip()

    if not body_json:
        page["body_json"] = json.dumps({"blocks": []}, ensure_ascii=False)
        return page

    try:
        parsed = json.loads(body_json)
        page["body_json"] = json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        page["body_json"] = json.dumps({"blocks": []}, ensure_ascii=False)

    return page


def list(request, route=None, **params):
    service = PageService()

    body = renderer.render(
        (route or {}).get("template", "html/admin/page/list.html"),
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
        "body_json": json.dumps({"blocks": []}, ensure_ascii=False),
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

    body = renderer.render(
        (route or {}).get("template", "html/admin/page/new.html"),
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

    page = _normalize_body_json_for_editor(page)

    body = renderer.render(
        (route or {}).get("template", "html/admin/page/edit.html"),
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

    body = renderer.render(
        (route or {}).get("template", "html/admin/page/delete.html"),
        {
            "title": "削除",
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
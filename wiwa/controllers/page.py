# パスとファイル名: wiwa/controllers/page.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.services.editorjs_service import EditorJSService
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()
editorjs_service = EditorJSService()


def slug(request, route=None, **params):
    service = PageService()

    page = service.get_page_by_path(request.path)

    if not page:
        return Response(
            body="固定ページが見つかりません。",
            status="404 Not Found",
        )

    page["body_html"] = editorjs_service.build_html(page.get("body_json", ""))

    body = renderer.render_route(
        route,
        "html/page/slug.html",
        {
            "title": page.get("title", ""),
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
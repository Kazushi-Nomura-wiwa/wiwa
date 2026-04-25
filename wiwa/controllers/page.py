# パスとファイル名: wiwa/controllers/page.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()


def slug(request, route=None, **params):
    service = PageService()

    # slugではなくpathで取得
    page = service.get_page_by_path(request.path)

    if not page:
        return Response(
            body="固定ページが見つかりません。",
            status="404 Not Found"
        )

    template_name = (route or {}).get("template", "html/page/slug.html")

    body = renderer.render(
        template_name,
        {
            "title": page.get("title", ""),
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
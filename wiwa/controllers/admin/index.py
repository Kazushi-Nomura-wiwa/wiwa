# パスとファイル名: wiwa/controllers/admin/index.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response


renderer = TemplateRenderer()


def index(request, route=None, **params):
    body = renderer.render_route(
        route,
        "html/admin/index.html",
        {
            "title": "Admin",
        },
        request=request,
    )
    return Response(body=body)
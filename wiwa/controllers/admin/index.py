# パスとファイル名: wiwa/controllers/admin/index.py
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response


renderer = TemplateRenderer()


def index(request, route=None, **params):
    template_name = (route or {}).get("template", "html/admin/index.html")
    body = renderer.render(
        template_name,
        {
            "title": "Admin",
        },
        request=request,
    )
    return Response(body=body)
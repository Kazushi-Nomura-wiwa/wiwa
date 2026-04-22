# パスとファイル名: wiwa/controllers/admin/routes.py
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.core.route_scanner import RouteScanner


def index(request, route=None):
    scanner = RouteScanner()
    routes = scanner.get_routes()

    renderer = TemplateRenderer()

    body = renderer.render(
        "html/admin/routes/index.html",
        {
            "title": "Routes",
            "routes": routes,
            "current_user": getattr(request, "current_user", None),
        },
    )

    return Response(
        body=body,
        status="200 OK",
        headers=[("Content-Type", "text/html; charset=utf-8")],
    )
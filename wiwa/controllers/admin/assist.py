# パスとファイル名: wiwa/controllers/admin/assist.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html
from wiwa.core.route_scanner import RouteScanner


renderer = TemplateRenderer()


def routes(request, route=None):
    scanner = RouteScanner()
    routes = scanner.get_routes()

    body = renderer.render_route(
        route,
        "html/admin/routes.html",
        {
            "title": "Routes一覧",
            "routes": routes,
            "current_user": request.user,
        },
        request=request,
    )

    return html(body)
# パスとファイル名: wiwa/extensions/robots/extension.py
from wiwa.config import SITE_URL
from wiwa.core.response import Response


def register():
    return {
        "routes": [
            {
                "url": "/robots.txt",
                "method": "GET",
                "handler": "wiwa.extensions.robots.extension.index",
                "auth_required": False,
                "roles": [],
            }
        ]
    }


def index(request, route=None, **params):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "",
        f"Sitemap: {SITE_URL}/sitemap.xml",
    ]

    body = "\n".join(lines) + "\n"

    return Response(
        body=body,
        status="200 OK",
        headers=[
            ("Content-Type", "text/plain; charset=UTF-8"),
        ],
    )
# パスとファイル名: wiwa/extensions/robots/extension.py
# Path and filename: wiwa/extensions/robots/extension.py

# robots.txt拡張
# Robots.txt extension
#
# 概要
# Summary
#   robots.txtを提供し、クローラのアクセス制御を行う
#   Provide robots.txt to control crawler access
#
# URL
# URL
#   /robots.txt
#
# 処理の流れ
# Flow
#   1. ルート登録
#      Register route
#   2. robots内容生成
#      Build robots.txt content
#   3. テキストレスポンス返却
#      Return text response

from wiwa.config import SITE_URL
from wiwa.core.response import Response


def register():
    """
    ルート登録
    Register extension routes
    """
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
    """
    robots.txt生成
    Generate robots.txt
    """
    # robots.txt内容構築
    # Build robots.txt content
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "",
        f"Sitemap: {SITE_URL}/sitemap.xml",
    ]

    body = "\n".join(lines) + "\n"

    # テキストレスポンス返却
    # Return text response
    return Response(
        body=body,
        status="200 OK",
        headers=[
            ("Content-Type", "text/plain; charset=UTF-8"),
        ],
    )
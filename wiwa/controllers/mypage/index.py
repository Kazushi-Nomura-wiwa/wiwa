# パスとファイル名: wiwa/controllers/mypage/index.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.core.auth import get_current_user


renderer = TemplateRenderer()


def index(request, route=None, **kwargs):
    current_user = get_current_user(request)

    body = renderer.render_route(
        route,
        "html/mypage/index.html",
        {
            "title": "MyPage",
            "current_user": current_user,
        },
        request=request,
    )
    return Response(body=body)
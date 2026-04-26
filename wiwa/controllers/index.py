# パスとファイル名: wiwa/controllers/index.py

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html
from wiwa.db.post_repository import PostRepository
from wiwa.services.post_view_service import PostViewService


renderer = TemplateRenderer()
post_repo = PostRepository()
post_view_service = PostViewService()


def index(request, route=None):
    posts = post_repo.list_published()[:5]
    posts = post_view_service.build_post_list(posts)

    body = renderer.render_route(
        route,
        "html/index.html",
        {
            "title": "Home",
            "posts": posts,
        },
        request=request,
    )
    return html(body)
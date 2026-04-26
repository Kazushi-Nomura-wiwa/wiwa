# パスとファイル名: wiwa/controllers/tag.py

from urllib.parse import unquote

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found
from wiwa.services.post_service import PostService


renderer = TemplateRenderer()
post_service = PostService()


def name(request, route=None, name: str = ""):
    tag_name = unquote(name).strip()
    if not tag_name:
        return not_found()

    posts = post_service.list_posts_by_tag(tag_name)

    body = renderer.render_route(
        route,
        "html/tag/name.html",
        {
            "title": f"タグ: {tag_name}",
            "tag_name": tag_name,
            "posts": posts,
            "total_count": len(posts),
        },
        request=request,
    )
    return html(body)
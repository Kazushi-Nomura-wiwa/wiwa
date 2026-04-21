# パスとファイル名: wiwa/controllers/tag.py
from urllib.parse import unquote

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, not_found
from wiwa.db.post_repository import PostRepository
from wiwa.services.auth_service import get_current_user


def name(request, route=None, name: str = ""):
    renderer = TemplateRenderer()
    post_repo = PostRepository()

    tag_name = unquote(name)
    if not tag_name:
        return not_found()

    posts = post_repo.get_posts_by_tag(tag_name)
    total_count = post_repo.count_posts_by_tag(tag_name)
    current_user = get_current_user(request)

    body = renderer.render(
        "tag/name.html",
        {
            "title": f"タグ: {tag_name}",
            "tag_name": tag_name,
            "posts": posts,
            "total_count": total_count,
            "current_user": current_user,
        },
    )
    return Response(body=body)
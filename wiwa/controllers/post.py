# パスとファイル名: wiwa/controllers/post.py

from wiwa.config import POSTS_PER_PAGE
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found
from wiwa.db.post_repository import PostRepository
from wiwa.services.post_view_service import PostViewService


renderer = TemplateRenderer()
post_repo = PostRepository()
post_view_service = PostViewService()


def index(request, route=None):
    try:
        page = int(request.query.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    if page < 1:
        page = 1

    per_page = POSTS_PER_PAGE
    skip = (page - 1) * per_page

    posts = post_repo.list_published(limit=per_page, skip=skip)
    posts = post_view_service.build_post_list(posts)

    total = post_repo.count_published()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    body = renderer.render_route(
        route,
        "html/post/index.html",
        {
            "title": "Post",
            "posts": posts,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
        request=request,
    )
    return html(body)


def slug(request, route=None, slug=None):
    post = post_repo.find_published_by_slug(slug)

    if not post:
        return not_found()

    post = post_view_service.build_post(post)

    body = renderer.render_route(
        route,
        "html/post/slug.html",
        {
            "title": post.get("title", ""),
            "post": post,
        },
        request=request,
    )
    return html(body)
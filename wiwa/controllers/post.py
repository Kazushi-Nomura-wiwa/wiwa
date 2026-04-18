# パスとファイル名: wiwa/controllers/post.py
from wiwa.config import POSTS_PER_PAGE
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found
from wiwa.db.post_repository import PostRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.utils.localtime import to_localtime_string

renderer = TemplateRenderer()
post_repo = PostRepository()
users_repo = UsersRepository()


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
    total = post_repo.count_published()

    author_ids = []
    for post in posts:
        author_id = post.get("author_id")
        if author_id:
            author_ids.append(author_id)

    display_names = users_repo.find_display_names_by_ids(author_ids)

    for post in posts:
        author_id = post.get("author_id", "")
        post["author_display_name"] = display_names.get(
            author_id,
            post.get("author_name", "")
        )
        post["published_at_display"] = to_localtime_string(post.get("published_at"))

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    body = renderer.render(
        route["template"],
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

    author_display_name = post.get("author_name", "")
    author_id = post.get("author_id", "")

    if author_id:
        user = users_repo.find_by_id(author_id)
        if user:
            author_display_name = user.get("display_name") or user.get("username") or author_display_name

    post["author_display_name"] = author_display_name
    post["published_at_display"] = to_localtime_string(post.get("published_at"))

    body = renderer.render(
        route["template"],
        {
            "title": post.get("title", ""),
            "post": post,
        },
        request=request,
    )
    return html(body)
# パスとファイル名: wiwa/controllers/index.py
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html
from wiwa.db.post_repository import PostRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.utils.localtime import to_localtime_string

renderer = TemplateRenderer()
post_repo = PostRepository()
users_repo = UsersRepository()


def index(request, route=None):
    posts = post_repo.list_published()[:5]

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

    body = renderer.render(
        (route or {}).get("template", "html/index.html"),
        {
            "title": "Home",
            "posts": posts,
        },
        request=request,
    )
    return html(body)
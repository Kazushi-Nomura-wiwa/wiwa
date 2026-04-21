# パスとファイル名: wiwa/controllers/admin/post.py
from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found, redirect
from wiwa.db.post_repository import PostRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.services.post_service import PostService
from wiwa.utils.localtime import to_localtime_string

renderer = TemplateRenderer()
post_repo = PostRepository()
users_repo = UsersRepository()
post_service = PostService()


def _attach_display_names(posts: list[dict]) -> list[dict]:
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
        post["created_at_display"] = to_localtime_string(post.get("created_at"))
        post["updated_at_display"] = to_localtime_string(post.get("updated_at"))
        post["deleted_at_display"] = to_localtime_string(post.get("deleted_at"))
        post["purge_at_display"] = to_localtime_string(post.get("purge_at"))

    return posts


def list(request, route=None):
    posts = post_repo.list_all()
    posts = _attach_display_names(posts)

    body = renderer.render(
        route["template"],
        {
            "title": "Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def trash(request, route=None):
    posts = post_repo.list_trashed_all()
    posts = _attach_display_names(posts)

    body = renderer.render(
        route["template"],
        {
            "title": "Trash Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def new(request, route=None):
    if request.method == "GET":
        body = renderer.render(
            route["template"],
            {
                "title": "New Post",
                "error": "",
                "action": "/admin/post/new",
                "submit_label": "投稿する",
                "form": {
                    "_id": "",
                    "title": "",
                    "slug": "",
                    "body": "",
                    "status": "published",
                },
            },
            request=request,
        )
        return html(body)

    title = request.get_form("title").strip()
    slug = request.get_form("slug").strip()
    body_text = request.get_form("body").strip()
    status = request.get_form("status", "published").strip() or "published"

    if not title or not body_text:
        body = renderer.render(
            route["template"],
            {
                "title": "New Post",
                "error": "title と body は必須です。slug は空欄でも構いません。",
                "action": "/admin/post/new",
                "submit_label": "投稿する",
                "form": {
                    "_id": "",
                    "title": title,
                    "slug": slug,
                    "body": body_text,
                    "status": status,
                },
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    current_user = request.user or {}
    author_id = str(current_user.get("_id", "") or "")
    author_name = current_user.get("username", "")

    post_service.create_post(
        title=title,
        body=body_text,
        slug=slug,
        author_id=author_id,
        author_name=author_name,
        status=status,
    )

    return redirect("/admin/post/list")


def edit(request, route=None, id=None):
    post = post_repo.find_by_id(id)

    if not post:
        return not_found()

    body = renderer.render(
        route["template"],
        {
            "title": "Edit Post",
            "error": "",
            "action": f"/admin/post/update/{id}",
            "submit_label": "更新する",
            "form": {
                "_id": str(post.get("_id", "")),
                "title": post.get("title", ""),
                "slug": post.get("slug", ""),
                "body": post.get("body", ""),
                "status": post.get("status", "published"),
            },
        },
        request=request,
    )
    return html(body)


def update(request, route=None, id=None):
    if request.method != "POST":
        return redirect("/admin/post/list")

    post = post_repo.find_by_id(id)
    if not post:
        return not_found()

    title = request.get_form("title").strip()
    slug = request.get_form("slug").strip()
    body_text = request.get_form("body").strip()
    status = request.get_form("status", "published").strip() or "published"

    if not title or not body_text:
        body = renderer.render(
            route["template"],
            {
                "title": "Edit Post",
                "error": "title と body は必須です。slug は空欄でも構いません。",
                "action": f"/admin/post/update/{id}",
                "submit_label": "更新する",
                "form": {
                    "_id": str(post.get("_id", "")),
                    "title": title,
                    "slug": slug,
                    "body": body_text,
                    "status": status,
                },
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    current_user = request.user or {}
    author_id = str(current_user.get("_id", "") or post.get("author_id", "") or "")
    author_name = current_user.get("username", "") or post.get("author_name", "")

    ok = post_service.update_post(
        post_id=str(post.get("_id")),
        title=title,
        body=body_text,
        slug=slug,
        author_id=author_id,
        author_name=author_name,
        status=status,
    )

    if not ok:
        return not_found()

    return redirect("/admin/post/list")


def delete(request, route=None, id=None):
    post = post_repo.find_by_id(id)

    if not post:
        return not_found()

    if request.method == "POST":
        post_repo.delete_post_by_id(id)
        return redirect("/admin/post/list")

    body = renderer.render(
        route["template"],
        {
            "title": "Delete Post",
            "post": post,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def restore(request, route=None, id=None):
    if request.method != "POST":
        return redirect("/admin/post/trash")

    post = post_repo.find_by_id(id)
    if not post or post.get("status") != "trash":
        return not_found()

    ok = post_repo.restore_post_by_id(id, status="draft")
    if not ok:
        return not_found()

    return redirect("/admin/post/trash")
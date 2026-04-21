# パスとファイル名: wiwa/controllers/admin/post.py
from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import forbidden, html, not_found, redirect
from wiwa.services.post_service import PostService
from wiwa.utils.csrf import validate_csrf

renderer = TemplateRenderer()
post_service = PostService()


def _current_user_info(request) -> tuple[str, str]:
    current_user = request.user or {}
    author_id = str(current_user.get("_id", "") or "")
    author_name = current_user.get("username", "") or ""
    return author_id, author_name


def _split_tags(raw_tags: str) -> list[str]:
    return raw_tags.replace("　", " ").split()


def list(request, route=None):
    posts = post_service.list_posts()

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
    posts = post_service.list_posts(include_trashed=True)

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
                    "body": "",
                    "tags": "",
                    "status": "published",
                },
            },
            request=request,
        )
        return html(body)

    if not validate_csrf(request):
        return forbidden()

    title = request.get_form("title").strip()
    body_text = request.get_form("body").strip()
    raw_tags = request.get_form("tags").strip()
    tags = _split_tags(raw_tags)
    status = request.get_form("status", "published").strip() or "published"

    if not title or not body_text:
        body = renderer.render(
            route["template"],
            {
                "title": "New Post",
                "error": "title と body は必須です。",
                "action": "/admin/post/new",
                "submit_label": "投稿する",
                "form": {
                    "_id": "",
                    "title": title,
                    "body": body_text,
                    "tags": raw_tags,
                    "status": status,
                },
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    author_id, author_name = _current_user_info(request)

    post_service.create_post(
        title=title,
        body=body_text,
        author_id=author_id,
        author_name=author_name,
        status=status,
        tags=tags,
    )

    return redirect("/admin/post/list")


def edit(request, route=None, id=None):
    post = post_service.find_post(id)
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
                "body": post.get("body", ""),
                "tags": " ".join(post.get("tags", [])),
                "status": post.get("status", "published"),
            },
        },
        request=request,
    )
    return html(body)


def update(request, route=None, id=None):
    if request.method != "POST":
        return redirect("/admin/post/list")

    if not validate_csrf(request):
        return forbidden()

    post = post_service.find_post(id)
    if not post:
        return not_found()

    title = request.get_form("title").strip()
    body_text = request.get_form("body").strip()
    raw_tags = request.get_form("tags").strip()
    tags = _split_tags(raw_tags)
    status = request.get_form("status", "published").strip() or "published"
    slug = post.get("slug", "") or ""

    if not title or not body_text:
        body = renderer.render(
            route["template"],
            {
                "title": "Edit Post",
                "error": "title と body は必須です。",
                "action": f"/admin/post/update/{id}",
                "submit_label": "更新する",
                "form": {
                    "_id": str(post.get("_id", "")),
                    "title": title,
                    "body": body_text,
                    "tags": raw_tags,
                    "status": status,
                },
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    author_id = str(post.get("author_id", "") or "")
    author_name = post.get("author_name", "") or ""

    updated_by_id, updated_by_name = _current_user_info(request)

    ok = post_service.update_post(
        post_id=str(post.get("_id")),
        title=title,
        body=body_text,
        slug=slug,
        author_id=author_id,
        author_name=author_name,
        status=status,
        updated_by_id=updated_by_id,
        updated_by_name=updated_by_name,
        tags=tags,
    )

    if not ok:
        return not_found()

    return redirect("/admin/post/list")


def delete(request, route=None, id=None):
    post = post_service.find_post(id)
    if not post:
        return not_found()

    if request.method == "POST":
        if not validate_csrf(request):
            return forbidden()

        ok = post_service.delete_post(id)
        if not ok:
            return not_found()

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

    if not validate_csrf(request):
        return forbidden()

    ok = post_service.restore_post(id, status="draft")
    if not ok:
        return not_found()

    return redirect("/admin/post/trash")
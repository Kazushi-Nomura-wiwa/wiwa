# パスとファイル名: wiwa/controllers/mypage/post.py
from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import forbidden, html, not_found, redirect
from wiwa.db.post_repository import PostRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.services.post_service import PostService
from wiwa.utils.csrf import validate_csrf
from wiwa.utils.localtime import to_localtime_string

renderer = TemplateRenderer()
post_repo = PostRepository()
users_repo = UsersRepository()
post_service = PostService()


def _current_author_id(request) -> str:
    current_user = request.user or {}
    return str(current_user.get("_id", "") or "")


def _current_author_name(request) -> str:
    current_user = request.user or {}
    return current_user.get("username", "") or ""


def _find_own_post(request, post_id: str):
    author_id = _current_author_id(request)
    if not author_id:
        return None

    return post_repo.find_active_by_id_and_author_id(post_id, author_id)


def _find_own_trashed_post(request, post_id: str):
    author_id = _current_author_id(request)
    if not author_id:
        return None

    return post_repo.find_trashed_by_id_and_author_id(post_id, author_id)


def list(request, route=None):
    author_id = _current_author_id(request)
    posts = post_repo.list_by_author_id(author_id)

    author_ids = []
    for post in posts:
        post_author_id = post.get("author_id")
        if post_author_id:
            author_ids.append(post_author_id)

    display_names = users_repo.find_display_names_by_ids(author_ids)

    for post in posts:
        post_author_id = post.get("author_id", "")
        post["author_display_name"] = display_names.get(
            post_author_id,
            post.get("author_name", "")
        )
        post["published_at_display"] = to_localtime_string(post.get("published_at"))
        post["created_at_display"] = to_localtime_string(post.get("created_at"))
        post["updated_at_display"] = to_localtime_string(post.get("updated_at"))

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
    author_id = _current_author_id(request)
    posts = post_repo.list_trashed_by_author_id(author_id)

    author_ids = []
    for post in posts:
        post_author_id = post.get("author_id")
        if post_author_id:
            author_ids.append(post_author_id)

    display_names = users_repo.find_display_names_by_ids(author_ids)

    for post in posts:
        post_author_id = post.get("author_id", "")
        post["author_display_name"] = display_names.get(
            post_author_id,
            post.get("author_name", "")
        )
        post["published_at_display"] = to_localtime_string(post.get("published_at"))
        post["created_at_display"] = to_localtime_string(post.get("created_at"))
        post["updated_at_display"] = to_localtime_string(post.get("updated_at"))
        post["deleted_at_display"] = to_localtime_string(post.get("deleted_at"))
        post["purge_at_display"] = to_localtime_string(post.get("purge_at"))

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
                "action": "/mypage/post/new",
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

    if not validate_csrf(request):
        return forbidden()

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
                "action": "/mypage/post/new",
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

    author_id = _current_author_id(request)
    author_name = _current_author_name(request)

    post_service.create_post(
        title=title,
        body=body_text,
        slug=slug,
        author_id=author_id,
        author_name=author_name,
        status=status,
    )

    return redirect("/mypage/post/list")


def edit(request, route=None, id=None):
    post = _find_own_post(request, id)
    if not post:
        return not_found()

    body = renderer.render(
        route["template"],
        {
            "title": "Edit Post",
            "error": "",
            "action": f"/mypage/post/update/{id}",
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
        return redirect("/mypage/post/list")

    if not validate_csrf(request):
        return forbidden()

    post = _find_own_post(request, id)
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
                "action": f"/mypage/post/update/{id}",
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

    author_id = _current_author_id(request)
    author_name = _current_author_name(request) or post.get("author_name", "")

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

    return redirect("/mypage/post/list")


def delete(request, route=None, id=None):
    post = _find_own_post(request, id)
    if not post:
        return not_found()

    if request.method == "POST":
        if not validate_csrf(request):
            return forbidden()

        post_repo.delete_post_by_id(id)
        return redirect("/mypage/post/list")

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
        return redirect("/mypage/post/trash")

    if not validate_csrf(request):
        return forbidden()

    post = _find_own_trashed_post(request, id)
    if not post:
        return not_found()

    ok = post_repo.restore_post_by_id(id, status="draft")
    if not ok:
        return not_found()

    return redirect("/mypage/post/trash")
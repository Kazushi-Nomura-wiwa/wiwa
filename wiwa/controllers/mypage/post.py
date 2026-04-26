# パスとファイル名: wiwa/controllers/mypage/post.py

from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import forbidden, html, not_found, redirect
from wiwa.services.post_form_service import (
    current_user_info,
    empty_post_form,
    post_to_form,
    split_tags,
    submitted_post_form,
    validate_post_form,
)
from wiwa.services.post_service import PostService
from wiwa.utils.csrf import get_csrf_token, validate_csrf


renderer = TemplateRenderer()
post_service = PostService()


def list(request, route=None):
    author_id, _ = current_user_info(request)
    posts = post_service.list_posts(author_id=author_id)

    body = renderer.render_route(
        route,
        "html/mypage/post/list.html",
        {
            "title": "My Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def trash(request, route=None):
    author_id, _ = current_user_info(request)
    posts = post_service.list_posts(author_id=author_id, include_trashed=True)

    body = renderer.render_route(
        route,
        "html/mypage/post/trash.html",
        {
            "title": "My Trash Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def new(request, route=None):
    if request.method == "GET":
        body = renderer.render_route(
            route,
            "html/mypage/post/new.html",
            {
                "title": "New Post",
                "error": "",
                "action": "/mypage/post/new",
                "submit_label": "投稿する",
                "csrf_token": get_csrf_token(request),
                "form": empty_post_form(),
            },
            request=request,
        )
        return html(body)

    if not validate_csrf(request):
        return forbidden()

    form = submitted_post_form(request)
    error = validate_post_form(form)

    if error:
        body = renderer.render_route(
            route,
            "html/mypage/post/new.html",
            {
                "title": "New Post",
                "error": error,
                "action": "/mypage/post/new",
                "submit_label": "投稿する",
                "csrf_token": get_csrf_token(request),
                "form": form,
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    author_id, author_name = current_user_info(request)

    post_service.create_post(
        title=form["title"],
        body=form["body"],
        author_id=author_id,
        author_name=author_name,
        status=form["status"],
        tags=split_tags(form["tags"]),
    )

    return redirect("/mypage/post/list")


def edit(request, route=None, id=None):
    author_id, _ = current_user_info(request)
    post = post_service.find_own_post(id, author_id)
    if not post:
        return not_found()

    body = renderer.render_route(
        route,
        "html/mypage/post/edit.html",
        {
            "title": "Edit Post",
            "error": "",
            "action": f"/mypage/post/update/{id}",
            "submit_label": "更新する",
            "csrf_token": get_csrf_token(request),
            "form": post_to_form(post),
        },
        request=request,
    )
    return html(body)


def update(request, route=None, id=None):
    if request.method != "POST":
        return redirect("/mypage/post/list")

    if not validate_csrf(request):
        return forbidden()

    author_id, current_username = current_user_info(request)
    post = post_service.find_own_post(id, author_id)
    if not post:
        return not_found()

    form = submitted_post_form(request)
    error = validate_post_form(form)

    if error:
        form["_id"] = str(post.get("_id", ""))
        body = renderer.render_route(
            route,
            "html/mypage/post/edit.html",
            {
                "title": "Edit Post",
                "error": error,
                "action": f"/mypage/post/update/{id}",
                "submit_label": "更新する",
                "csrf_token": get_csrf_token(request),
                "form": form,
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    author_name = post.get("author_name", "") or current_username

    ok = post_service.update_post(
        post_id=str(post.get("_id")),
        title=form["title"],
        body=form["body"],
        slug=post.get("slug", "") or "",
        author_id=author_id,
        author_name=author_name,
        status=form["status"],
        updated_by_id=author_id,
        updated_by_name=current_username,
        tags=split_tags(form["tags"]),
    )

    if not ok:
        return not_found()

    return redirect("/mypage/post/list")


def delete(request, route=None, id=None):
    author_id, _ = current_user_info(request)
    post = post_service.find_own_post(id, author_id)
    if not post:
        return not_found()

    if request.method == "POST":
        if not validate_csrf(request):
            return forbidden()

        ok = post_service.delete_post(id, author_id=author_id)
        if not ok:
            return not_found()

        return redirect("/mypage/post/list")

    body = renderer.render_route(
        route,
        "html/mypage/post/delete.html",
        {
            "title": "Delete Post",
            "post": post,
            "retention_days": TRASH_RETENTION_DAYS,
            "csrf_token": get_csrf_token(request),
        },
        request=request,
    )
    return html(body)


def restore(request, route=None, id=None):
    if request.method != "POST":
        return redirect("/mypage/post/trash")

    if not validate_csrf(request):
        return forbidden()

    author_id, _ = current_user_info(request)
    ok = post_service.restore_post(id, status="draft", author_id=author_id)
    if not ok:
        return not_found()

    return redirect("/mypage/post/trash")
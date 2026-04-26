# パスとファイル名: wiwa/controllers/admin/post.py

from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found, redirect
from wiwa.services.post_form_service import (
    current_user_info,
    empty_post_form,
    post_to_form,
    split_tags,
    submitted_post_form,
    validate_post_form,
)
from wiwa.services.post_service import PostService


renderer = TemplateRenderer()
post_service = PostService()


def list(request, route=None, **params):
    posts = post_service.list_posts()

    body = renderer.render_route(
        route,
        "html/admin/post/list.html",
        {
            "title": "Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def trash(request, route=None, **params):
    posts = post_service.list_posts(include_trashed=True)

    body = renderer.render_route(
        route,
        "html/admin/post/trash.html",
        {
            "title": "Trash Post List",
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def new(request, route=None, **params):
    if request.method == "GET":
        body = renderer.render_route(
            route,
            "html/admin/post/new.html",
            {
                "title": "New Post",
                "error": "",
                "action": "/admin/post/new",
                "submit_label": "投稿する",
                "form": empty_post_form(),
            },
            request=request,
        )
        return html(body)

    form = submitted_post_form(request)
    error = validate_post_form(form)

    if error:
        body = renderer.render_route(
            route,
            "html/admin/post/new.html",
            {
                "title": "New Post",
                "error": error,
                "action": "/admin/post/new",
                "submit_label": "投稿する",
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

    return redirect("/admin/post/list")


def edit(request, route=None, id=None, **params):
    post = post_service.find_post(id)
    if not post:
        return not_found()

    body = renderer.render_route(
        route,
        "html/admin/post/edit.html",
        {
            "title": "Edit Post",
            "error": "",
            "action": f"/admin/post/update/{id}",
            "submit_label": "更新する",
            "form": post_to_form(post),
        },
        request=request,
    )
    return html(body)


def update(request, route=None, id=None, **params):
    if request.method != "POST":
        return redirect("/admin/post/list")

    post = post_service.find_post(id)
    if not post:
        return not_found()

    form = submitted_post_form(request)
    error = validate_post_form(form)

    if error:
        form["_id"] = str(post.get("_id", ""))
        body = renderer.render_route(
            route,
            "html/admin/post/edit.html",
            {
                "title": "Edit Post",
                "error": error,
                "action": f"/admin/post/update/{id}",
                "submit_label": "更新する",
                "form": form,
            },
            request=request,
        )
        return html(body, status="400 Bad Request")

    author_id = str(post.get("author_id", "") or "")
    author_name = post.get("author_name", "") or ""
    updated_by_id, updated_by_name = current_user_info(request)

    ok = post_service.update_post(
        post_id=str(post.get("_id")),
        title=form["title"],
        body=form["body"],
        slug=post.get("slug", "") or "",
        author_id=author_id,
        author_name=author_name,
        status=form["status"],
        updated_by_id=updated_by_id,
        updated_by_name=updated_by_name,
        tags=split_tags(form["tags"]),
    )

    if not ok:
        return not_found()

    return redirect("/admin/post/list")


def delete(request, route=None, id=None, **params):
    post = post_service.find_post(id)
    if not post:
        return not_found()

    if request.method == "POST":
        ok = post_service.delete_post(id)
        if not ok:
            return not_found()

        return redirect("/admin/post/list")

    body = renderer.render_route(
        route,
        "html/admin/post/delete.html",
        {
            "title": "Delete Post",
            "post": post,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def restore(request, route=None, id=None, **params):
    if request.method != "POST":
        return redirect("/admin/post/trash")

    ok = post_service.restore_post(id, status="draft")
    if not ok:
        return not_found()

    return redirect("/admin/post/trash")
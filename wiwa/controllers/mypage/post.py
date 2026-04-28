# パスとファイル名: wiwa/controllers/mypage/post.py
# Path and filename: wiwa/controllers/mypage/post.py

# マイページ投稿管理コントローラ
# MyPage post management controller
#
# URL
# URL
#   /mypage/post/list
#   /mypage/post/trash
#   /mypage/post/new
#   /mypage/post/edit/<id>
#   /mypage/post/update/<id>
#   /mypage/post/delete/<id>
#   /mypage/post/restore/<id>
#
# 処理の流れ（一覧）
# Flow (list)
#   1. 自分の投稿取得
#      Fetch user's posts
#   2. テンプレート描画
#      Render template
#
# 処理の流れ（ゴミ箱）
# Flow (trash)
#   1. ゴミ箱投稿取得
#      Fetch trashed posts
#   2. テンプレート描画
#      Render template
#
# 処理の流れ（作成）
# Flow (create)
#   1. GET時はフォーム表示
#      Render form on GET
#   2. POST時は入力取得
#      Get submitted form
#   3. 入力検証
#      Validate form
#   4. 投稿作成
#      Create post
#
# 処理の流れ（編集）
# Flow (edit)
#   1. 投稿取得
#      Fetch post
#   2. テンプレート描画
#      Render template
#
# 処理の流れ（更新）
# Flow (update)
#   1. 投稿取得
#      Fetch post
#   2. 入力取得
#      Get submitted form
#   3. 入力検証
#      Validate form
#   4. 投稿更新
#      Update post
#
# 処理の流れ（削除）
# Flow (delete)
#   1. 投稿取得
#      Fetch post
#   2. POST時は削除実行
#      Execute delete
#   3. 確認画面描画
#      Render confirmation
#
# 処理の流れ（復元）
# Flow (restore)
#   1. POST時は復元実行
#      Execute restore
#   2. リダイレクト
#      Redirect

from wiwa.config import TRASH_RETENTION_DAYS
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import forbidden, html, not_found, redirect
from wiwa.core.i18n import t
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
    """
    自分の投稿一覧を表示
    Display user's post list
    """
    author_id, _ = current_user_info(request)
    posts = post_service.list_posts(author_id=author_id)

    body = renderer.render_route(
        route,
        "html/mypage/post/list.html",
        {
            "title": t("mypage.post.list.title"),
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def trash(request, route=None):
    """
    自分のゴミ箱内の投稿一覧を表示
    Display user's trashed post list
    """
    author_id, _ = current_user_info(request)
    posts = post_service.list_posts(author_id=author_id, include_trashed=True)

    body = renderer.render_route(
        route,
        "html/mypage/post/trash.html",
        {
            "title": t("mypage.post.trash.title"),
            "posts": posts,
            "retention_days": TRASH_RETENTION_DAYS,
        },
        request=request,
    )
    return html(body)


def new(request, route=None):
    """
    新規投稿を作成
    Create a new post
    """
    if request.method == "GET":
        body = renderer.render_route(
            route,
            "html/mypage/post/new.html",
            {
                "title": t("mypage.post.new.title"),
                "error": "",
                "action": "/mypage/post/new",
                "submit_label": t("mypage.post.submit.create"),
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
                "title": t("mypage.post.new.title"),
                "error": error,
                "action": "/mypage/post/new",
                "submit_label": t("mypage.post.submit.create"),
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
    """
    投稿編集画面を表示
    Display the post edit screen
    """
    author_id, _ = current_user_info(request)
    post = post_service.find_own_post(id, author_id)
    if not post:
        return not_found()

    body = renderer.render_route(
        route,
        "html/mypage/post/edit.html",
        {
            "title": t("mypage.post.edit.title"),
            "error": "",
            "action": f"/mypage/post/update/{id}",
            "submit_label": t("mypage.post.submit.update"),
            "csrf_token": get_csrf_token(request),
            "form": post_to_form(post),
        },
        request=request,
    )
    return html(body)


def update(request, route=None, id=None):
    """
    投稿を更新
    Update the post
    """
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
                "title": t("mypage.post.edit.title"),
                "error": error,
                "action": f"/mypage/post/update/{id}",
                "submit_label": t("mypage.post.submit.update"),
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
    """
    投稿をゴミ箱へ移動
    Move the post to trash
    """
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
            "title": t("mypage.post.delete.title"),
            "post": post,
            "retention_days": TRASH_RETENTION_DAYS,
            "csrf_token": get_csrf_token(request),
        },
        request=request,
    )
    return html(body)


def restore(request, route=None, id=None):
    """
    ゴミ箱の投稿を復元
    Restore the trashed post
    """
    if request.method != "POST":
        return redirect("/mypage/post/trash")

    if not validate_csrf(request):
        return forbidden()

    author_id, _ = current_user_info(request)
    ok = post_service.restore_post(id, status="draft", author_id=author_id)
    if not ok:
        return not_found()

    return redirect("/mypage/post/trash")
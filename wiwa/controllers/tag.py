# パスとファイル名: wiwa/controllers/tag.py
# Path and filename: wiwa/controllers/tag.py

# タグ別投稿一覧コントローラ
# Tag archive controller
#
# URL
# URL
#   /tag/<name>
#
# 処理の流れ
# Flow
#   1. URL上のタグ名を復元
#      Decode tag name from URL
#   2. タグ名を検証
#      Validate tag name
#   3. タグに紐づく投稿を取得
#      Fetch posts by tag
#   4. テンプレート描画
#      Render template
#   5. HTMLレスポンスを返す
#      Return HTML response

from urllib.parse import unquote

from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html, not_found
from wiwa.services.post_service import PostService


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# 投稿サービス
# Post service
post_service = PostService()


def name(request, route=None, name: str = ""):
    """
    タグ別投稿一覧を表示する
    Render posts by tag
    """

    # URLエンコードされたタグ名を復元
    # Decode URL-encoded tag name
    tag_name = unquote(name).strip()

    # タグ名が空の場合は404
    # Return 404 if tag name is empty
    if not tag_name:
        return not_found()

    # タグに紐づく投稿を取得
    # Fetch posts associated with the tag
    posts = post_service.list_posts_by_tag(tag_name)

    # タグ一覧テンプレートを描画
    # Render tag archive template
    body = renderer.render_route(
        route,
        "html/tag/name.html",
        {
            "title": t("tag_title", tag_name=tag_name),
            "tag_name": tag_name,
            "posts": posts,
            "total_count": len(posts),
        },
        request=request,
    )

    # HTMLレスポンスを返す
    # Return HTML response
    return html(body)
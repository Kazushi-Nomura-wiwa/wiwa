# パスとファイル名: wiwa/controllers/index.py
# Path and filename: wiwa/controllers/index.py

# トップページコントローラ
# Home page controller
#
# URL
# URL
#   /
#
# 処理の流れ
# Flow
#   1. 公開済み投稿を取得
#      Fetch published posts
#   2. 表示用データに変換
#      Build view data
#   3. テンプレート描画
#      Render template
#   4. HTMLレスポンスを返す
#      Return HTML response

from wiwa.config import HOME_POSTS_LIMIT
from wiwa.core.i18n import t
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import html
from wiwa.db.post_repository import PostRepository
from wiwa.services.post_view_service import PostViewService


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# 投稿リポジトリ
# Post repository
post_repo = PostRepository()

# 投稿表示用サービス
# Post view service
post_view_service = PostViewService()


def index(request, route=None):
    """
    トップページを表示する
    Render the home page
    """

    # 公開済み投稿を設定件数分取得
    # Fetch published posts with configured limit
    posts = post_repo.list_published(limit=HOME_POSTS_LIMIT)

    # テンプレート表示用の投稿データに変換
    # Convert posts into template-friendly view data
    posts = post_view_service.build_post_list(posts)

    # トップページテンプレートを描画
    # Render home page template
    body = renderer.render_route(
        route,
        "html/index.html",
        {
            "title": t("home_title"),
            "posts": posts,
        },
        request=request,
    )

    # HTMLレスポンスを返す
    # Return HTML response
    return html(body)
# パスとファイル名: wiwa/services/post_view_service.py
# Path and filename: wiwa/services/post_view_service.py

# 投稿表示サービス
# Post view service
#
# 概要
# Summary
#   投稿データを表示用に変換し、著者名や日時を整形する
#   Transform post data for display and format author and timestamps
#
# 処理の流れ
# Flow
#   1. 著者ID収集
#      Collect author ids
#   2. 表示名取得
#      Fetch display names
#   3. 表示用データ付与
#      Attach display fields
#   4. 日時フォーマット
#      Format timestamps

from wiwa.db.users_repository import UsersRepository
from wiwa.utils.localtime import to_localtime_string


class PostViewService:
    def __init__(self):
        """
        サービス初期化
        Initialize service
        """
        self.users_repo = UsersRepository()

    # ----------------------------
    # 一覧表示処理
    # List view operations
    # ----------------------------

    def build_post_list(self, posts: list[dict]) -> list[dict]:
        """
        投稿一覧整形
        Build post list view
        """
        author_ids = []

        # 著者ID収集
        # Collect author ids
        for post in posts:
            author_id = post.get("author_id")
            if author_id:
                author_ids.append(author_id)

        # 表示名取得
        # Fetch display names
        display_names = self.users_repo.find_display_names_by_ids(author_ids)

        # 表示用データ付与
        # Attach display fields
        for post in posts:
            post["author_display_name"] = self._author_display_name(
                post,
                display_names,
            )

            post["published_at_display"] = to_localtime_string(
                post.get("published_at")
            )

        return posts

    # ----------------------------
    # 詳細表示処理
    # Detail view operations
    # ----------------------------

    def build_post(self, post: dict) -> dict:
        """
        投稿詳細整形
        Build post detail view
        """
        if not post:
            return {}

        author_display_name = post.get("author_name", "")
        author_id = post.get("author_id", "")

        # 著者名補完
        # Resolve author display name
        if author_id:
            user = self.users_repo.find_by_id(author_id)
            if user:
                author_display_name = (
                    user.get("display_name")
                    or user.get("username")
                    or author_display_name
                )

        post["author_display_name"] = author_display_name

        # 日時フォーマット
        # Format timestamp
        post["published_at_display"] = to_localtime_string(
            post.get("published_at")
        )

        return post

    # ----------------------------
    # 内部処理
    # Internal utilities
    # ----------------------------

    def _author_display_name(self, post: dict, display_names: dict) -> str:
        """
        著者表示名取得
        Resolve author display name
        """
        author_id = post.get("author_id", "")

        return display_names.get(
            author_id,
            post.get("author_name", ""),
        )
# パスとファイル名: wiwa/services/post_view_service.py

from wiwa.db.users_repository import UsersRepository
from wiwa.utils.localtime import to_localtime_string


class PostViewService:
    def __init__(self):
        self.users_repo = UsersRepository()

    def build_post_list(self, posts: list[dict]) -> list[dict]:
        author_ids = []

        for post in posts:
            author_id = post.get("author_id")
            if author_id:
                author_ids.append(author_id)

        display_names = self.users_repo.find_display_names_by_ids(author_ids)

        for post in posts:
            post["author_display_name"] = self._author_display_name(
                post,
                display_names,
            )
            post["published_at_display"] = to_localtime_string(
                post.get("published_at")
            )

        return posts

    def build_post(self, post: dict) -> dict:
        if not post:
            return {}

        author_display_name = post.get("author_name", "")
        author_id = post.get("author_id", "")

        if author_id:
            user = self.users_repo.find_by_id(author_id)
            if user:
                author_display_name = (
                    user.get("display_name")
                    or user.get("username")
                    or author_display_name
                )

        post["author_display_name"] = author_display_name
        post["published_at_display"] = to_localtime_string(
            post.get("published_at")
        )

        return post

    def _author_display_name(self, post: dict, display_names: dict) -> str:
        author_id = post.get("author_id", "")
        return display_names.get(
            author_id,
            post.get("author_name", ""),
        )
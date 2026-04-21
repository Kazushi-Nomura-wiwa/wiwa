# パスとファイル名: wiwa/services/post_service.py
from datetime import UTC, datetime

from wiwa.db.post_repository import PostRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.utils.localtime import to_localtime_string


class PostService:
    def __init__(self):
        self.post_repo = PostRepository()
        self.users_repo = UsersRepository()

    def create_post(
        self,
        title: str,
        body: str,
        author_id: str,
        author_name: str,
        status: str = "published",
        tags: list[str] | None = None,
    ) -> str:
        now = datetime.now(UTC)

        final_slug = self._build_unique_slug(
            raw_slug=title,
            fallback_source=title,
        )

        post = {
            "title": title,
            "body": body,
            "slug": final_slug,
            "tags": tags or [],
            "author_id": author_id,
            "author_name": author_name,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        if status == "published":
            post["published_at"] = now
        else:
            post["published_at"] = None

        return self.post_repo.insert_post(post)

    def update_post(
        self,
        post_id: str,
        title: str,
        body: str,
        slug: str,
        author_id: str,
        author_name: str,
        status: str = "published",
        updated_by_id: str | None = None,
        updated_by_name: str | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        current_post = self.post_repo.find_by_id(post_id)
        if not current_post:
            return False

        final_slug = self._build_unique_slug(
            raw_slug=slug,
            fallback_source=title,
            exclude_post_id=post_id,
        )

        now = datetime.now(UTC)

        update_data = {
            "title": title,
            "body": body,
            "slug": final_slug,
            "tags": tags or [],
            "author_id": author_id,
            "author_name": author_name,
            "status": status,
            "updated_at": now,
        }

        current_status = current_post.get("status", "")
        current_published_at = current_post.get("published_at")

        if updated_by_id:
            update_data["updated_by_id"] = updated_by_id

        if updated_by_name:
            update_data["updated_by_name"] = updated_by_name

        if status == "published":
            if current_status != "published" or not current_published_at:
                update_data["published_at"] = now
        else:
            update_data["published_at"] = None

        return self.post_repo.update_post_by_id(post_id, update_data)

    def list_posts(
        self,
        author_id: str | None = None,
        include_trashed: bool = False,
    ) -> list[dict]:
        if include_trashed:
            if author_id:
                posts = self.post_repo.list_trashed_by_author_id(author_id)
            else:
                posts = self.post_repo.list_trashed_all()
        else:
            if author_id:
                posts = self.post_repo.list_by_author_id(author_id)
            else:
                posts = self.post_repo.list_all()

        return self._enrich_posts(posts, include_deleted=include_trashed)

    def list_posts_by_tag(self, tag: str) -> list[dict]:
        posts = self.post_repo.list_published_by_tag(tag)
        return self._enrich_posts(posts, include_deleted=False)

    def find_post(self, post_id: str):
        return self.post_repo.find_by_id(post_id)

    def find_own_post(self, post_id: str, author_id: str):
        if not author_id:
            return None
        return self.post_repo.find_active_by_id_and_author_id(post_id, author_id)

    def find_own_trashed_post(self, post_id: str, author_id: str):
        if not author_id:
            return None
        return self.post_repo.find_trashed_by_id_and_author_id(post_id, author_id)

    def delete_post(self, post_id: str, author_id: str | None = None) -> bool:
        if author_id:
            post = self.find_own_post(post_id, author_id)
        else:
            post = self.find_post(post_id)

        if not post:
            return False

        return self.post_repo.delete_post_by_id(post_id)

    def restore_post(
        self,
        post_id: str,
        status: str = "draft",
        author_id: str | None = None,
    ) -> bool:
        if author_id:
            post = self.find_own_trashed_post(post_id, author_id)
        else:
            post = self.find_post(post_id)
            if not post or post.get("status") != "trash":
                return False

        return self.post_repo.restore_post_by_id(post_id, status=status)

    def _enrich_posts(
        self,
        posts: list[dict],
        include_deleted: bool = False,
    ) -> list[dict]:
        author_ids = []

        for post in posts:
            post_author_id = post.get("author_id")
            if post_author_id:
                author_ids.append(post_author_id)

        display_names = self.users_repo.find_display_names_by_ids(author_ids)

        enriched_posts = []

        for post in posts:
            item = dict(post)
            post_author_id = item.get("author_id", "")

            item["author_display_name"] = display_names.get(
                post_author_id,
                item.get("author_name", "")
            )
            item["published_at_display"] = to_localtime_string(item.get("published_at"))
            item["created_at_display"] = to_localtime_string(item.get("created_at"))
            item["updated_at_display"] = to_localtime_string(item.get("updated_at"))
            item["tags_display"] = " ".join(item.get("tags", []))

            if include_deleted:
                item["deleted_at_display"] = to_localtime_string(item.get("deleted_at"))
                item["purge_at_display"] = to_localtime_string(item.get("purge_at"))

            enriched_posts.append(item)

        return enriched_posts

    def _build_unique_slug(
        self,
        raw_slug: str,
        fallback_source: str,
        exclude_post_id: str | None = None,
    ) -> str:
        base_slug = self.post_repo.normalize_slug(raw_slug)

        if not base_slug:
            base_slug = self.post_repo.normalize_slug(fallback_source)

        if not base_slug:
            base_slug = self._generate_fallback_slug()

        slug = base_slug
        counter = 2

        while self.post_repo.slug_exists(slug, exclude_post_id=exclude_post_id):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _generate_fallback_slug(self) -> str:
        return "post-" + datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
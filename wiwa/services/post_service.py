# パスとファイル名: wiwa/services/post_service.py
from datetime import UTC, datetime

from wiwa.db.post_repository import PostRepository


class PostService:
    def __init__(self):
        self.post_repo = PostRepository()

    def create_post(
        self,
        title: str,
        body: str,
        slug: str,
        author_id: str,
        author_name: str,
        status: str = "published",
    ) -> str:
        now = datetime.now(UTC)

        final_slug = self._build_unique_slug(
            raw_slug=slug,
            fallback_source=title,
        )

        post = {
            "title": title,
            "body": body,
            "slug": final_slug,
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
    ) -> bool:
        current_post = self.post_repo.find_by_id(post_id)
        if not current_post:
            return False

        final_slug = self._build_unique_slug(
            raw_slug=slug,
            fallback_source=title,
            exclude_post_id=post_id,
        )

        update_data = {
            "title": title,
            "body": body,
            "slug": final_slug,
            "author_id": author_id,
            "author_name": author_name,
            "status": status,
            "updated_at": datetime.now(UTC),
        }

        current_status = current_post.get("status", "")
        current_published_at = current_post.get("published_at")

        if status == "published":
            if current_status != "published" or not current_published_at:
                update_data["published_at"] = datetime.now(UTC)
        else:
            update_data["published_at"] = None

        return self.post_repo.update_post_by_id(post_id, update_data)

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
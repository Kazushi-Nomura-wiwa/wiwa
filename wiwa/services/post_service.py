# パスとファイル名: wiwa/services/post_service.py
from datetime import UTC, datetime

from wiwa.db.post_repository import PostRepository


class PostService:
    def __init__(self):
        self.repo = PostRepository()

    def create_post(
        self,
        title: str,
        body: str,
        slug: str = "",
        author_id: str = "",
        author_name: str = "",
        status: str = "published",
        published_at=None,
    ) -> str:
        normalized_slug = self._build_unique_slug(title=title, slug=slug)

        now = datetime.now(UTC)
        if published_at is None and status == "published":
            published_at = now

        post = {
            "title": (title or "").strip(),
            "body": body or "",
            "slug": normalized_slug,
            "author_id": author_id or "",
            "author_name": author_name or "",
            "status": status or "draft",
            "published_at": published_at,
            "created_at": now,
            "updated_at": now,
        }

        return self.repo.insert_post(post)

    def update_post(
        self,
        post_id: str,
        title: str,
        body: str,
        slug: str = "",
        author_id: str = "",
        author_name: str = "",
        status: str = "published",
        published_at=None,
    ) -> bool:
        existing = self.repo.find_by_id(post_id)
        if not existing:
            return False

        normalized_slug = self._build_unique_slug(
            title=title,
            slug=slug,
            exclude_post_id=post_id,
        )

        current_status = existing.get("status", "draft")
        current_published_at = existing.get("published_at")

        if published_at is None:
            if current_published_at:
                published_at = current_published_at
            elif status == "published" and current_status != "published":
                published_at = datetime.now(UTC)

        post = {
            "title": (title or "").strip(),
            "body": body or "",
            "slug": normalized_slug,
            "author_id": author_id or "",
            "author_name": author_name or "",
            "status": status or "draft",
            "published_at": published_at,
            "updated_at": datetime.now(UTC),
        }

        return self.repo.update_post_by_id(post_id, post)

    def _build_unique_slug(
        self,
        title: str,
        slug: str = "",
        exclude_post_id: str | None = None,
    ) -> str:
        base_slug = (slug or title or "").strip()
        normalized = self.repo.normalize_slug(base_slug)

        if not normalized:
            raise ValueError("slug を生成できません。title または slug を入力してください。")

        if not self.repo.slug_exists(normalized, exclude_post_id=exclude_post_id):
            return normalized

        counter = 2
        while True:
            candidate = f"{normalized}-{counter}"
            if not self.repo.slug_exists(candidate, exclude_post_id=exclude_post_id):
                return candidate
            counter += 1
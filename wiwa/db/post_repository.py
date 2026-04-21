# パスとファイル名: wiwa/db/post_repository.py
import re
import unicodedata
from datetime import UTC, datetime, timedelta

from bson import ObjectId

from wiwa.db.mongo import get_collection
from wiwa.config import TRASH_RETENTION_DAYS


class PostRepository:
    def __init__(self):
        self.collection = get_collection("posts")

    def insert_post(self, post: dict) -> str:
        result = self.collection.insert_one(post)
        return str(result.inserted_id)

    def list_all(self) -> list[dict]:
        posts = list(
            self.collection
            .find({"status": {"$ne": "trash"}})
            .sort("created_at", -1)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def list_by_author_id(self, author_id: str) -> list[dict]:
        posts = list(
            self.collection
            .find({
                "author_id": author_id,
                "status": {"$ne": "trash"},
            })
            .sort("created_at", -1)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def list_trashed_all(self) -> list[dict]:
        posts = list(
            self.collection
            .find({"status": "trash"})
            .sort("deleted_at", -1)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def list_trashed_by_author_id(self, author_id: str) -> list[dict]:
        posts = list(
            self.collection
            .find({
                "author_id": author_id,
                "status": "trash",
            })
            .sort("deleted_at", -1)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def list_published(self, limit: int = 10, skip: int = 0) -> list[dict]:
        posts = list(
            self.collection
            .find({"status": "published"})
            .sort("published_at", -1)
            .skip(skip)
            .limit(limit)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def count_published(self) -> int:
        return self.collection.count_documents({"status": "published"})

    def find_by_id(self, post_id: str) -> dict | None:
        if not ObjectId.is_valid(post_id):
            return None

        post = self.collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def find_active_by_id(self, post_id: str) -> dict | None:
        if not ObjectId.is_valid(post_id):
            return None

        post = self.collection.find_one({
            "_id": ObjectId(post_id),
            "status": {"$ne": "trash"},
        })
        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def find_by_id_and_author_id(self, post_id: str, author_id: str) -> dict | None:
        if not ObjectId.is_valid(post_id):
            return None

        post = self.collection.find_one({
            "_id": ObjectId(post_id),
            "author_id": author_id,
        })
        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def find_active_by_id_and_author_id(self, post_id: str, author_id: str) -> dict | None:
        if not ObjectId.is_valid(post_id):
            return None

        post = self.collection.find_one({
            "_id": ObjectId(post_id),
            "author_id": author_id,
            "status": {"$ne": "trash"},
        })
        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def find_trashed_by_id_and_author_id(self, post_id: str, author_id: str) -> dict | None:
        if not ObjectId.is_valid(post_id):
            return None

        post = self.collection.find_one({
            "_id": ObjectId(post_id),
            "author_id": author_id,
            "status": "trash",
        })
        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def find_published_by_slug(self, slug: str) -> dict | None:
        post = self.collection.find_one({
            "slug": slug,
            "status": "published",
        })

        if not post:
            return None

        post["_id"] = str(post["_id"])
        return post

    def update_post_by_id(self, post_id: str, post: dict) -> bool:
        if not ObjectId.is_valid(post_id):
            return False

        post["updated_at"] = datetime.now(UTC)

        result = self.collection.update_one(
            {
                "_id": ObjectId(post_id),
                "status": {"$ne": "trash"},
            },
            {"$set": post},
        )
        return result.modified_count > 0

    def delete_post_by_id(self, post_id: str) -> bool:
        if not ObjectId.is_valid(post_id):
            return False

        now = datetime.now(UTC)
        purge_at = now + timedelta(days=TRASH_RETENTION_DAYS)

        result = self.collection.update_one(
            {
                "_id": ObjectId(post_id),
                "status": {"$ne": "trash"},
            },
            {
                "$set": {
                    "status": "trash",
                    "deleted_at": now,
                    "purge_at": purge_at,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count > 0

    def restore_post_by_id(self, post_id: str, status: str = "draft") -> bool:
        if not ObjectId.is_valid(post_id):
            return False

        now = datetime.now(UTC)

        result = self.collection.update_one(
            {
                "_id": ObjectId(post_id),
                "status": "trash",
            },
            {
                "$set": {
                    "status": status,
                    "updated_at": now,
                },
                "$unset": {
                    "deleted_at": "",
                    "purge_at": "",
                },
            },
        )
        return result.modified_count > 0

    def delete_post_permanently_by_id(self, post_id: str) -> bool:
        if not ObjectId.is_valid(post_id):
            return False

        result = self.collection.delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count > 0

    def slug_exists(self, slug: str, exclude_post_id: str | None = None) -> bool:
        query = {
            "slug": slug,
            "status": {"$ne": "trash"},
        }

        if exclude_post_id and ObjectId.is_valid(exclude_post_id):
            query["_id"] = {"$ne": ObjectId(exclude_post_id)}

        return self.collection.find_one(query) is not None

    def normalize_slug(self, value: str) -> str:
        text = (value or "").strip()
        text = unicodedata.normalize("NFKC", text).lower()

        text = text.replace("/", "-")
        text = text.replace("\\", "-")
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"[^a-z0-9\-_ぁ-んァ-ヶ一-龠ー]", "-", text)
        text = re.sub(r"-{2,}", "-", text)
        text = text.strip("-")

        return text

    def publish_post(self, post_id: str) -> bool:
        if not ObjectId.is_valid(post_id):
            return False

        now = datetime.now(UTC)

        result = self.collection.update_one(
            {
                "_id": ObjectId(post_id),
                "status": {"$ne": "trash"},
            },
            {
                "$set": {
                    "status": "published",
                    "published_at": now,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count > 0

    def list_published_by_tag(self, tag: str) -> list[dict]:
        posts = list(
            self.collection.find(
                {
                    "status": "published",
                    "tags": tag,
                }
            ).sort("published_at", -1)
        )

        for post in posts:
            post["_id"] = str(post["_id"])

        return posts

    def list_tags(self) -> list[str]:
        tags = self.collection.distinct("tags", {"status": "published"})
        return sorted([tag for tag in tags if tag])
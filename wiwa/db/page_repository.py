# パスとファイル名: wiwa/db/page_repository.py
# Path and filename: wiwa/db/page_repository.py

# 固定ページリポジトリ
# Page repository
#
# 概要
# Summary
#   固定ページのCRUD操作を提供する
#   Provide CRUD operations for pages
#
# 処理の流れ
# Flow
#   1. ページ取得
#      Fetch pages
#   2. ページ作成
#      Create page
#   3. ページ更新
#      Update page
#   4. ページ削除
#      Delete page

from datetime import UTC, datetime

from bson import ObjectId

from wiwa.db.mongo import get_collection


class PageRepository:
    def __init__(self):
        """
        リポジトリ初期化
        Initialize repository
        """
        self.collection = get_collection("pages")

    def find_all(self):
        """
        全ページ取得
        Fetch all pages
        """
        pages = list(
            self.collection.find().sort("created_at", -1)
        )

        for page in pages:
            page["_id"] = str(page["_id"])

        return pages

    def find_by_id(self, page_id: str):
        """
        IDでページ取得
        Fetch page by id
        """
        if not ObjectId.is_valid(page_id):
            return None

        page = self.collection.find_one({
            "_id": ObjectId(page_id)
        })

        if page:
            page["_id"] = str(page["_id"])

        return page

    def find_by_slug(self, slug: str):
        """
        slugで公開ページ取得
        Fetch published page by slug
        """
        return self.collection.find_one({
            "slug": slug,
            "status": "published",
        })

    def find_any_by_slug(self, slug: str):
        """
        slugでページ取得（状態問わず）
        Fetch page by slug (any status)
        """
        return self.collection.find_one({
            "slug": slug
        })

    def create(self, data: dict):
        """
        ページ作成
        Create page
        """
        now = datetime.now(UTC)

        document = {
            "title": data.get("title", "").strip(),
            "slug": data.get("slug", "").strip(),
            "body": data.get("body", ""),
            "body_json": data.get("body_json", {}),
            "status": data.get("status", "draft"),
            "created_at": now,
            "updated_at": now,
            "published_at": now if data.get("status") == "published" else None,
            "created_by": data.get("created_by"),
            "updated_by": data.get("updated_by"),
        }

        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def update(self, page_id: str, data: dict):
        """
        ページ更新
        Update page
        """
        if not ObjectId.is_valid(page_id):
            return False

        update_data = {
            "title": data.get("title", "").strip(),
            "slug": data.get("slug", "").strip(),
            "body": data.get("body", ""),
            "body_json": data.get("body_json", {}),
            "status": data.get("status", "draft"),
            "updated_at": datetime.now(UTC),
            "updated_by": data.get("updated_by"),
        }

        # 初回公開時のみpublished_atを設定
        # Set published_at only on first publish
        if data.get("status") == "published":
            page = self.find_by_id(page_id)
            if page and not page.get("published_at"):
                update_data["published_at"] = datetime.now(UTC)

        result = self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$set": update_data}
        )

        return result.modified_count > 0

    def delete(self, page_id: str):
        """
        ページ削除
        Delete page
        """
        if not ObjectId.is_valid(page_id):
            return False

        result = self.collection.delete_one({
            "_id": ObjectId(page_id)
        })

        return result.deleted_count > 0
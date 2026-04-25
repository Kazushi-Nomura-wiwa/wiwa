# パスとファイル名: wiwa/services/page_service.py

from datetime import datetime
from bson import ObjectId
import json

from wiwa.db.mongo import get_db


class PageService:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.pages

    # ----------------------------
    # 共通
    # ----------------------------

    def _normalize_body_json(self, raw_body_json) -> str:
        """
        Editor.jsのJSONを安全に正規化して保存する。
        MongoDBにはJSON文字列として保存する。
        """
        empty_data = {"blocks": []}

        if not raw_body_json:
            return json.dumps(empty_data, ensure_ascii=False)

        if isinstance(raw_body_json, dict):
            return json.dumps(raw_body_json, ensure_ascii=False)

        if isinstance(raw_body_json, list):
            return json.dumps({"blocks": raw_body_json}, ensure_ascii=False)

        if not isinstance(raw_body_json, str):
            return json.dumps(empty_data, ensure_ascii=False)

        raw_body_json = raw_body_json.strip()

        if not raw_body_json:
            return json.dumps(empty_data, ensure_ascii=False)

        try:
            parsed = json.loads(raw_body_json)
        except json.JSONDecodeError:
            return json.dumps(empty_data, ensure_ascii=False)

        if isinstance(parsed, dict):
            if "blocks" not in parsed:
                parsed["blocks"] = []
            return json.dumps(parsed, ensure_ascii=False)

        if isinstance(parsed, list):
            return json.dumps({"blocks": parsed}, ensure_ascii=False)

        return json.dumps(empty_data, ensure_ascii=False)

    def _build_path(self, slug: str, parent: dict | None = None) -> str:
        slug = (slug or "").strip().strip("/")

        if parent:
            parent_path = (parent.get("path") or "").rstrip("/")
            return f"{parent_path}/{slug}"

        return f"/{slug}"

    # ----------------------------
    # Create
    # ----------------------------

    def create_page(self, data: dict) -> tuple[str | None, str | None]:
        title = (data.get("title") or "").strip()
        slug = (data.get("slug") or "").strip().strip("/")
        raw_body_json = data.get("body_json", "")
        status = (data.get("status") or "draft").strip()

        if not title:
            return None, "タイトルは必須です。"

        if not slug:
            return None, "スラッグは必須です。"

        body_json = self._normalize_body_json(raw_body_json)
        path = self._build_path(slug)

        now = datetime.utcnow()

        doc = {
            "title": title,
            "slug": slug,
            "path": path,
            "body_json": body_json,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        try:
            result = self.collection.insert_one(doc)
            return str(result.inserted_id), None
        except Exception:
            return None, "ページの保存に失敗しました。"

    # ----------------------------
    # Read
    # ----------------------------

    def list_pages(self) -> list[dict]:
        return list(self.collection.find().sort("created_at", -1))

    def get_page_by_id(self, page_id: str) -> dict | None:
        try:
            return self.collection.find_one({"_id": ObjectId(page_id)})
        except Exception:
            return None

    def get_page_by_path(self, path: str) -> dict | None:
        return self.collection.find_one({
            "path": path,
            "status": "published",
        })

    # ----------------------------
    # Update
    # ----------------------------

    def update_page(self, page_id: str, data: dict) -> tuple[bool, str | None]:
        page = self.get_page_by_id(page_id)
        if not page:
            return False, "ページが見つかりません。"

        title = (data.get("title") or "").strip()
        slug = (data.get("slug") or "").strip().strip("/")
        raw_body_json = data.get("body_json", "")
        status = (data.get("status") or "draft").strip()

        if not title:
            return False, "タイトルは必須です。"

        if not slug:
            return False, "スラッグは必須です。"

        body_json = self._normalize_body_json(raw_body_json)
        path = self._build_path(slug)

        update_doc = {
            "title": title,
            "slug": slug,
            "path": path,
            "body_json": body_json,
            "status": status,
            "updated_at": datetime.utcnow(),
        }

        try:
            self.collection.update_one(
                {"_id": ObjectId(page_id)},
                {"$set": update_doc},
            )
            return True, None
        except Exception:
            return False, "更新に失敗しました。"

    # ----------------------------
    # Delete
    # ----------------------------

    def delete_page(self, page_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(page_id)})
            return result.deleted_count > 0
        except Exception:
            return False
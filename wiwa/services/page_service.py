# パスとファイル名: wiwa/services/page_service.py

import json
import re

from wiwa.config import RESERVED_SLUGS
from wiwa.db.page_repository import PageRepository
from wiwa.services.editorjs_builder import EditorJSBuilder


class PageService:
    def __init__(self):
        self.repository = PageRepository()
        self.editorjs_builder = EditorJSBuilder()

    def list_pages(self):
        return self.repository.find_all()

    def get_page_by_id(self, page_id: str):
        return self.repository.find_by_id(page_id)

    def get_published_page_by_slug(self, slug: str):
        return self.repository.find_by_slug(slug)

    def create_page(self, data: dict):
        clean_data = self._clean_page_data(data)

        error = self._validate_page_data(clean_data)
        if error:
            return None, error

        if self.repository.find_any_by_slug(clean_data["slug"]):
            return None, "同じスラッグの固定ページがすでに存在します。"

        page_id = self.repository.create(clean_data)
        return page_id, None

    def update_page(self, page_id: str, data: dict):
        clean_data = self._clean_page_data(data)

        error = self._validate_page_data(clean_data)
        if error:
            return False, error

        existing = self.repository.find_any_by_slug(clean_data["slug"])
        if existing and str(existing["_id"]) != str(page_id):
            return False, "同じスラッグの固定ページがすでに存在します。"

        result = self.repository.update(page_id, clean_data)
        return result, None

    def delete_page(self, page_id: str):
        return self.repository.delete(page_id)

    def _clean_page_data(self, data: dict):
        body_json = self._parse_body_json(data.get("body_json", ""))

        return {
            "title": data.get("title", "").strip(),
            "slug": self._normalize_slug(data.get("slug", "")),
            "body": self.editorjs_builder.build_html(body_json),
            "body_json": body_json,
            "status": data.get("status", "draft"),
            "created_by": data.get("created_by"),
            "updated_by": data.get("updated_by"),
        }

    def _parse_body_json(self, raw):
        if isinstance(raw, dict):
            return raw

        if not raw:
            return {"blocks": []}

        try:
            parsed = json.loads(raw)
        except Exception:
            return {"blocks": []}

        if not isinstance(parsed, dict):
            return {"blocks": []}

        return parsed

    def _validate_page_data(self, data: dict):
        if not data["title"]:
            return "タイトルを入力してください。"

        if not data["slug"]:
            return "スラッグを入力してください。"

        if data["slug"] in RESERVED_SLUGS:
            return "このスラッグは使用できません。"

        if "/" in data["slug"]:
            return "スラッグに / は使えません。"

        if not re.fullmatch(r"[a-z0-9_-]+", data["slug"]):
            return "スラッグ形式が不正です。"

        if data["status"] not in ["draft", "published"]:
            return "公開状態が不正です。"

        return None

    def _normalize_slug(self, slug: str):
        slug = slug.strip().lower()
        slug = re.sub(r"\s+", "-", slug)
        return slug
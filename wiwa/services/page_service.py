# パスとファイル名: wiwa/services/page_service.py

import html
import json
import re

from wiwa.config import RESERVED_SLUGS
from wiwa.db.page_repository import PageRepository


class PageService:
    def __init__(self, db):
        self.repository = PageRepository(db)

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
            "body": self._build_html_from_editorjs(body_json),
            "body_json": body_json,
            "status": data.get("status", "draft"),
            "created_by": data.get("created_by"),
            "updated_by": data.get("updated_by"),
        }

    def _parse_body_json(self, raw_body_json):
        if isinstance(raw_body_json, dict):
            return raw_body_json

        if not raw_body_json:
            return {
                "time": None,
                "blocks": [],
                "version": "",
            }

        try:
            parsed = json.loads(raw_body_json)
        except json.JSONDecodeError:
            return {
                "time": None,
                "blocks": [],
                "version": "",
            }

        if not isinstance(parsed, dict):
            return {
                "time": None,
                "blocks": [],
                "version": "",
            }

        return parsed

    def _build_html_from_editorjs(self, body_json: dict):
        blocks = body_json.get("blocks", [])

        if not isinstance(blocks, list):
            return ""

        html_parts = []

        for block in blocks:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")
            data = block.get("data", {})

            if block_type == "paragraph":
                text = html.escape(data.get("text", ""))
                html_parts.append(f"<p>{text}</p>")

            elif block_type == "header":
                text = html.escape(data.get("text", ""))
                level = int(data.get("level", 2))

                if level < 2 or level > 4:
                    level = 2

                html_parts.append(f"<h{level}>{text}</h{level}>")

            elif block_type == "list":
                items = data.get("items", [])
                style = data.get("style", "unordered")

                tag = "ol" if style == "ordered" else "ul"

                html_parts.append(f"<{tag}>")
                for item in items:
                    html_parts.append(f"<li>{html.escape(str(item))}</li>")
                html_parts.append(f"</{tag}>")

        return "\n".join(html_parts)

    def _validate_page_data(self, data: dict):
        if not data["title"]:
            return "タイトルを入力してください。"

        if not data["slug"]:
            return "スラッグを入力してください。"

        if data["slug"] in RESERVED_SLUGS:
            return "このスラッグは予約されているため使用できません。"

        if "/" in data["slug"]:
            return "スラッグに / は使用できません。"

        if not re.fullmatch(r"[a-z0-9_-]+", data["slug"]):
            return "スラッグには半角英数字、ハイフン、アンダースコアのみ使用できます。"

        if data["status"] not in ["draft", "published"]:
            return "公開状態が不正です。"

        return None

    def _normalize_slug(self, slug: str):
        slug = slug.strip().lower()
        slug = re.sub(r"\s+", "-", slug)
        return slug
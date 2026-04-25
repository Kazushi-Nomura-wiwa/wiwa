# パスとファイル名: wiwa/controllers/page.py

import html
import json

from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response
from wiwa.services.page_service import PageService


renderer = TemplateRenderer()


def _editorjs_to_html(body_json):
    if not body_json:
        return ""

    if isinstance(body_json, dict):
        data = body_json
    else:
        try:
            data = json.loads(body_json)
        except Exception:
            return ""

    html_parts = []

    for block in data.get("blocks", []):
        block_type = block.get("type")
        block_data = block.get("data", {})

        if block_type == "header":
            text = html.escape(block_data.get("text", ""))
            level = int(block_data.get("level", 2))
            level = max(1, min(level, 6))
            html_parts.append(f"<h{level}>{text}</h{level}>")

        elif block_type == "paragraph":
            text = html.escape(block_data.get("text", ""))
            html_parts.append(f"<p>{text}</p>")

        elif block_type == "list":
            items = block_data.get("items", [])
            style = block_data.get("style", "unordered")

            tag = "ol" if style == "ordered" else "ul"
            html_parts.append(f"<{tag}>")

            for item in items:
                if isinstance(item, dict):
                    item_text = item.get("content", "")
                else:
                    item_text = str(item)

                html_parts.append(f"<li>{html.escape(item_text)}</li>")

            html_parts.append(f"</{tag}>")

    return "\n".join(html_parts)


def slug(request, route=None, **params):
    service = PageService()

    page = service.get_page_by_path(request.path)

    if not page:
        return Response(
            body="固定ページが見つかりません。",
            status="404 Not Found"
        )

    page["body_html"] = _editorjs_to_html(page.get("body_json", ""))

    template_name = (route or {}).get("template", "html/page/slug.html")

    body = renderer.render(
        template_name,
        {
            "title": page.get("title", ""),
            "page": page,
        },
        request=request,
    )

    return Response(body=body)
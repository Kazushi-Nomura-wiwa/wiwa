# パスとファイル名: wiwa/services/editorjs_builder.py

import html


class EditorJSBuilder:
    def build_html(self, body_json: dict) -> str:
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
                html_parts.append(self._build_paragraph(data))

            elif block_type == "header":
                html_parts.append(self._build_header(data))

            elif block_type == "list":
                html_parts.append(self._build_list(data))

        return "\n".join(html_parts)

    def _build_paragraph(self, data: dict) -> str:
        text = html.escape(data.get("text", ""))
        return f"<p>{text}</p>"

    def _build_header(self, data: dict) -> str:
        text = html.escape(data.get("text", ""))

        try:
            level = int(data.get("level", 2))
        except Exception:
            level = 2

        if level < 2 or level > 4:
            level = 2

        return f"<h{level}>{text}</h{level}>"

    def _build_list(self, data: dict) -> str:
        items = data.get("items", [])
        style = data.get("style", "unordered")

        tag = "ol" if style == "ordered" else "ul"

        html_parts = [f"<{tag}>"]

        if isinstance(items, list):
            for item in items:
                html_parts.append(f"<li>{html.escape(str(item))}</li>")

        html_parts.append(f"</{tag}>")

        return "\n".join(html_parts)
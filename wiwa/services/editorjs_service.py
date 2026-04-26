# パスとファイル名: wiwa/services/editorjs_service.py

import html
import json


class EditorJSService:
    def build_html(self, body_json) -> str:
        data = self._ensure_dict(body_json)
        blocks = data.get("blocks", [])

        if not isinstance(blocks, list):
            return ""

        html_parts = []

        for block in blocks:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")
            block_data = block.get("data", {})

            if block_type == "header":
                html_parts.append(self._build_header(block_data))

            elif block_type == "paragraph":
                html_parts.append(self._build_paragraph(block_data))

            elif block_type == "list":
                html_parts.append(self._build_list(block_data))

            elif block_type == "table":
                html_parts.append(self._build_table(block_data))

        return "\n".join(html_parts)

    def normalize(self, body_json) -> str:
        data = self._ensure_dict(body_json)
        return json.dumps(data, ensure_ascii=False)

    def empty(self) -> str:
        return json.dumps({"blocks": []}, ensure_ascii=False)

    def _ensure_dict(self, body_json) -> dict:
        if isinstance(body_json, dict):
            return body_json

        if isinstance(body_json, list):
            return {"blocks": body_json}

        if isinstance(body_json, str):
            body_json = body_json.strip()

            if not body_json:
                return {"blocks": []}

            try:
                data = json.loads(body_json)
            except json.JSONDecodeError:
                return {"blocks": []}

            if isinstance(data, dict):
                return data

            if isinstance(data, list):
                return {"blocks": data}

        return {"blocks": []}

    def _build_header(self, data: dict) -> str:
        text = html.escape(data.get("text", ""))

        try:
            level = int(data.get("level", 2))
        except Exception:
            level = 2

        level = max(1, min(level, 6))

        return f"<h{level}>{text}</h{level}>"

    def _build_paragraph(self, data: dict) -> str:
        text = html.escape(data.get("text", ""))
        return f"<p>{text}</p>"

    def _build_list(self, data: dict) -> str:
        items = data.get("items", [])
        style = data.get("style", "unordered")

        tag = "ol" if style == "ordered" else "ul"
        html_parts = [f"<{tag}>"]

        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item_text = item.get("content", "")
                else:
                    item_text = str(item)

                html_parts.append(f"<li>{html.escape(item_text)}</li>")

        html_parts.append(f"</{tag}>")
        return "\n".join(html_parts)

    def _build_table(self, data: dict) -> str:
        rows = data.get("content", [])
        with_headings = data.get("withHeadings", False)

        if not isinstance(rows, list):
            return ""

        html_parts = ["<table>"]

        for row_index, row in enumerate(rows):
            if not isinstance(row, list):
                continue

            html_parts.append("<tr>")

            for cell in row:
                cell_text = html.escape(str(cell))

                if with_headings and row_index == 0:
                    html_parts.append(f"<th>{cell_text}</th>")
                else:
                    html_parts.append(f"<td>{cell_text}</td>")

            html_parts.append("</tr>")

        html_parts.append("</table>")
        return "\n".join(html_parts)
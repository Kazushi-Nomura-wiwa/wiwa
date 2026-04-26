# パスとファイル名: wiwa/services/theme_files_service.py

import mimetypes
from pathlib import Path

from wiwa.config import BASE_DIR
from wiwa.core.request import Request
from wiwa.core.response import Response, not_found


THEME_BASE = BASE_DIR / "themes"


def serve_theme_file(request: Request) -> Response:
    theme_base_dir = THEME_BASE.resolve()

    raw_path = request.path.removeprefix("/themes/").strip("/")

    if not raw_path:
        return not_found()

    file_path = (theme_base_dir / raw_path).resolve()

    # ディレクトリトラバーサル対策
    if not str(file_path).startswith(str(theme_base_dir)):
        return not_found()

    if not file_path.exists() or not file_path.is_file():
        return not_found()

    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    return Response(
        body=file_path.read_bytes(),
        status="200 OK",
        headers=[("Content-Type", content_type)],
    )
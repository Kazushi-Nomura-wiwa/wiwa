# パスとファイル名: wiwa/services/static_files_service.py
import mimetypes
from pathlib import Path

from wiwa.config import ACTIVE_THEME, TEMPLATE_BASE
from wiwa.core.request import Request
from wiwa.core.response import Response, not_found


def get_static_base_dir() -> Path:
    return TEMPLATE_BASE / "static"


def normalize_static_path(static_path: str) -> str | None:
    normalized = static_path.strip("/")

    theme_prefix = f"themes/{ACTIVE_THEME}/"

    if normalized.startswith(theme_prefix):
        return normalized

    if normalized.startswith("themes/"):
        return None

    if normalized.startswith("js/"):
        return normalized

    if normalized.startswith("css/"):
        return normalized

    if normalized.startswith("img/"):
        return normalized

    return f"themes/{ACTIVE_THEME}/{normalized}"


def serve_static(request: Request) -> Response:
    static_base_dir = get_static_base_dir().resolve()
    raw_static_path = request.path.removeprefix("/static/")
    static_path = normalize_static_path(raw_static_path)

    if static_path is None:
        return not_found()

    file_path = (static_base_dir / static_path).resolve()

    if not str(file_path).startswith(str(static_base_dir)):
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
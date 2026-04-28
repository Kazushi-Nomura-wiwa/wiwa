# パスとファイル名: wiwa/services/theme_files_service.py
# Path and filename: wiwa/services/theme_files_service.py

# テーマファイル配信サービス
# Theme files service
#
# 概要
# Summary
#   themesディレクトリ配下のファイルを安全に配信する
#   Serve files under themes directory securely
#
# 処理の流れ
# Flow
#   1. ベースディレクトリ取得
#      Get base directory
#   2. パス抽出
#      Extract request path
#   3. パス検証
#      Validate path
#   4. MIME判定
#      Detect content type
#   5. ファイル返却
#      Return file response

import mimetypes
from pathlib import Path

from wiwa.config import BASE_DIR
from wiwa.core.request import Request
from wiwa.core.response import Response, not_found


# テーマベースディレクトリ
# Theme base directory
THEME_BASE = BASE_DIR / "themes"


# ----------------------------
# 配信処理
# Serving files
# ----------------------------

def serve_theme_file(request: Request) -> Response:
    """
    テーマファイル配信
    Serve theme file
    """
    theme_base_dir = THEME_BASE.resolve()

    # パス抽出
    # Extract path
    raw_path = request.path.removeprefix("/themes/").strip("/")

    if not raw_path:
        return not_found()

    file_path = (theme_base_dir / raw_path).resolve()

    # ディレクトリトラバーサル対策
    # Prevent directory traversal
    if not str(file_path).startswith(str(theme_base_dir)):
        return not_found()

    if not file_path.exists() or not file_path.is_file():
        return not_found()

    # MIMEタイプ判定
    # Detect MIME type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    # ファイル返却
    # Return file response
    return Response(
        body=file_path.read_bytes(),
        status="200 OK",
        headers=[("Content-Type", content_type)],
    )
# パスとファイル名: wiwa/services/static_files_service.py
# Path and filename: wiwa/services/static_files_service.py

# 静的ファイル配信サービス
# Static files service
#
# 概要
# Summary
#   静的ファイルのパス正規化と安全な配信を行う
#   Normalize static paths and serve files securely
#
# 処理の流れ
# Flow
#   1. ベースディレクトリ取得
#      Get base directory
#   2. パス正規化
#      Normalize path
#   3. パス検証
#      Validate path
#   4. MIME判定
#      Detect content type
#   5. ファイル返却
#      Return file response

import mimetypes
from pathlib import Path

from wiwa.config import ACTIVE_THEME, STATIC_BASE
from wiwa.core.request import Request
from wiwa.core.response import Response, not_found


# ----------------------------
# 基本処理
# Basic utilities
# ----------------------------

def get_static_base_dir() -> Path:
    """
    ベースディレクトリ取得
    Get static base directory
    """
    return STATIC_BASE


# ----------------------------
# パス処理
# Path normalization
# ----------------------------

def normalize_static_path(static_path: str) -> str | None:
    """
    パス正規化
    Normalize static path
    """
    normalized = static_path.strip("/")

    theme_prefix = f"themes/{ACTIVE_THEME}/"

    # テーマパスそのまま許可
    # Allow direct access to active theme
    if normalized.startswith(theme_prefix):
        return normalized

    # 他テーマアクセス禁止
    # Block access to other themes
    if normalized.startswith("themes/"):
        return None

    # 直下ディレクトリ許可
    # Allow root-level assets
    if normalized.startswith("js/"):
        return normalized

    if normalized.startswith("css/"):
        return normalized

    if normalized.startswith("img/"):
        return normalized

    # テーマへフォールバック
    # Fallback to active theme
    return f"themes/{ACTIVE_THEME}/{normalized}"


# ----------------------------
# 配信処理
# Serving files
# ----------------------------

def serve_static(request: Request) -> Response:
    """
    静的ファイル配信
    Serve static file
    """
    static_base_dir = get_static_base_dir().resolve()

    raw_static_path = request.path.removeprefix("/static/")
    static_path = normalize_static_path(raw_static_path)

    if static_path is None:
        return not_found()

    file_path = (static_base_dir / static_path).resolve()

    # ディレクトリトラバーサル対策
    # Prevent directory traversal
    if not str(file_path).startswith(str(static_base_dir)):
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
# パスとファイル名: wiwa/controllers/upload.py

# 概要:
# 画像・PDFアップロード処理
# Summary:
# Image and PDF upload handlers

import os
import uuid

import magic

from wiwa.config import (
    UPLOAD_IMG_DIR,
    UPLOAD_IMG_URL_PREFIX,
    UPLOAD_FILE_DIR,
    UPLOAD_FILE_URL_PREFIX,
    MAX_UPLOAD_IMAGE_SIZE,
    MAX_UPLOAD_FILE_SIZE,
)
from wiwa.core.i18n import t
from wiwa.core.response import json_response


# 許可する画像MIMEタイプと拡張子
# Allowed image MIME types and extensions
ALLOWED_IMAGE_MIME_TYPES = {
    "image/apng": "apng",
    "image/avif": "avif",
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/tiff": "tiff",
    "image/webp": "webp",
}


# 許可するファイルMIMEタイプと拡張子
# Allowed file MIME types and extensions
ALLOWED_FILE_MIME_TYPES = {
    "application/pdf": "pdf",
}


# 現在のユーザーを検証する
# Validate current user
def _validate_user(request):
    current_user = getattr(request, "user", None)

    # ログインチェック
    # Authentication check
    if not current_user:
        return json_response({
            "success": 0,
            "message": t("upload.login_required"),
        }, status="401 Unauthorized")

    # role取得（正規化）
    # Normalize role value
    role = (current_user.get("role") or "").strip().lower()

    # 権限チェック
    # Authorization check
    if role not in ("admin", "author"):
        return json_response({
            "success": 0,
            "message": t("upload.permission_denied"),
        }, status="403 Forbidden")

    return None


# アップロードファイルを取得する
# Get uploaded file
def _get_uploaded_file(request):
    files = getattr(request, "files", {})

    uploaded_file = files.get("file")

    if uploaded_file is None:
        uploaded_file = files.get("image")

    if uploaded_file is None:
        return None, json_response({
            "success": 0,
            "message": t("upload.file_not_found"),
        }, status="400 Bad Request")

    return uploaded_file, None

# ファイルを保存する
# Save uploaded file
def _save_upload(file_bytes, upload_dir, url_prefix, ext):
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(upload_dir, filename)

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    file_url = f"{url_prefix}/{filename}"

    return file_url


# 画像アップロード処理
# Image upload handler
def image(request, **kwargs):
    user_error = _validate_user(request)

    if user_error:
        return user_error

    uploaded_file, file_error = _get_uploaded_file(request)

    if file_error:
        return file_error

    file_bytes = uploaded_file.file.read()

    # サイズチェック
    # File size validation
    if len(file_bytes) > MAX_UPLOAD_IMAGE_SIZE:
        return json_response({
            "success": 0,
            "message": t("upload.image_too_large"),
        }, status="400 Bad Request")

    # MIMEタイプ判定
    # Detect MIME type
    mime_type = magic.from_buffer(file_bytes, mime=True)

    # 画像形式チェック
    # Image type validation
    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        return json_response({
            "success": 0,
            "message": t("upload.invalid_image_type"),
        }, status="400 Bad Request")

    ext = ALLOWED_IMAGE_MIME_TYPES[mime_type]

    file_url = _save_upload(
        file_bytes=file_bytes,
        upload_dir=UPLOAD_IMG_DIR,
        url_prefix=UPLOAD_IMG_URL_PREFIX,
        ext=ext,
    )

    # Editor.js形式で返却
    # Return response for Editor.js
    return json_response({
        "success": 1,
        "file": {
            "url": file_url,
        },
    })


# PDFアップロード処理
# PDF upload handler
def file(request, **kwargs):
    user_error = _validate_user(request)

    if user_error:
        return user_error

    uploaded_file, file_error = _get_uploaded_file(request)

    if file_error:
        return file_error

    file_bytes = uploaded_file.file.read()

    # サイズチェック
    # File size validation
    if len(file_bytes) > MAX_UPLOAD_FILE_SIZE:
        return json_response({
            "success": 0,
            "message": t("upload.file_too_large"),
        }, status="400 Bad Request")

    # MIMEタイプ判定
    # Detect MIME type
    mime_type = magic.from_buffer(file_bytes, mime=True)

    # ファイル形式チェック
    # File type validation
    if mime_type not in ALLOWED_FILE_MIME_TYPES:
        return json_response({
            "success": 0,
            "message": t("upload.invalid_file_type"),
        }, status="400 Bad Request")

    ext = ALLOWED_FILE_MIME_TYPES[mime_type]

    file_url = _save_upload(
        file_bytes=file_bytes,
        upload_dir=UPLOAD_FILE_DIR,
        url_prefix=UPLOAD_FILE_URL_PREFIX,
        ext=ext,
    )

    return json_response({
        "success": 1,
        "file": {
            "url": file_url,
        },
    })
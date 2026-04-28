# パスとファイル名: wiwa/services/post_form_service.py
# Path and filename: wiwa/services/post_form_service.py

# 投稿フォームサービス
# Post form service
#
# 概要
# Summary
#   投稿フォームの生成・変換・検証を行う
#   Handle post form generation, transformation, and validation
#
# 処理の流れ
# Flow
#   1. ユーザー情報取得
#      Get current user info
#   2. タグ分割
#      Split tags
#   3. フォーム生成
#      Build form data
#   4. 入力変換
#      Convert submitted data
#   5. バリデーション
#      Validate form

from wiwa.core.i18n import t


def current_user_info(request) -> tuple[str, str]:
    """
    ユーザー情報取得
    Get current user info
    """
    current_user = request.user or {}
    user_id = str(current_user.get("_id", "") or "")
    username = current_user.get("username", "") or ""
    return user_id, username


def split_tags(raw_tags: str) -> list[str]:
    """
    タグ分割
    Split tags by space
    """
    return (raw_tags or "").replace("　", " ").split()


def empty_post_form(status: str = "published") -> dict:
    """
    空フォーム生成
    Build empty form
    """
    return {
        "_id": "",
        "title": "",
        "body": "",
        "tags": "",
        "status": status,
    }


def post_to_form(post: dict) -> dict:
    """
    投稿→フォーム変換
    Convert post to form
    """
    return {
        "_id": str(post.get("_id", "")),
        "title": post.get("title", ""),
        "body": post.get("body", ""),
        "tags": " ".join(post.get("tags", [])),
        "status": post.get("status", "published"),
    }


def submitted_post_form(request) -> dict:
    """
    送信データ取得
    Extract submitted form
    """
    return {
        "_id": "",
        "title": request.get_form("title").strip(),
        "body": request.get_form("body").strip(),
        "tags": request.get_form("tags").strip(),
        "status": request.get_form("status", "published").strip() or "published",
    }


def validate_post_form(form: dict) -> str:
    """
    フォーム検証
    Validate form
    """
    if not form.get("title"):
        return t("error.post.title_required")

    if not form.get("body"):
        return t("error.post.body_required")

    return ""
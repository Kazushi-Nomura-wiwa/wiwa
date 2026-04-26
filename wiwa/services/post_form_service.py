# パスとファイル名: wiwa/services/post_form_service.py

def current_user_info(request) -> tuple[str, str]:
    current_user = request.user or {}
    user_id = str(current_user.get("_id", "") or "")
    username = current_user.get("username", "") or ""
    return user_id, username


def split_tags(raw_tags: str) -> list[str]:
    return (raw_tags or "").replace("　", " ").split()


def empty_post_form(status: str = "published") -> dict:
    return {
        "_id": "",
        "title": "",
        "body": "",
        "tags": "",
        "status": status,
    }


def post_to_form(post: dict) -> dict:
    return {
        "_id": str(post.get("_id", "")),
        "title": post.get("title", ""),
        "body": post.get("body", ""),
        "tags": " ".join(post.get("tags", [])),
        "status": post.get("status", "published"),
    }


def submitted_post_form(request) -> dict:
    return {
        "_id": "",
        "title": request.get_form("title").strip(),
        "body": request.get_form("body").strip(),
        "tags": request.get_form("tags").strip(),
        "status": request.get_form("status", "published").strip() or "published",
    }


def validate_post_form(form: dict) -> str:
    if not form.get("title"):
        return "title は必須です。"

    if not form.get("body"):
        return "body は必須です。"

    return ""
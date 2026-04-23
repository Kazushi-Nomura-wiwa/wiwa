# パスとファイル名: wiwa/controllers/admin/users.py
from bson import ObjectId
from urllib.parse import quote

from wiwa.core.password import hash_password
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.db.users_repository import UsersRepository


renderer = TemplateRenderer()
users_repo = UsersRepository()

ALLOWED_ROLES = {"admin", "editor", "author"}


def _redirect_with_error(message: str):
    return redirect("/admin/users?error=" + quote(message))


def _to_object_id(user_id: str):
    try:
        return ObjectId(user_id)
    except Exception:
        return None


def _is_last_active_admin(user: dict) -> bool:
    current_role = (user.get("role") or "").strip()
    is_active = bool(user.get("is_active", True))

    if current_role != "admin" or not is_active:
        return False

    admin_count = users_repo.count_active_admins()
    return admin_count <= 1


def list(request, route=None, **params):
    error_message = request.get_query("error", "")
    templates_name = (route or {}).get("template", "html/admin/users/list.html")
    body = renderer.render(
        templates_name,
        {
            "title": "Users",
            "users": users_repo.list_users(),
            "error_message": error_message,
        },
        request=request,
    )
    return Response(body=body)


def new(request, route=None, **params):
    error_message = ""
    form_data = {
        "username": "",
        "email": "",
        "role": "author",
        "display_name": "",
    }

    if request.method == "POST":
        username = request.get_form("username").strip()
        email = request.get_form("email").strip()
        password = request.get_form("password").strip()
        role = request.get_form("role").strip() or "author"
        display_name = request.get_form("display_name").strip()

        form_data = {
            "username": username,
            "email": email,
            "role": role,
            "display_name": display_name,
        }

        try:
            if not username:
                raise ValueError("username が空です。")
            if not email:
                raise ValueError("email が空です。")
            if not password:
                raise ValueError("password が空です。")
            if role not in ALLOWED_ROLES:
                raise ValueError(f"許可されていない role です: {role}")

            password_hash = hash_password(password)

            users_repo.create(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                display_name=display_name or username,
                is_active=True,
            )

            return redirect("/admin/users/list")

        except ValueError as e:
            error_message = str(e)
    html_template = (route or {}).get("template", "html/admin/users/new.html")  
    body = renderer.render(
        html_template,
        {
            "title": "ユーザー追加",
            "error_message": error_message,
            "form_data": form_data,
        },
        request=request,
    )
    return Response(body=body)


def edit(request, route=None, **params):
    user_id = (params.get("id") or "").strip()
    if not user_id:
        return _redirect_with_error("user_id が空です。")

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error("user_id が不正です。")

    user = users_repo.find_by_id(object_id)
    if not user:
        return _redirect_with_error("対象ユーザーが存在しません。")

    html_template = (route or {}).get("template", "html/admin/users/edit.html") 
    body = renderer.render(
        html_template,
        {
            "title": "ユーザー編集",
            "user": user,
            "allowed_roles": sorted(ALLOWED_ROLES),
            "is_last_active_admin": _is_last_active_admin(user),
        },
        request=request,
    )
    return Response(body=body)


def update(request, route=None, **params):
    user_id = request.get_form("user_id").strip()
    username = request.get_form("username").strip()
    email = request.get_form("email").strip()
    display_name = request.get_form("display_name").strip()
    role = request.get_form("role").strip()
    is_active = request.get_form("is_active").strip() == "1"

    if not user_id:
        return _redirect_with_error("user_id が空です。")

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error("user_id が不正です。")

    target_user = users_repo.find_by_id(object_id)
    if not target_user:
        return _redirect_with_error("対象ユーザーが存在しません。")

    if not username:
        return _redirect_with_error("username が空です。")

    if not email:
        return _redirect_with_error("email が空です。")

    if role not in ALLOWED_ROLES:
        return _redirect_with_error("許可されていない role です。")

    if _is_last_active_admin(target_user):
        if role != "admin":
            return _redirect_with_error("最後の admin の role は変更できません。")

        if not is_active:
            return _redirect_with_error("最後の admin は無効化できません。")

    users_repo.update_user(
        user_id=object_id,
        username=username,
        email=email,
        display_name=display_name or username,
        role=role,
        is_active=is_active,
    )

    return redirect("/admin/users/list")


def delete(request, route=None, **params):
    user_id = request.get_form("user_id").strip()

    if not user_id:
        return _redirect_with_error("user_id が空です。")

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error("user_id が不正です。")

    target_user = users_repo.find_by_id(object_id)
    if not target_user:
        return _redirect_with_error("対象ユーザーが存在しません。")

    if _is_last_active_admin(target_user):
        return _redirect_with_error("最後の admin は削除できません。")

    users_repo.delete_user(object_id)

    return redirect("/admin/users/list")
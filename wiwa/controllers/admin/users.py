# パスとファイル名: wiwa/controllers/admin/users.py
# Path and filename: wiwa/controllers/admin/users.py

# ユーザー管理コントローラ
# Admin user management controller
#
# URL
# URL
#   /admin/users/list
#   /admin/users/new
#   /admin/users/edit/<id>
#   /admin/users/update
#   /admin/users/delete
#
# 処理の流れ（一覧）
# Flow (list)
#   1. ユーザー一覧取得
#      Fetch users
#   2. テンプレート描画
#      Render template
#
# 処理の流れ（作成）
# Flow (create)
#   1. フォーム初期化
#      Initialize form
#   2. POST時は入力取得
#      Get submitted form
#   3. 入力検証
#      Validate input
#   4. ユーザー作成
#      Create user
#
# 処理の流れ（編集）
# Flow (edit)
#   1. ID検証
#      Validate ID
#   2. ユーザー取得
#      Fetch user
#   3. テンプレート描画
#      Render template
#
# 処理の流れ（更新）
# Flow (update)
#   1. 入力取得
#      Get submitted form
#   2. 入力検証
#      Validate input
#   3. admin保護チェック
#      Protect last admin
#   4. ユーザー更新
#      Update user
#
# 処理の流れ（削除）
# Flow (delete)
#   1. ID検証
#      Validate ID
#   2. admin保護チェック
#      Protect last admin
#   3. ユーザー削除
#      Delete user

from urllib.parse import quote

from bson import ObjectId

from wiwa.core.i18n import t
from wiwa.core.password import hash_password
from wiwa.core.renderer import TemplateRenderer
from wiwa.core.response import Response, redirect
from wiwa.db.users_repository import UsersRepository


# テンプレートレンダラー
# Template renderer
renderer = TemplateRenderer()

# ユーザーリポジトリ
# User repository
users_repo = UsersRepository()


# 許可するユーザー権限
# Allowed user roles
ALLOWED_ROLES = {"admin", "editor", "author"}


def _redirect_with_error(message: str):
    """
    エラーメッセージ付きでユーザー一覧へ戻す
    Redirect to user list with error message
    """
    return redirect("/admin/users/list?error=" + quote(message))


def _to_object_id(user_id: str):
    """
    文字列をObjectIdへ変換する
    Convert string to ObjectId
    """
    try:
        return ObjectId(user_id)
    except Exception:
        return None


def _is_last_active_admin(user: dict) -> bool:
    """
    対象ユーザーが最後の有効なadminか判定する
    Check if the user is the last active admin
    """

    current_role = (user.get("role") or "").strip()
    is_active = bool(user.get("is_active", True))

    if current_role != "admin" or not is_active:
        return False

    admin_count = users_repo.count_active_admins()
    return admin_count <= 1


def list(request, route=None, **params):
    """
    ユーザー一覧を表示する
    Render user list
    """

    # クエリからエラーメッセージを取得
    # Get error message from query string
    error_message = request.get_query("error", "")

    body = renderer.render_route(
        route,
        "html/admin/users/list.html",
        {
            "title": t("admin_users_title"),
            "users": users_repo.list_users(),
            "error_message": error_message,
        },
        request=request,
    )

    return Response(body=body)


def new(request, route=None, **params):
    """
    ユーザー作成画面および作成処理
    Render new user form and create user
    """

    error_message = ""

    # 初期フォームデータ
    # Initial form data
    form_data = {
        "username": "",
        "email": "",
        "role": "author",
        "display_name": "",
    }

    # POST時はユーザー作成
    # On POST, create user
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
                raise ValueError(t("error_username_empty"))
            if not email:
                raise ValueError(t("error_email_empty"))
            if not password:
                raise ValueError(t("error_password_empty"))
            if role not in ALLOWED_ROLES:
                raise ValueError(t("error_role_not_allowed").format(role=role))

            # パスワードをハッシュ化
            # Hash password
            password_hash = hash_password(password)

            # ユーザー作成
            # Create user
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

    body = renderer.render_route(
        route,
        "html/admin/users/new.html",
        {
            "title": t("admin_user_new_title"),
            "error_message": error_message,
            "form_data": form_data,
        },
        request=request,
    )

    return Response(body=body)


def edit(request, route=None, **params):
    """
    ユーザー編集画面を表示する
    Render user edit form
    """

    user_id = (params.get("id") or "").strip()
    if not user_id:
        return _redirect_with_error(t("error_user_id_empty"))

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error(t("error_user_id_invalid"))

    user = users_repo.find_by_id(object_id)
    if not user:
        return _redirect_with_error(t("error_user_not_found"))

    body = renderer.render_route(
        route,
        "html/admin/users/edit.html",
        {
            "title": t("admin_user_edit_title"),
            "user": user,
            "allowed_roles": sorted(ALLOWED_ROLES),
            "is_last_active_admin": _is_last_active_admin(user),
        },
        request=request,
    )

    return Response(body=body)


def update(request, route=None, **params):
    """
    ユーザー更新処理
    Update user
    """

    user_id = request.get_form("user_id").strip()
    username = request.get_form("username").strip()
    email = request.get_form("email").strip()
    display_name = request.get_form("display_name").strip()
    role = request.get_form("role").strip()
    is_active = request.get_form("is_active").strip() == "1"

    if not user_id:
        return _redirect_with_error(t("error_user_id_empty"))

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error(t("error_user_id_invalid"))

    target_user = users_repo.find_by_id(object_id)
    if not target_user:
        return _redirect_with_error(t("error_user_not_found"))

    if not username:
        return _redirect_with_error(t("error_username_empty"))

    if not email:
        return _redirect_with_error(t("error_email_empty"))

    if role not in ALLOWED_ROLES:
        return _redirect_with_error(t("error_role_not_allowed_simple"))

    # 最後のadminを保護
    # Protect the last active admin
    if _is_last_active_admin(target_user):
        if role != "admin":
            return _redirect_with_error(t("error_last_admin_role"))

        if not is_active:
            return _redirect_with_error(t("error_last_admin_disable"))

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
    """
    ユーザー削除処理
    Delete user
    """

    user_id = request.get_form("user_id").strip()

    if not user_id:
        return _redirect_with_error(t("error_user_id_empty"))

    object_id = _to_object_id(user_id)
    if not object_id:
        return _redirect_with_error(t("error_user_id_invalid"))

    target_user = users_repo.find_by_id(object_id)
    if not target_user:
        return _redirect_with_error(t("error_user_not_found"))

    # 最後のadminは削除不可
    # Do not delete the last active admin
    if _is_last_active_admin(target_user):
        return _redirect_with_error(t("error_last_admin_delete"))

    users_repo.delete_user(object_id)

    return redirect("/admin/users/list")
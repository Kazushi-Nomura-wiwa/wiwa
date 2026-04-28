# パスとファイル名: wiwa/db/users_repository.py
# Path and filename: wiwa/db/users_repository.py

# ユーザーリポジトリ
# User repository
#
# 概要
# Summary
#   ユーザーの作成・取得・更新・削除および認証関連情報を管理する
#   Manage user CRUD operations and authentication-related fields
#
# 処理の流れ
# Flow
#   1. ユーザー作成
#      Create user
#   2. ユーザー取得
#      Fetch user
#   3. ユーザー更新
#      Update user
#   4. ユーザー削除
#      Delete user

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId

from wiwa.db.mongo import get_collection
from wiwa.core.i18n import t


class UsersRepository:
    def __init__(self):
        """
        リポジトリ初期化
        Initialize repository
        """
        self.collection = get_collection("users")

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "author",
        display_name: str | None = None,
        is_active: bool = True,
    ) -> Any:
        """
        ユーザー作成
        Create user
        """
        username = (username or "").strip()
        email = (email or "").strip().lower()
        password_hash = (password_hash or "").strip()
        role = (role or "author").strip()
        display_name = (display_name or username).strip()

        if not username:
            raise ValueError(t("error.user.username_required"))
        if not email:
            raise ValueError(t("error.user.email_required"))
        if not password_hash:
            raise ValueError(t("error.user.password_required"))

        now = datetime.now(UTC)

        # username重複チェック
        # Check duplicate username
        existing_user = self.find_by_username(username)
        if existing_user:
            raise ValueError(t("error.user.username_exists"))

        # email重複チェック
        # Check duplicate email
        existing_email = self.find_by_email(email)
        if existing_email:
            raise ValueError(t("error.user.email_exists"))

        result = self.collection.insert_one({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
            "role": role,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
            "last_login_at": None,
            "password_changed_at": now,
        })

        return result.inserted_id

    def find_by_id(self, user_id: Any):
        """
        IDでユーザー取得
        Find user by ID
        """
        if not user_id:
            return None

        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except Exception:
                return None

        return self.collection.find_one({"_id": user_id})

    def find_by_username(self, username: str):
        """
        usernameでユーザー取得
        Find user by username
        """
        username = (username or "").strip()
        if not username:
            return None

        return self.collection.find_one({"username": username})

    def find_by_email(self, email: str):
        """
        emailでユーザー取得
        Find user by email
        """
        email = (email or "").strip().lower()
        if not email:
            return None

        return self.collection.find_one({"email": email})

    def find_display_names_by_ids(self, user_ids: list[str]) -> dict[str, str]:
        """
        display_name一括取得
        Fetch display names by user IDs
        """
        object_ids: list[ObjectId] = []

        for user_id in user_ids:
            if not user_id:
                continue
            try:
                object_ids.append(ObjectId(user_id))
            except Exception:
                continue

        if not object_ids:
            return {}

        users = self.collection.find(
            {"_id": {"$in": object_ids}},
            {"display_name": 1, "username": 1},
        )

        result: dict[str, str] = {}
        for user in users:
            key = str(user.get("_id"))
            result[key] = user.get("display_name") or user.get("username") or ""

        return result

    def update_last_login(self, user_id: Any) -> None:
        """
        最終ログイン更新
        Update last login
        """
        now = datetime.now(UTC)
        self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "last_login_at": now,
                    "updated_at": now,
                }
            },
        )

    def update_password(self, user_id: Any, password_hash: str) -> None:
        """
        パスワード更新
        Update password
        """
        now = datetime.now(UTC)
        self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "password_hash": password_hash,
                    "password_changed_at": now,
                    "updated_at": now,
                }
            },
        )

    def update_role(self, user_id: Any, role: str) -> None:
        """
        ロール更新
        Update role
        """
        role = (role or "").strip()
        if not role:
            raise ValueError(t("error.user.role_required"))

        now = datetime.now(UTC)
        self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "role": role,
                    "updated_at": now,
                }
            },
        )

    def set_active(self, user_id: Any, is_active: bool) -> None:
        """
        有効状態更新
        Set active flag
        """
        now = datetime.now(UTC)
        self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "is_active": bool(is_active),
                    "updated_at": now,
                }
            },
        )

    def update_user(
        self,
        user_id: Any,
        username: str,
        email: str,
        display_name: str,
        role: str,
        is_active: bool,
    ) -> None:
        """
        ユーザー更新
        Update user
        """
        user = self.find_by_id(user_id)
        if not user:
            raise ValueError(t("error.user.not_found"))

        username = (username or "").strip()
        email = (email or "").strip().lower()
        display_name = (display_name or username).strip()
        role = (role or "").strip()

        if not username:
            raise ValueError(t("error.user.username_required"))
        if not email:
            raise ValueError(t("error.user.email_required"))
        if not role:
            raise ValueError(t("error.user.role_required"))

        existing_user = self.find_by_username(username)
        if existing_user and existing_user["_id"] != user["_id"]:
            raise ValueError(t("error.user.username_exists"))

        existing_email = self.find_by_email(email)
        if existing_email and existing_email["_id"] != user["_id"]:
            raise ValueError(t("error.user.email_exists"))

        now = datetime.now(UTC)

        self.collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "username": username,
                    "email": email,
                    "display_name": display_name,
                    "role": role,
                    "is_active": bool(is_active),
                    "updated_at": now,
                }
            },
        )

    def delete_user(self, user_id: Any) -> None:
        """
        ユーザー削除
        Delete user
        """
        user = self.find_by_id(user_id)
        if not user:
            raise ValueError(t("error.user.not_found"))

        self.collection.delete_one({"_id": user["_id"]})

    def list_users(self) -> list[dict]:
        """
        ユーザー一覧
        List users
        """
        return list(
            self.collection.find().sort("created_at", 1)
        )

    def count_active_admins(self) -> int:
        """
        有効なadmin数
        Count active admins
        """
        return self.collection.count_documents({
            "role": "admin",
            "is_active": True,
        })
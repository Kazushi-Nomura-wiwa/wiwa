# パスとファイル名: wiwa/services/login_service.py
# Path and filename: wiwa/services/login_service.py

# ログインサービス
# Login service
#
# 概要
# Summary
#   ユーザー認証を行い、セッションを発行する
#   Authenticate user and issue session
#
# 処理の流れ
# Flow
#   1. 入力検証
#      Validate input
#   2. ユーザー取得
#      Fetch user
#   3. 有効状態チェック
#      Check active status
#   4. パスワード検証
#      Verify password
#   5. セッション生成
#      Create session

from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository
from wiwa.core.i18n import t


@dataclass
class LoginResult:
    ok: bool
    message: str = ""
    session_id: str = ""


class LoginService:
    def __init__(self):
        """
        サービス初期化
        Initialize service
        """
        self.users_repository = UsersRepository()
        self.sessions_repository = SessionsRepository()
        self.password_hasher = PasswordHasher()

    def login(self, username: str, password: str) -> LoginResult:
        """
        ログイン処理
        Login process
        """
        username = (username or "").strip()
        password = password or ""

        # 入力検証
        # Validate input
        if not username or not password:
            return LoginResult(
                ok=False,
                message=t("error.login.required"),
            )

        # ユーザー取得
        # Fetch user
        user = self.users_repository.find_by_username(username)
        if not user:
            return LoginResult(
                ok=False,
                message=t("error.login.invalid"),
            )

        # 有効状態チェック
        # Check active status
        if not user.get("is_active", True):
            return LoginResult(
                ok=False,
                message=t("error.login.inactive"),
            )

        # パスワード取得
        # Get password hash
        password_hash = user.get("password_hash", "") or ""
        if not password_hash:
            return LoginResult(
                ok=False,
                message=t("error.login.invalid"),
            )

        # パスワード検証
        # Verify password
        try:
            self.password_hasher.verify(password_hash, password)
        except (VerifyMismatchError, InvalidHash):
            return LoginResult(
                ok=False,
                message=t("error.login.invalid"),
            )

        # セッション生成
        # Create session
        session_id = self.sessions_repository.create(username=username)

        return LoginResult(
            ok=True,
            session_id=session_id,
        )

    def logout(self, session_id: str) -> None:
        """
        ログアウト処理
        Logout process
        """
        if not session_id:
            return

        self.sessions_repository.delete(session_id)
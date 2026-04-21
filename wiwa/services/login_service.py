# パスとファイル名: wiwa/services/login_service.py
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository


@dataclass
class LoginResult:
    ok: bool
    message: str = ""
    session_id: str = ""


class LoginService:
    def __init__(self):
        self.users_repository = UsersRepository()
        self.sessions_repository = SessionsRepository()
        self.password_hasher = PasswordHasher()

    def login(self, username: str, password: str) -> LoginResult:
        username = (username or "").strip()
        password = password or ""

        if not username or not password:
            return LoginResult(
                ok=False,
                message="ユーザー名とパスワードは必須です。",
            )

        user = self.users_repository.find_by_username(username)
        if not user:
            return LoginResult(
                ok=False,
                message="ユーザー名またはパスワードが違います。",
            )

        if not user.get("is_active", True):
            return LoginResult(
                ok=False,
                message="このアカウントは無効です。",
            )

        password_hash = user.get("password_hash", "") or ""
        if not password_hash:
            return LoginResult(
                ok=False,
                message="ユーザー名またはパスワードが違います。",
            )

        try:
            self.password_hasher.verify(password_hash, password)
        except (VerifyMismatchError, InvalidHash):
            return LoginResult(
                ok=False,
                message="ユーザー名またはパスワードが違います。",
            )

        session_id = self.sessions_repository.create(username=username)

        return LoginResult(
            ok=True,
            session_id=session_id,
        )

    def logout(self, session_id: str) -> None:
        if not session_id:
            return

        self.sessions_repository.delete(session_id)
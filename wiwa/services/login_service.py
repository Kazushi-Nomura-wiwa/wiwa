# パスとファイル名: wiwa/services/login_service.py
from dataclasses import dataclass

from wiwa.core.password import hash_password, needs_rehash, verify_password
from wiwa.db.sessions_repository import SessionsRepository
from wiwa.db.users_repository import UsersRepository


@dataclass
class LoginResult:
    ok: bool
    message: str = ""
    user: dict | None = None
    session_id: str | None = None


class LoginService:
    def __init__(self):
        self.users_repo = UsersRepository()
        self.sessions_repo = SessionsRepository()

    def login(self, username: str, password: str) -> LoginResult:
        username = (username or "").strip()
        password = password or ""

        if not username:
            return LoginResult(ok=False, message="ユーザー名を入力してください。")

        if not password:
            return LoginResult(ok=False, message="パスワードを入力してください。")

        user = self.users_repo.find_by_username(username)
        if not user:
            return LoginResult(ok=False, message="ユーザー名またはパスワードが違います。")

        if not user.get("is_active", True):
            return LoginResult(ok=False, message="このユーザーは無効化されています。")

        stored_hash = user.get("password_hash", "")
        if not verify_password(password, stored_hash):
            return LoginResult(ok=False, message="ユーザー名またはパスワードが違います。")

        if needs_rehash(stored_hash):
            new_password_hash = hash_password(password)
            self.users_repo.update_password(user["_id"], new_password_hash)
            user["password_hash"] = new_password_hash

        session_id = self.sessions_repo.create(username=username)
        self.users_repo.update_last_login(user["_id"])

        return LoginResult(
            ok=True,
            message="ログインに成功しました。",
            user=user,
            session_id=session_id,
        )

    def logout(self, session_id: str) -> None:
        if not session_id:
            return

        self.sessions_repo.delete(session_id)
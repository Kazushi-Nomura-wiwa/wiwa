# パスとファイル名: wiwa/core/password.py
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    password = (password or "").strip()
    if not password:
        raise ValueError("パスワードが空です。")

    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    password = password or ""
    password_hash = password_hash or ""

    if not password or not password_hash:
        return False

    return check_password_hash(password_hash, password)
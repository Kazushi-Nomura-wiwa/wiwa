# パスとファイル名: wiwa/core/password.py
from __future__ import annotations

import hashlib
import hmac
import os

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from werkzeug.security import check_password_hash


_password_hasher = PasswordHasher()
_password_pepper = os.getenv("WIWA_PASSWORD_PEPPER", "")


def _apply_pepper(password: str) -> str:
    if not _password_pepper:
        return password

    return hmac.new(
        _password_pepper.encode("utf-8"),
        password.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_password(password: str) -> str:
    password = password or ""
    if not password:
        raise ValueError("password が空です。")

    peppered_password = _apply_pepper(password)
    return _password_hasher.hash(peppered_password)


def verify_password(password: str, stored_hash: str) -> bool:
    password = password or ""
    stored_hash = (stored_hash or "").strip()

    if not password or not stored_hash:
        return False

    peppered_password = _apply_pepper(password)

    if stored_hash.startswith("$argon2"):
        try:
            return _password_hasher.verify(stored_hash, peppered_password)
        except (VerifyMismatchError, InvalidHashError):
            return False

    if stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"):
        return check_password_hash(stored_hash, peppered_password)

    return False


def needs_rehash(stored_hash: str) -> bool:
    stored_hash = (stored_hash or "").strip()

    if not stored_hash:
        return True

    if not stored_hash.startswith("$argon2"):
        return True

    try:
        return _password_hasher.check_needs_rehash(stored_hash)
    except InvalidHashError:
        return True
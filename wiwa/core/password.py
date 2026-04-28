# パスとファイル名: wiwa/core/password.py
# Path and filename: wiwa/core/password.py

# パスワード処理ユーティリティ
# Password handling utilities
#
# 概要
# Summary
#   パスワードのハッシュ化・検証・再ハッシュ判定を行う
#   Handle password hashing, verification, and rehash checks
#
# 処理の流れ
# Flow
#   1. pepper適用
#      Apply pepper
#   2. ハッシュ生成
#      Generate hash
#   3. ハッシュ検証
#      Verify hash
#   4. 再ハッシュ判定
#      Check rehash necessity

from __future__ import annotations

import hashlib
import hmac
import os

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from werkzeug.security import check_password_hash

from wiwa.core.i18n import t


_password_hasher = PasswordHasher()
_password_pepper = os.getenv("WIWA_PASSWORD_PEPPER", "")


def _apply_pepper(password: str) -> str:
    """
    パスワードにpepperを適用
    Apply pepper to password
    """
    if not _password_pepper:
        return password

    return hmac.new(
        _password_pepper.encode("utf-8"),
        password.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_password(password: str) -> str:
    """
    パスワードをハッシュ化
    Hash password
    """
    password = password or ""
    if not password:
        raise ValueError(t("error.password.empty"))

    peppered_password = _apply_pepper(password)
    return _password_hasher.hash(peppered_password)


def verify_password(password: str, stored_hash: str) -> bool:
    """
    パスワードと保存済みハッシュを検証
    Verify password against stored hash
    """
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
    """
    保存済みハッシュの再ハッシュが必要か判定
    Check whether stored hash needs rehash
    """
    stored_hash = (stored_hash or "").strip()

    if not stored_hash:
        return True

    if not stored_hash.startswith("$argon2"):
        return True

    try:
        return _password_hasher.check_needs_rehash(stored_hash)
    except InvalidHashError:
        return True
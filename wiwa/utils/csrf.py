# パスとファイル名: wiwa/utils/csrf.py
# Path and filename: wiwa/utils/csrf.py

# CSRFトークンユーティリティ
# CSRF token utilities
#
# 概要
# Summary
#   セッションに保存されたCSRFトークンを取得し、フォーム送信時に検証する
#   Retrieve CSRF token from session and validate form submission
#
# 処理の流れ
# Flow
#   1. トークン取得
#      Get token
#   2. フォームトークン取得
#      Get form token
#   3. 存在チェック
#      Check presence
#   4. 安全比較
#      Secure comparison

from hmac import compare_digest


# ----------------------------
# トークン取得
# Token retrieval
# ----------------------------

def get_csrf_token(request) -> str:
    """
    CSRFトークン取得
    Get CSRF token from session
    """
    user = request.user or {}
    return user.get("csrf_token", "") or ""


# ----------------------------
# 検証処理
# Validation
# ----------------------------

def validate_csrf(request) -> bool:
    """
    CSRF検証
    Validate CSRF token
    """
    session_token = get_csrf_token(request)
    form_token = request.get_form("csrf_token")

    # 存在チェック
    # Check presence
    if not session_token or not form_token:
        return False

    # タイミング攻撃対策比較
    # Constant-time comparison
    return compare_digest(session_token, form_token)
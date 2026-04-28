# パスとファイル名: wiwa/utils/localtime.py
# Path and filename: wiwa/utils/localtime.py

# ローカル時刻変換ユーティリティ
# Local time conversion utilities
#
# 概要
# Summary
#   UTC時刻を設定されたタイムゾーンへ変換し、表示用フォーマットを提供する
#   Convert UTC datetime to configured timezone and provide formatted output
#
# 処理の流れ
# Flow
#   1. 値チェック
#      Check value
#   2. タイムゾーン補正
#      Normalize timezone
#   3. ローカル変換
#      Convert to local time
#   4. 文字列化
#      Format to string

from datetime import UTC

from wiwa.config import TIMEZONE


# ----------------------------
# 時刻変換
# Time conversion
# ----------------------------

def to_localtime(value):
    """
    ローカル時刻変換
    Convert to local timezone
    """
    if not value:
        return None

    # タイムゾーン未設定対策
    # Normalize naive datetime
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)

    # ローカルタイムへ変換
    # Convert to configured timezone
    return value.astimezone(TIMEZONE)


# ----------------------------
# 文字列変換
# String formatting
# ----------------------------

def to_localtime_string(value, fmt="%Y-%m-%d %H:%M:%S"):
    """
    ローカル時刻文字列化
    Convert datetime to formatted string
    """
    local = to_localtime(value)

    if not local:
        return ""

    return local.strftime(fmt)
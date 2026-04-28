# パスとファイル名: wiwa/utils/slug.py
# Path and filename: wiwa/utils/slug.py

# スラッグ正規化ユーティリティ
# Slug normalization utilities
#
# 概要
# Summary
#   入力文字列をURLスラッグとして安全かつ一貫した形式に正規化する
#   Normalize input string into safe and consistent URL slug
#
# 処理の流れ
# Flow
#   1. デコード
#      Decode URL-encoded string
#   2. トリム
#      Trim whitespace
#   3. 禁止文字除去
#      Remove unsafe characters
#   4. 区切り正規化
#      Normalize separators
#   5. 最終整形
#      Final cleanup

from urllib.parse import unquote


# ----------------------------
# 正規化処理
# Normalization
# ----------------------------

def normalize_slug(value: str) -> str:
    """
    スラッグ正規化
    Normalize slug
    """
    if value is None:
        return ""

    slug = str(value)

    # URLデコード
    # Decode URL-encoded string
    slug = unquote(slug)

    # 前後空白除去
    # Trim whitespace
    slug = slug.strip()

    # パス区切り防止
    # Prevent path traversal confusion
    slug = slug.replace("/", "-")

    # Windows系危険文字除去
    # Remove Windows-unsafe characters
    slug = slug.replace("\\", "-")
    slug = slug.replace(":", "-")
    slug = slug.replace("*", "")
    slug = slug.replace("?", "")
    slug = slug.replace('"', "")
    slug = slug.replace("<", "")
    slug = slug.replace(">", "")
    slug = slug.replace("|", "")

    # 連続ハイフン整理
    # Normalize repeated hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")

    # 前後ハイフン・空白除去
    # Final trim
    slug = slug.strip(" -")

    return slug
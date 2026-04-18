# パスとファイル名: wiwa/utils/slug.py
from urllib.parse import unquote


def normalize_slug(value: str) -> str:
    if value is None:
        return ""

    slug = str(value)

    # URLエンコード済みで渡ってきた場合にも備えて一度デコード
    slug = unquote(slug)

    # 前後空白除去
    slug = slug.strip()

    # スラッシュは禁止。階層と誤認されるのでハイフンへ置換
    slug = slug.replace("/", "-")

    # Windows系で危険になりやすい文字も軽く潰しておく
    slug = slug.replace("\\", "-")
    slug = slug.replace(":", "-")
    slug = slug.replace("*", "")
    slug = slug.replace("?", "")
    slug = slug.replace('"', "")
    slug = slug.replace("<", "")
    slug = slug.replace(">", "")
    slug = slug.replace("|", "")

    # 連続ハイフンをある程度整理
    while "--" in slug:
        slug = slug.replace("--", "-")

    # 前後のハイフンと空白を除去
    slug = slug.strip(" -")

    return slug
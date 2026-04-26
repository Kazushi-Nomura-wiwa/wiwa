# パスとファイル名: wiwa/core/route_rules.py

# 動的パラメータ名（単一ソース）
DYNAMIC_NAMES = {"id", "slug", "name", "query"}


def split_path(path: str) -> list[str]:
    return [part for part in path.strip("/").split("/") if part]


def is_dynamic_segment(name: str) -> bool:
    return name in DYNAMIC_NAMES
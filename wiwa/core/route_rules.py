# パスとファイル名: wiwa/core/route_rules.py
# Path and filename: wiwa/core/route_rules.py

# ルーティングルール定義
# Routing rules definition
#
# 概要
# Summary
#   動的パラメータ名とパス分割ロジックを定義する
#   Define dynamic parameter names and path utilities
#
# 処理の流れ
# Flow
#   1. パス分割
#      Split path
#   2. 動的パラメータ判定
#      Check dynamic segment

# 動的パラメータ名（単一ソース）
# Dynamic parameter names (single source of truth)
DYNAMIC_NAMES = {"id", "slug", "name", "query"}


def split_path(path: str) -> list[str]:
    """
    パスを分割
    Split path into segments
    """
    return [part for part in path.strip("/").split("/") if part]


def is_dynamic_segment(name: str) -> bool:
    """
    動的パラメータか判定
    Check if segment is dynamic
    """
    return name in DYNAMIC_NAMES
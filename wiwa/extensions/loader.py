# パスとファイル名: wiwa/extensions/loader.py
# Path and filename: wiwa/extensions/loader.py

# 拡張機能ローダー
# Extension loader
#
# 概要
# Summary
#   有効な拡張機能を読み込み、ルート定義を収集する
#   Load enabled extensions and collect route definitions
#
# 処理の流れ
# Flow
#   1. 拡張モジュール読み込み
#      Import extension modules
#   2. register関数呼び出し
#      Call register function
#   3. ルート収集
#      Collect routes
#   4. ルート検証
#      Validate routes

import importlib

from wiwa.config import ENABLED_EXTENSIONS
from wiwa.core.i18n import t


class ExtensionLoader:
    def __init__(self):
        """
        ローダー初期化
        Initialize loader
        """
        self.enabled_extensions = ENABLED_EXTENSIONS

    def load_routes(self) -> list[dict]:
        """
        拡張ルート取得
        Load extension routes
        """
        routes = []

        for extension_name in self.enabled_extensions:
            module_path = f"wiwa.extensions.{extension_name}.extension"

            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                raise ImportError(
                    t("error.extension.load_failed", name=extension_name, path=module_path)
                ) from e

            register = getattr(module, "register", None)
            if register is None:
                continue

            result = register()
            if not result:
                continue

            extension_routes = result.get("routes", [])
            if extension_routes:
                routes.extend(extension_routes)

        self._validate_routes(routes)
        return routes

    def _validate_routes(self, routes: list[dict]) -> None:
        """
        拡張ルート検証
        Validate extension routes
        """
        seen = set()

        for route in routes:
            url = route.get("url")
            method = route.get("method")
            handler = route.get("handler")

            if not url or not method or not handler:
                raise ValueError(t("error.extension.invalid_route", route=route))

            key = (method.upper(), url)

            if key in seen:
                raise ValueError(
                    t("error.extension.duplicate_route", method=method, url=url)
                )

            seen.add(key)
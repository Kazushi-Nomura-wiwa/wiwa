# パスとファイル名: wiwa/extensions/loader.py
import importlib

from wiwa.config import ENABLED_EXTENSIONS


class ExtensionLoader:
    def __init__(self):
        self.enabled_extensions = ENABLED_EXTENSIONS

    def load_routes(self) -> list[dict]:
        routes = []

        for extension_name in self.enabled_extensions:
            module_path = f"wiwa.extensions.{extension_name}.extension"

            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                raise ImportError(
                    f"拡張 '{extension_name}' の読み込みに失敗しました: {module_path}"
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
        seen = set()

        for route in routes:
            url = route.get("url")
            method = route.get("method")
            handler = route.get("handler")

            if not url or not method or not handler:
                raise ValueError(f"拡張ルートの形式が不正です: {route}")

            key = (method.upper(), url)
            if key in seen:
                raise ValueError(
                    f"拡張ルートが重複しています: method={method}, url={url}"
                )

            seen.add(key)
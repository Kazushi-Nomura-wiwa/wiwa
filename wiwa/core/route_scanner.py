# パスとファイル名: wiwa/core/route_scanner.py
# Path and filename: wiwa/core/route_scanner.py

# ルートスキャナ
# Route scanner
#
# 概要
# Summary
#   controllers配下を走査してルート一覧を生成する
#   Scan controllers and build route list
#
# 処理の流れ
# Flow
#   1. モジュール走査
#      Walk modules
#   2. 関数抽出
#      Extract functions
#   3. ルート構築
#      Build route definitions
#   4. ソート
#      Sort routes

import importlib
import inspect
import pkgutil


class RouteScanner:
    def __init__(self, base_package: str = "wiwa.controllers"):
        """
        スキャナ初期化
        Initialize scanner
        """
        self.base_package = base_package
        self._cache = None

    def get_routes(self, refresh: bool = False) -> list[dict]:
        """
        ルート一覧取得
        Get route list
        """
        if refresh or self._cache is None:
            self._cache = self.scan_routes()
        return self._cache

    def scan_routes(self) -> list[dict]:
        """
        ルートスキャン実行
        Scan routes
        """
        routes = []

        package = importlib.import_module(self.base_package)

        # モジュール走査
        # Walk modules
        for module_info in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + ".",
        ):
            module = importlib.import_module(module_info.name)
            routes.extend(self._scan_module(module))

        # パスでソート
        # Sort by path
        routes.sort(key=lambda item: item["path"])
        return routes

    def _scan_module(self, module) -> list[dict]:
        """
        モジュール内ルート抽出
        Extract routes from module
        """
        routes = []
        module_name = module.__name__
        parts = self._module_to_parts(module_name)

        for function_name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ != module_name:
                continue

            if function_name.startswith("_"):
                continue

            routes.append(
                self._build_route(parts, function_name)
            )

        return routes

    def _module_to_parts(self, module_name: str) -> list[str]:
        """
        モジュール名をパスパーツに変換
        Convert module name to path parts
        """
        prefix = self.base_package + "."

        if not module_name.startswith(prefix):
            return []

        relative = module_name.removeprefix(prefix)
        if not relative:
            return []

        parts = relative.split(".")

        if parts and parts[-1] == "index":
            parts = parts[:-1]

        return parts

    def _build_route(self, parts: list[str], function_name: str) -> dict:
        """
        ルート定義生成
        Build route definition
        """
        if not parts and function_name == "index":
            path = "/"
        elif function_name == "index":
            path = "/" + "/".join(parts)
        else:
            path = "/" + "/".join(parts + [function_name])

        handler = ".".join(parts + [function_name]) if parts else function_name

        return {
            "path": path,
            "handler": handler,
        }
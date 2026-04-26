# パスとファイル名: wiwa/core/route_scanner.py

import importlib
import inspect
import pkgutil


class RouteScanner:
    def __init__(self, base_package: str = "wiwa.controllers"):
        self.base_package = base_package
        self._cache = None

    def get_routes(self, refresh: bool = False) -> list[dict]:
        if refresh or self._cache is None:
            self._cache = self.scan_routes()
        return self._cache

    def scan_routes(self) -> list[dict]:
        routes = []

        package = importlib.import_module(self.base_package)

        for module_info in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + ".",
        ):
            module = importlib.import_module(module_info.name)
            routes.extend(self._scan_module(module))

        routes.sort(key=lambda item: item["path"])
        return routes

    def _scan_module(self, module) -> list[dict]:
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
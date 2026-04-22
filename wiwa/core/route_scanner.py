# パスとファイル名: wiwa/core/route_scanner.py
import importlib
import inspect
import pkgutil


class RouteScanner:
    LEGACY_DYNAMIC_NAMES = ["slug", "id", "name", "query"]
    ACTION_DYNAMIC_NAMES = {"edit", "update", "delete", "restore"}

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

        routes.sort(key=lambda item: (item["path"], item["handler"]))
        return routes

    def _scan_module(self, module) -> list[dict]:
        routes = []
        module_name = module.__name__
        relative_parts = self._module_to_parts(module_name)

        for function_name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ != module_name:
                continue

            if function_name.startswith("_"):
                continue

            routes.extend(
                self._build_routes_for_function(
                    relative_parts=relative_parts,
                    function_name=function_name,
                )
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

    def _build_routes_for_function(
        self,
        relative_parts: list[str],
        function_name: str,
    ) -> list[dict]:
        routes = []

        if function_name in self.ACTION_DYNAMIC_NAMES:
            routes.append(
                self._build_action_dynamic_route(relative_parts, function_name)
            )
            return routes

        if function_name in self.LEGACY_DYNAMIC_NAMES:
            routes.append(
                self._build_legacy_dynamic_route(relative_parts, function_name)
            )
            return routes

        static_route = self._build_static_route(relative_parts, function_name)
        if static_route:
            routes.append(static_route)

        return routes

    def _build_static_route(
        self,
        relative_parts: list[str],
        function_name: str,
    ) -> dict | None:
        handler = ".".join(relative_parts + [function_name]) if relative_parts else function_name

        if not relative_parts and function_name == "index":
            path = "/"
            template = "html/index.html"
        elif function_name == "index":
            path = "/" + "/".join(relative_parts)
            template = "html/" + "/".join(relative_parts + ["index"]) + ".html"
        else:
            path = "/" + "/".join(relative_parts + [function_name])
            template = "html/" + "/".join(relative_parts + [function_name]) + ".html"

        return {
            "kind": "static",
            "path": path,
            "handler": handler,
            "template": template,
            "params": [],
            "auth_required": self._is_auth_required(relative_parts),
            "roles": self._get_allowed_roles(relative_parts),
        }

    def _build_action_dynamic_route(
        self,
        relative_parts: list[str],
        function_name: str,
    ) -> dict:
        handler = ".".join(relative_parts + [function_name]) if relative_parts else function_name

        return {
            "kind": "action_dynamic",
            "path": "/" + "/".join(relative_parts + [function_name, "_id"]),
            "handler": handler,
            "template": "html/" + "/".join(relative_parts + [function_name]) + ".html",
            "params": ["id"],
            "auth_required": self._is_auth_required(relative_parts),
            "roles": self._get_allowed_roles(relative_parts),
        }

    def _build_legacy_dynamic_route(
        self,
        relative_parts: list[str],
        function_name: str,
    ) -> dict:
        handler = ".".join(relative_parts + [function_name]) if relative_parts else function_name

        return {
            "kind": "legacy_dynamic",
            "path": "/" + "/".join(relative_parts + [f"_{function_name}"]),
            "handler": handler,
            "template": "html/" + "/".join(relative_parts + [function_name]) + ".html",
            "params": [function_name],
            "auth_required": self._is_auth_required(relative_parts),
            "roles": self._get_allowed_roles(relative_parts),
        }

    def _is_auth_required(self, parts: list[str]) -> bool:
        if not parts:
            return False

        return parts[0] in {"admin", "mypage"}

    def _get_allowed_roles(self, parts: list[str]) -> list[str]:
        if not parts:
            return []

        if parts[0] == "admin":
            return ["admin"]

        if parts[0] == "mypage":
            return ["admin", "author"]

        return []
# パスとファイル名: wiwa/core/resolver.py
import importlib


class Resolver:
    DYNAMIC_NAMES = ["slug", "id", "name", "query"]

    def resolve(self, path: str, method: str = "GET") -> dict | None:
        normalized_path = self._normalize_path(path)
        parts = self._split(normalized_path)

        static_result = self._resolve_static(parts)
        if static_result:
            return self._attach_meta(static_result, parts, method)

        dynamic_result = self._resolve_dynamic(parts)
        if dynamic_result:
            return self._attach_meta(dynamic_result, parts, method)

        return None

    def _attach_meta(
        self,
        result: dict,
        parts: list[str],
        method: str,
    ) -> dict:
        result["method"] = method.upper()
        result["auth_required"] = self._is_auth_required(parts)
        result["roles"] = self._get_allowed_roles(parts)
        return result

    def _build_template_path(self, parts: list[str]) -> str:
        return "html/" + "/".join(parts) + ".html"

    def _resolve_static(self, parts: list[str]) -> dict | None:
        if not parts:
            if self._handler_exists("index.index"):
                return {
                    "handler": "index.index",
                    "template": "html/index.html",
                    "params": {},
                }
            return None

        handler = ".".join(parts)
        if self._handler_exists(handler):
            return {
                "handler": handler,
                "template": self._build_template_path(parts),
                "params": {},
            }

        handler_parts = parts + ["index"]
        handler = ".".join(handler_parts)
        if self._handler_exists(handler):
            return {
                "handler": handler,
                "template": self._build_template_path(handler_parts),
                "params": {},
            }

        return None

    def _resolve_dynamic(self, parts: list[str]) -> dict | None:
        if len(parts) < 2:
            return None

        base_parts = parts[:-1]
        raw_value = parts[-1]

        handler = ".".join(base_parts)
        if self._handler_exists(handler):
            param_name = self._guess_param_name(base_parts)
            template_parts = self._build_dynamic_template_parts(base_parts, param_name)
            return {
                "handler": handler,
                "template": self._build_template_path(template_parts),
                "params": {
                    param_name: raw_value,
                },
            }

        for dynamic_name in self.DYNAMIC_NAMES:
            candidate_parts = parts[:-1] + [dynamic_name]
            legacy_handler = ".".join(candidate_parts)

            if not self._handler_exists(legacy_handler):
                continue

            return {
                "handler": legacy_handler,
                "template": self._build_template_path(candidate_parts),
                "params": {
                    dynamic_name: raw_value,
                },
            }

        return None

    def _build_dynamic_template_parts(
        self,
        base_parts: list[str],
        param_name: str,
    ) -> list[str]:
        if not base_parts:
            return [param_name]

        last = base_parts[-1]

        if last in {"edit", "update", "delete", "restore"}:
            return base_parts

        return base_parts + [param_name]

    def _guess_param_name(self, base_parts: list[str]) -> str:
        if not base_parts:
            return "id"

        last = base_parts[-1]

        if last in {"edit", "update", "delete", "restore"}:
            return "id"

        if last in self.DYNAMIC_NAMES:
            return last

        return "id"

    def _split_handler(self, handler: str) -> tuple[str, str]:
        parts = handler.split(".")
        module_path = "wiwa.controllers." + ".".join(parts[:-1])
        function_name = parts[-1]
        return module_path, function_name

    def _handler_exists(self, handler: str) -> bool:
        module_path, function_name = self._split_handler(handler)

        if not function_name or function_name.startswith("_"):
            return False

        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            return False

        target = getattr(module, function_name, None)
        return callable(target)

    def _normalize_path(self, path: str) -> str:
        if not path:
            return "/"
        return "/" + path.strip("/")

    def _split(self, path: str) -> list[str]:
        stripped = path.strip("/")
        if not stripped:
            return []
        return [part for part in stripped.split("/") if part]

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
            return ["admin", "editor", "author"]

        return []
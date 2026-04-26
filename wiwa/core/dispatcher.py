# パスとファイル名: wiwa/core/dispatcher.py

import importlib

from wiwa.core.response import forbidden
from wiwa.utils.csrf import validate_csrf


CSRF_EXEMPT_PATHS = {
    "/auth/login",
}


class Dispatcher:
    def dispatch(self, resolved: dict, request):
        if not resolved:
            return forbidden()

        if self._should_check_csrf(request):
            if not validate_csrf(request):
                return forbidden()

        func = self.get_callable(resolved.get("handler"))
        params = resolved.get("params", {})

        return func(request, route=resolved, **params)

    def get_callable(self, handler: str):
        module_path, function_name = self._split_handler(handler)

        if not function_name or function_name.startswith("_"):
            raise ValueError(f"非公開 handler は呼び出せません: {handler}")

        module = importlib.import_module(module_path)
        func = getattr(module, function_name, None)

        if not callable(func):
            raise TypeError(f"handler は callable ではありません: {handler}")

        return func

    def _split_handler(self, handler: str) -> tuple[str, str]:
        if not handler:
            raise ValueError("handler が空です。")

        parts = handler.split(".")
        if len(parts) < 2:
            raise ValueError(f"handler の形式が不正です: {handler}")

        if handler.startswith("wiwa."):
            module_path = ".".join(parts[:-1])
        else:
            module_path = "wiwa.controllers." + ".".join(parts[:-1])

        function_name = parts[-1]
        return module_path, function_name

    def _should_check_csrf(self, request) -> bool:
        if request.method != "POST":
            return False

        if request.path in CSRF_EXEMPT_PATHS:
            return False

        return True
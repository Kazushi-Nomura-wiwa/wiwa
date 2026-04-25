# パスとファイル名: wiwa/core/dispatcher.py

import importlib

from wiwa.core.response import forbidden
from wiwa.utils.csrf import validate_csrf


# CSRFチェックを除外するパス
CSRF_EXEMPT_PATHS = {
    "/auth/login",
}


class Dispatcher:
    def get_callable(self, handler: str):
        if not handler:
            raise ValueError("handler が空です。")

        parts = handler.split(".")
        if len(parts) < 2:
            raise ValueError(f"handler の形式が不正です: {handler}")

        if handler.startswith("wiwa."):
            module_path = ".".join(parts[:-1])
            function_name = parts[-1]
        else:
            module_path = "wiwa.controllers." + ".".join(parts[:-1])
            function_name = parts[-1]

        if not function_name or function_name.startswith("_"):
            raise ValueError(f"非公開 handler は呼び出せません: {handler}")

        module = importlib.import_module(module_path)
        func = getattr(module, function_name, None)

        if not callable(func):
            raise TypeError(f"handler は callable ではありません: {handler}")

        return func

    def dispatch(self, resolved: dict, request):
        if not resolved:
            return forbidden()

        if request.method == "POST" and request.path not in CSRF_EXEMPT_PATHS:
            if not validate_csrf(request):
                return forbidden()

        handler = resolved.get("handler")
        params = resolved.get("params", {})

        func = self.get_callable(handler)

        return func(request, route=resolved, **params)
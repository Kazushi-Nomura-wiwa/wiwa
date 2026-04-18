# パスとファイル名: wiwa/core/dispatcher.py
import importlib


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

        module = importlib.import_module(module_path)
        func = getattr(module, function_name)

        if not callable(func):
            raise TypeError(f"handler は callable ではありません: {handler}")

        return func

    def dispatch(self, resolved: dict, request):
        handler = resolved.get("handler")
        params = resolved.get("params", {})

        func = self.get_callable(handler)

        return func(request, route=resolved, **params)
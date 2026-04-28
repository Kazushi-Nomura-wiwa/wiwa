# パスとファイル名: wiwa/core/dispatcher.py
# Path and filename: wiwa/core/dispatcher.py

# ディスパッチ処理
# Request dispatcher
#
# 概要
# Summary
#   解決済みルートに基づいてハンドラを呼び出す
#   Invoke handler based on resolved route
#
# 処理の流れ
# Flow
#   1. ルート存在チェック
#      Check resolved route
#   2. CSRF検証
#      Validate CSRF
#   3. ハンドラ解決
#      Resolve handler
#   4. ハンドラ実行
#      Execute handler

import importlib

from wiwa.core.response import forbidden
from wiwa.core.i18n import t
from wiwa.utils.csrf import validate_csrf


CSRF_EXEMPT_PATHS = {
    "/auth/login",
}


class Dispatcher:
    def dispatch(self, resolved: dict, request):
        """
        解決済みルートから処理を呼び出す
        Dispatch the resolved route to the handler
        """
        if not resolved:
            return forbidden()

        if self._should_check_csrf(request):
            if not validate_csrf(request):
                return forbidden()

        func = self.get_callable(resolved.get("handler"))
        params = resolved.get("params", {})

        return func(request, route=resolved, **params)

    def get_callable(self, handler: str):
        """
        handler文字列から呼び出し可能な関数を取得
        Get a callable function from the handler string
        """
        module_path, function_name = self._split_handler(handler)

        if not function_name or function_name.startswith("_"):
            raise ValueError(t("error.handler.private", handler=handler))

        module = importlib.import_module(module_path)
        func = getattr(module, function_name, None)

        if not callable(func):
            raise TypeError(t("error.handler.not_callable", handler=handler))

        return func

    def _split_handler(self, handler: str) -> tuple[str, str]:
        """
        handler文字列をモジュールパスと関数名に分割
        Split the handler string into module path and function name
        """
        if not handler:
            raise ValueError(t("error.handler.empty"))

        parts = handler.split(".")
        if len(parts) < 2:
            raise ValueError(t("error.handler.invalid", handler=handler))

        if handler.startswith("wiwa."):
            module_path = ".".join(parts[:-1])
        else:
            module_path = "wiwa.controllers." + ".".join(parts[:-1])

        function_name = parts[-1]
        return module_path, function_name

    def _should_check_csrf(self, request) -> bool:
        """
        CSRF検証が必要か判定
        Check whether CSRF validation is required
        """
        if request.method != "POST":
            return False

        if request.path in CSRF_EXEMPT_PATHS:
            return False

        return True
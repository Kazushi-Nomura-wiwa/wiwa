# パスとファイル名: wiwa/core/response.py
# Path and filename: wiwa/core/response.py

# HTTPレスポンスユーティリティ
# HTTP response utilities
#
# 概要
# Summary
#   WSGIレスポンスを生成し、Cookieやヘッダを管理する
#   Build WSGI responses and manage headers and cookies
#
# 処理の流れ
# Flow
#   1. レスポンス生成
#      Create response
#   2. ヘッダ設定
#      Set headers
#   3. Cookie操作
#      Handle cookies
#   4. WSGI応答
#      Return WSGI response

from http import cookies


class Response:
    def __init__(self, body="", status="200 OK", headers=None):
        """
        レスポンスを初期化
        Initialize response
        """
        self.body = body
        self.status = status
        self.headers = headers or []

    def set_cookie(
        self,
        key: str,
        value: str,
        path: str = "/",
        http_only: bool = True,
        secure: bool = False,
        same_site: str = "Lax",
        max_age: int | None = None,
    ) -> None:
        """
        Cookieを設定
        Set cookie
        """
        cookie = cookies.SimpleCookie()
        cookie[key] = value
        cookie[key]["path"] = path

        if http_only:
            cookie[key]["httponly"] = True

        if secure:
            cookie[key]["secure"] = True

        if same_site:
            cookie[key]["samesite"] = same_site

        if max_age is not None:
            cookie[key]["max-age"] = str(max_age)

        self.headers.append(("Set-Cookie", cookie.output(header="").strip()))

    def delete_cookie(self, key: str, path: str = "/") -> None:
        """
        Cookie削除
        Delete cookie
        """
        cookie = cookies.SimpleCookie()
        cookie[key] = ""
        cookie[key]["path"] = path
        cookie[key]["max-age"] = "0"
        self.headers.append(("Set-Cookie", cookie.output(header="").strip()))

    def has_cookie(self, key: str) -> bool:
        """
        Cookie存在確認
        Check cookie existence
        """
        prefix = f"{key}="

        for header_name, header_value in self.headers:
            if header_name.lower() != "set-cookie":
                continue

            if header_value.startswith(prefix):
                return True

        return False

    def __call__(self, environ, start_response):
        """
        WSGIレスポンスを返す
        Return WSGI response
        """
        body = self.body
        if isinstance(body, str):
            body = body.encode("utf-8")

        headers = list(self.headers)

        # Content-Type未指定時はHTMLを設定
        # Set default Content-Type
        if not any(name.lower() == "content-type" for name, _ in headers):
            headers.append(("Content-Type", "text/html; charset=utf-8"))

        start_response(self.status, headers)
        return [body]


def html(body: str, status: str = "200 OK"):
    """
    HTMLレスポンス生成
    Create HTML response
    """
    return Response(body=body, status=status)


def not_found():
    """
    404レスポンス生成
    Create 404 response
    """
    return Response(body="404 Not Found", status="404 Not Found")


def forbidden():
    """
    403レスポンス生成
    Create 403 response
    """
    return Response(body="403 Forbidden", status="403 Forbidden")


def redirect(location: str):
    """
    リダイレクトレスポンス生成
    Create redirect response
    """
    return Response(body="", status="302 Found", headers=[("Location", location)])


def internal_server_error(message: str = "500 Internal Server Error"):
    """
    500レスポンス生成
    Create 500 response
    """
    return Response(body=message, status="500 Internal Server Error")
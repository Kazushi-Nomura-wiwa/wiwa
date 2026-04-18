# パスとファイル名: wiwa/core/response.py
from http import cookies


class Response:
    def __init__(self, body="", status="200 OK", headers=None):
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
        cookie = cookies.SimpleCookie()
        cookie[key] = ""
        cookie[key]["path"] = path
        cookie[key]["max-age"] = "0"
        self.headers.append(("Set-Cookie", cookie.output(header="").strip()))

    def __call__(self, environ, start_response):
        body = self.body
        if isinstance(body, str):
            body = body.encode("utf-8")

        headers = list(self.headers)
        if not any(name.lower() == "content-type" for name, _ in headers):
            headers.append(("Content-Type", "text/html; charset=utf-8"))

        start_response(self.status, headers)
        return [body]


def html(body: str, status: str = "200 OK"):
    return Response(body=body, status=status)


def not_found():
    return Response(body="404 Not Found", status="404 Not Found")


def forbidden():
    return Response(body="403 Forbidden", status="403 Forbidden")


def redirect(location: str):
    return Response(body="", status="302 Found", headers=[("Location", location)])


def internal_server_error(message: str = "500 Internal Server Error"):
    return Response(body=message, status="500 Internal Server Error")
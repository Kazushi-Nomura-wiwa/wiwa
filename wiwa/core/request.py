# パスとファイル名: wiwa/core/request.py
# Path and filename: wiwa/core/request.py

# HTTPリクエストラッパー
# HTTP request wrapper
#
# 概要
# Summary
#   WSGI environをラップし、クエリ・フォーム・Cookie・ファイルを扱いやすくする
#   Wrap WSGI environ to provide easy access to query, form, cookies, and files
#
# 処理の流れ
# Flow
#   1. environから基本情報取得
#      Extract basic data from environ
#   2. クエリ解析
#      Parse query string
#   3. フォーム解析
#      Parse form data
#   4. multipart解析
#      Parse multipart form data
#   5. Cookie解析
#      Parse cookies
#   6. 付加情報取得
#      Provide extra info

from http import cookies
from io import BytesIO
from urllib.parse import parse_qs, unquote


# アップロードファイル
# Uploaded file wrapper
class UploadedFile:
    def __init__(
        self,
        filename: str,
        content_type: str,
        data: bytes,
    ):
        """
        アップロードファイル初期化
        Initialize uploaded file
        """
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(data)


# HTTPリクエスト
# HTTP request
class Request:
    def __init__(self, environ: dict):
        """
        リクエスト初期化
        Initialize request
        """
        self.environ = environ

        self.method = environ.get(
            "REQUEST_METHOD",
            "GET",
        ).upper()

        self.path = self._decode_path(
            environ.get("PATH_INFO", "/")
        )

        self.query_string = environ.get(
            "QUERY_STRING",
            "",
        )

        self.query_params = parse_qs(self.query_string)

        self._body = None
        self._form_data = None
        self._files = None
        self._cookies = None

        self.user = None
        self.session_id = None

    @property
    def query(self) -> dict[str, str]:
        """
        クエリ取得
        Get query parameters
        """
        return {
            key: values[0]
            for key, values in self.query_params.items()
            if values
        }

    def get_query(
        self,
        key: str,
        default: str = "",
    ) -> str:
        """
        クエリ値取得
        Get query value
        """
        values = self.query_params.get(key)

        if not values:
            return default

        return values[0]

    def get_form(
        self,
        key: str,
        default: str = "",
    ) -> str:
        """
        フォーム値取得
        Get form value
        """
        if self._form_data is None:
            self._parse_form_data()

        values = self._form_data.get(key)

        if not values:
            return default

        return values[0]

    @property
    def files(self):
        """
        アップロードファイル取得
        Get uploaded files
        """
        if self._files is None:
            self._parse_multipart()

        return self._files

    @property
    def cookies(self) -> dict[str, str]:
        """
        Cookie取得
        Get cookies
        """
        if self._cookies is None:
            self._parse_cookies()

        return self._cookies

    @property
    def remote_addr(self) -> str:
        """
        クライアントIP取得
        Get client IP address
        """
        remote_addr = self.environ.get(
            "REMOTE_ADDR",
            "",
        ) or ""

        x_forwarded_for = self.environ.get(
            "HTTP_X_FORWARDED_FOR",
            "",
        ) or ""

        x_real_ip = self.environ.get(
            "HTTP_X_REAL_IP",
            "",
        ) or ""

        trusted_proxies = {
            "127.0.0.1",
            "::1",
        }

        if remote_addr in trusted_proxies:
            if x_forwarded_for:
                forwarded_ips = [
                    ip.strip()
                    for ip in x_forwarded_for.split(",")
                    if ip.strip()
                ]

                if forwarded_ips:
                    return forwarded_ips[0]

            if x_real_ip.strip():
                return x_real_ip.strip()

        return remote_addr

    @property
    def user_agent(self) -> str:
        """
        ユーザーエージェント取得
        Get user agent
        """
        return self.environ.get(
            "HTTP_USER_AGENT",
            "",
        )

    @property
    def host(self) -> str:
        """
        ホスト取得
        Get host
        """
        return self.environ.get(
            "HTTP_HOST",
            "",
        )

    @property
    def referer(self) -> str:
        """
        リファラ取得
        Get referer
        """
        return self.environ.get(
            "HTTP_REFERER",
            "",
        )

    def _decode_path(self, raw_path: str) -> str:
        """
        パスデコード
        Decode request path
        """
        value = raw_path or "/"

        try:
            return (
                unquote(value)
                .encode("latin-1")
                .decode("utf-8")
            )

        except (
            UnicodeEncodeError,
            UnicodeDecodeError,
        ):
            try:
                return unquote(value)

            except Exception:
                return value

    def _read_body(self) -> bytes:
        """
        リクエストボディ取得
        Read request body
        """
        if self._body is not None:
            return self._body

        try:
            content_length = int(
                self.environ.get(
                    "CONTENT_LENGTH",
                    "0",
                ) or "0"
            )

        except ValueError:
            content_length = 0

        if content_length <= 0:
            self._body = b""
            return self._body

        self._body = self.environ[
            "wsgi.input"
        ].read(content_length)

        return self._body

    def _parse_form_data(self) -> None:
        """
        フォーム解析
        Parse form data
        """
        self._form_data = {}

        if self.method not in {
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return

        content_type = self.environ.get(
            "CONTENT_TYPE",
            "",
        )

        # multipartは除外
        # Skip multipart
        if "multipart/form-data" in content_type:
            return

        body = self._read_body()

        if (
            "application/x-www-form-urlencoded"
            in content_type
        ):
            decoded = body.decode("utf-8")

            self._form_data = parse_qs(decoded)

    def _parse_multipart(self):
        """
        multipart解析
        Parse multipart form data
        """
        self._files = {}

        if self.method not in {
            "POST",
            "PUT",
            "PATCH",
        }:
            return

        content_type = self.environ.get(
            "CONTENT_TYPE",
            "",
        )

        if "multipart/form-data" not in content_type:
            return

        boundary = self._get_multipart_boundary(
            content_type
        )

        if not boundary:
            return

        body = self._read_body()

        boundary_bytes = (
            b"--" + boundary.encode("utf-8")
        )

        parts = body.split(boundary_bytes)

        for part in parts:
            part = part.strip()

            if not part or part == b"--":
                continue

            if part.endswith(b"--"):
                part = part[:-2].strip()

            if b"\r\n\r\n" not in part:
                continue

            raw_headers, file_data = part.split(
                b"\r\n\r\n",
                1,
            )

            file_data = file_data.rstrip(b"\r\n")

            headers = self._parse_multipart_headers(
                raw_headers
            )

            disposition = headers.get(
                "content-disposition",
                "",
            )

            name = self._get_header_value(
                disposition,
                "name",
            )

            filename = self._get_header_value(
                disposition,
                "filename",
            )

            if not name or not filename:
                continue

            uploaded_file = UploadedFile(
                filename=filename,
                content_type=headers.get(
                    "content-type",
                    "",
                ),
                data=file_data,
            )

            self._files[name] = uploaded_file

    def _get_multipart_boundary(
        self,
        content_type: str,
    ) -> str:
        """
        boundary取得
        Get multipart boundary
        """
        parts = content_type.split(";")

        for part in parts:
            part = part.strip()

            if part.startswith("boundary="):
                boundary = part.split(
                    "=",
                    1,
                )[1].strip()

                return boundary.strip('"')

        return ""

    def _parse_multipart_headers(
        self,
        raw_headers: bytes,
    ) -> dict[str, str]:
        """
        multipartヘッダ解析
        Parse multipart headers
        """
        headers = {}

        for line in raw_headers.decode(
            "utf-8",
            errors="replace",
        ).split("\r\n"):

            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            headers[
                key.strip().lower()
            ] = value.strip()

        return headers

    def _get_header_value(
        self,
        header: str,
        key: str,
    ) -> str:
        """
        ヘッダ値取得
        Get header value
        """
        parts = header.split(";")

        for part in parts:
            part = part.strip()

            if part.startswith(f"{key}="):
                value = part.split(
                    "=",
                    1,
                )[1].strip()

                return value.strip('"')

        return ""

    def _parse_cookies(self) -> None:
        """
        Cookie解析
        Parse cookies
        """
        self._cookies = {}

        raw_cookie = self.environ.get(
            "HTTP_COOKIE",
            "",
        )

        if not raw_cookie:
            return

        simple_cookie = cookies.SimpleCookie()

        simple_cookie.load(raw_cookie)

        for key, morsel in simple_cookie.items():
            self._cookies[key] = morsel.value
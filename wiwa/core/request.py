# パスとファイル名: wiwa/core/request.py
# Path and filename: wiwa/core/request.py

# HTTPリクエストラッパー
# HTTP request wrapper
#
# 概要
# Summary
#   WSGI environをラップし、クエリ・フォーム・Cookieなどを扱いやすくする
#   Wrap WSGI environ to provide easy access to query, form, and cookies
#
# 処理の流れ
# Flow
#   1. environから基本情報取得
#      Extract basic data from environ
#   2. クエリ解析
#      Parse query string
#   3. フォーム解析
#      Parse form data
#   4. Cookie解析
#      Parse cookies
#   5. 付加情報取得（IP, UAなど）
#      Provide extra info (IP, UA, etc.)

from http import cookies
from urllib.parse import parse_qs, unquote


class Request:
    def __init__(self, environ: dict):
        """
        リクエストを初期化
        Initialize request
        """
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.path = self._decode_path(environ.get("PATH_INFO", "/"))
        self.query_string = environ.get("QUERY_STRING", "")
        self.query_params = parse_qs(self.query_string)

        self._form_data = None
        self._cookies = None

        self.user = None
        self.session_id = None

    @property
    def query(self) -> dict[str, str]:
        """
        クエリを辞書として取得
        Get query parameters as dict
        """
        return {
            key: values[0]
            for key, values in self.query_params.items()
            if values
        }

    def get_query(self, key: str, default: str = "") -> str:
        """
        クエリ値を取得
        Get query value
        """
        values = self.query_params.get(key)
        if not values:
            return default
        return values[0]

    def get_form(self, key: str, default: str = "") -> str:
        """
        フォーム値を取得
        Get form value
        """
        if self._form_data is None:
            self._parse_form_data()

        values = self._form_data.get(key)
        if not values:
            return default
        return values[0]

    @property
    def cookies(self) -> dict[str, str]:
        """
        Cookieを取得
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
        remote_addr = self.environ.get("REMOTE_ADDR", "") or ""
        x_forwarded_for = self.environ.get("HTTP_X_FORWARDED_FOR", "") or ""
        x_real_ip = self.environ.get("HTTP_X_REAL_IP", "") or ""

        trusted_proxies = {"127.0.0.1", "::1"}

        if remote_addr in trusted_proxies:
            if x_forwarded_for:
                forwarded_ips = [ip.strip() for ip in x_forwarded_for.split(",") if ip.strip()]
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
        return self.environ.get("HTTP_USER_AGENT", "")

    @property
    def host(self) -> str:
        """
        ホスト名取得
        Get host
        """
        return self.environ.get("HTTP_HOST", "")

    @property
    def referer(self) -> str:
        """
        リファラ取得
        Get referer
        """
        return self.environ.get("HTTP_REFERER", "")

    def _decode_path(self, raw_path: str) -> str:
        """
        パスをデコード
        Decode path safely
        """
        value = raw_path or "/"

        try:
            return unquote(value).encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                return unquote(value)
            except Exception:
                return value

    def _parse_form_data(self) -> None:
        """
        フォームデータ解析
        Parse form data
        """
        self._form_data = {}

        if self.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return

        try:
            content_length = int(self.environ.get("CONTENT_LENGTH", "0") or "0")
        except ValueError:
            content_length = 0

        if content_length <= 0:
            return

        body = self.environ["wsgi.input"].read(content_length)
        content_type = self.environ.get("CONTENT_TYPE", "")

        if "application/x-www-form-urlencoded" in content_type:
            decoded = body.decode("utf-8")
            self._form_data = parse_qs(decoded)
            return

        self._form_data = {}

    def _parse_cookies(self) -> None:
        """
        Cookie解析
        Parse cookies
        """
        self._cookies = {}

        raw_cookie = self.environ.get("HTTP_COOKIE", "")
        if not raw_cookie:
            return

        simple_cookie = cookies.SimpleCookie()
        simple_cookie.load(raw_cookie)

        for key, morsel in simple_cookie.items():
            self._cookies[key] = morsel.value
# パスとファイル名: wiwa/server.py

# WiWA開発用サーバー
# Development server for WiWA

from wsgiref.simple_server import WSGIRequestHandler, make_server

from wiwa.config import HOST, PORT
from wiwa.app import application


class QuietHandler(WSGIRequestHandler):
    """
    標準アクセスログを抑制するハンドラー
    Handler that suppresses default access logs
    """

    def log_message(self, format, *args):
        # WiWA側でアクセスログを処理するため、標準ログは出力しない
        # Suppress default logs because WiWA handles access logging
        pass


def run():
    """
    開発用サーバーを起動する
    Start the development server
    """

    with make_server(HOST, PORT, application, handler_class=QuietHandler) as httpd:
        print(f"[WiWA] Starting server on http://{HOST}:{PORT}", flush=True)
        httpd.serve_forever()
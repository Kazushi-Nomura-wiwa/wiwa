# パスとファイル名: wiwa/server.py
# Path and filename: wiwa/server.py

# WiWA開発用サーバー
# Development server for WiWA
#
# 概要
# Summary
#   ローカル開発用のWSGIサーバーを提供する
#   Provide a local WSGI server for development
#
# 処理の流れ
# Flow
#   1. サーバー生成
#      Create server
#   2. 起動ログ出力
#      Print startup message
#   3. サーバー起動
#      Start serving requests

from wsgiref.simple_server import WSGIRequestHandler, make_server

from wiwa.config import HOST, PORT
from wiwa.app import application


class QuietHandler(WSGIRequestHandler):
    """
    標準アクセスログを抑制するハンドラー
    Handler that suppresses default access logs
    """

    def log_message(self, format, *args):
        # 標準ログを出力しない
        # Suppress default logs
        pass


def run():
    """
    開発用サーバーを起動する
    Start the development server
    """

    with make_server(HOST, PORT, application, handler_class=QuietHandler) as httpd:
        print(f"[WiWA] Starting server on http://{HOST}:{PORT}", flush=True)
        httpd.serve_forever()
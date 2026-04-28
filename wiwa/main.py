# パスとファイル名: wiwa/main.py
# Path and filename: wiwa/main.py

# WSGIアプリケーション公開モジュール
# Public module for WSGI application
#
# 概要
# Summary
#   外部サーバーから参照されるエントリーポイント
#   Entry point for external WSGI servers
#
# 使用例
# Example
#   gunicorn wiwa.main:application

# WiWAのWSGIアプリケーション本体
# Core WSGI application for WiWA
from wiwa.app import application


# 公開対象の定義
# Explicitly define public exports
__all__ = ["application"]
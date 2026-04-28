# パスとファイル名: wiwa/main.py

# WSGIアプリケーションの公開用モジュール
# Public module for exposing the WSGI application
#
# 例:
# Example:
#   gunicorn wiwa.main:application

# WiWAのWSGIアプリケーション本体
# Core WSGI application for WiWA
from wiwa.app import application


# 外部から公開する名前を明示
# Explicitly define public exports
__all__ = ["application"]
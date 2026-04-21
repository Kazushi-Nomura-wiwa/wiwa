# パスとファイル名: wiwa/server.py
from wsgiref.simple_server import WSGIRequestHandler, make_server

from wiwa.config import HOST, PORT
from wiwa.app import application


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


def run():
    with make_server(HOST, PORT, application, handler_class=QuietHandler) as httpd:
        print(f"[WiWA] Starting server on http://{HOST}:{PORT}", flush=True)
        httpd.serve_forever()
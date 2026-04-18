# パスとファイル名: wiwa/config.py
from pathlib import Path
from zoneinfo import ZoneInfo

HOST = "127.0.0.1"
PORT = 8000

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_BASE = BASE_DIR / "templates"

MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB_NAME = "wiwa"

TIMEZONE = ZoneInfo("Asia/Tokyo")

LOGIN_URL = "/auth/login"

ACTIVE_THEME = "default"

POSTS_PER_PAGE = 10

SITE_URL = "https://wiwa.jp"

ENABLED_EXTENSIONS = [
    "sitemap",
    "robots",
]
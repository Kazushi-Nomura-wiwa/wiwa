# パスとファイル名: wiwa/config.py
from pathlib import Path
from zoneinfo import ZoneInfo

# ------------------------------
# サーバー設定
# ------------------------------
# アプリケーションのバインドアドレス
HOST = "127.0.0.1"

# アプリケーションのポート番号
PORT = 8000

# ------------------------------
# パス設定
# ------------------------------

# このファイル（config.py）のディレクトリ
PACKAGE_DIR = Path(__file__).resolve().parent

# run.py があるプロジェクトルート
BASE_DIR = PACKAGE_DIR.parent

# テンプレートのベースディレクトリ
TEMPLATE_BASE = BASE_DIR / "templates"

# 静的ファイルのベースディレクトリ
STATIC_BASE = BASE_DIR / "static"

# アップロードファイルのベースディレクトリ
UPLOAD_BASE = BASE_DIR / "uploads"

# 画像アップロード先
UPLOAD_IMG_DIR = UPLOAD_BASE / "img"

# 画像アップロードURL
UPLOAD_IMG_URL_PREFIX = "/uploads/img"

# ファイルアップロード先
UPLOAD_FILE_DIR = UPLOAD_BASE / "file"

# ファイルアップロードURL
UPLOAD_FILE_URL_PREFIX = "/uploads/file"

# 一時ファイルアップロード先
UPLOAD_TMP_DIR = UPLOAD_BASE / "tmp"

# 一時ファイルアップロードURL
UPLOAD_TMP_URL_PREFIX = "/uploads/tmp"

# テーマファイルのベースディレクトリ
THEME_BASE = BASE_DIR / "themes"

# テーマURL
THEME_URL_PREFIX = "/themes"

# ------------------------------
# MongoDB設定
# ------------------------------
# MongoDBの接続URI
MONGODB_URI = "mongodb://localhost:27017"

# 使用するデータベース名
MONGODB_DB_NAME = "wiwa"

# ------------------------------
# タイムゾーン設定
# ------------------------------
# アプリケーション全体で使用するタイムゾーン
TIMEZONE = ZoneInfo("Asia/Tokyo")

# ------------------------------
# 認証・ログイン設定
# ------------------------------
# 未認証時のリダイレクト先URL
LOGIN_URL = "/auth/login"

# セッションCookie名
SESSION_COOKIE_NAME = "session_id"

# セッション有効期限（日数）
# この日数をもとに expires_at と Cookie の max_age を計算する
SESSION_EXPIRES_DAYS = 7

# ------------------------------
# テーマ設定
# ------------------------------
# 使用するテーマ名（templates/themes/<name> に対応）
ACTIVE_THEME = "default"

# ------------------------------
# 投稿（Post）設定
# ------------------------------
# 一覧ページの表示件数
POSTS_PER_PAGE = 10

# ゴミ箱に入れてから完全削除されるまでの日数
# delete時に purge_at = now + この日数 で設定される
TRASH_RETENTION_DAYS = 30

# ------------------------------
# サイト設定
# ------------------------------
# サイトのベースURL（絶対URL生成などで使用）
SITE_URL = "https://wiwa.jp"

# ------------------------------
# 拡張機能（Extensions）
# ------------------------------
# 有効化する拡張機能の一覧
ENABLED_EXTENSIONS = [
    "sitemap",
    "robots",
]

# ------------------------------
# セキュリティ設定
# ------------------------------
# CSRFトークン生成時のバイト長
CSRF_TOKEN_BYTES = 32

# ------------------------------
# アクセスログ設定
# ------------------------------
# ログが自動削除されるまでの日数（MongoDB TTL）
ACCESS_LOG_RETENTION_DAYS = 90

# ------------------------------
# 予約されたスラッグ
# ------------------------------
# これらのスラッグは固定ページで使用できないようにする
RESERVED_SLUGS = [
    "admin",
    "mypage",
    "auth",
    "post",
    "tag",
    "search",
    "index",
    "api",
    "static",
    "assets",
]
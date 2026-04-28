# パスとファイル名: wiwa/config.py
# Path and filename: wiwa/config.py

# WiWA基本設定
# Basic configuration for WiWA

from pathlib import Path
from zoneinfo import ZoneInfo


# ------------------------------
# i18n設定
# i18n settings
# ------------------------------

# 標準言語
# Default language
DEFAULT_LANG = "ja"

# 対応言語
# Supported languages
SUPPORTED_LANGS = ["ja", "en"]


# ------------------------------
# サーバー設定
# Server settings
# ------------------------------

# アプリケーションのバインドアドレス
# Application bind address
HOST = "127.0.0.1"

# アプリケーションのポート番号
# Application port number
PORT = 8000


# ------------------------------
# パス設定
# Path settings
# ------------------------------

# このファイル（config.py）のディレクトリ
# Directory of this file (config.py)
PACKAGE_DIR = Path(__file__).resolve().parent

# run.py があるプロジェクトルート
# Project root where run.py exists
BASE_DIR = PACKAGE_DIR.parent

# テンプレートのベースディレクトリ
# Base directory for templates
TEMPLATE_BASE = BASE_DIR / "templates"

# 静的ファイルのベースディレクトリ
# Base directory for static files
STATIC_BASE = BASE_DIR / "static"

# アップロードファイルのベースディレクトリ
# Base directory for uploaded files
UPLOAD_BASE = BASE_DIR / "uploads"

# ファイルアップロード先ディレクトリ
# Directory for uploaded files
UPLOAD_FILE_DIR = UPLOAD_BASE / "file"

# ファイルアップロードURLプレフィックス
# URL prefix for uploaded files
UPLOAD_FILE_URL_PREFIX = "/uploads/file"

# 一時ファイルアップロード先ディレクトリ
# Directory for temporary uploads
UPLOAD_TMP_DIR = UPLOAD_BASE / "tmp"

# 一時ファイルアップロードURLプレフィックス
# URL prefix for temporary uploads
UPLOAD_TMP_URL_PREFIX = "/uploads/tmp"

# テーマファイルのベースディレクトリ
# Base directory for theme files
THEME_BASE = BASE_DIR / "themes"

# テーマURLプレフィックス
# URL prefix for theme files
THEME_URL_PREFIX = "/themes"


# ------------------------------
# MongoDB設定
# MongoDB settings
# ------------------------------

# MongoDBの接続URI
# MongoDB connection URI
MONGODB_URI = "mongodb://localhost:27017"

# 使用するデータベース名
# Database name
MONGODB_DB_NAME = "wiwa"


# ------------------------------
# タイムゾーン設定
# Timezone settings
# ------------------------------

# アプリケーション全体で使用するタイムゾーン
# Timezone used by the application
TIMEZONE = ZoneInfo("Asia/Tokyo")


# ------------------------------
# 認証・ログイン設定
# Authentication settings
# ------------------------------

# 未認証時のリダイレクト先URL
# Redirect URL for unauthenticated users
LOGIN_URL = "/auth/login"

# セッションCookie名
# Session cookie name
SESSION_COOKIE_NAME = "session_id"

# セッション有効期限（日数）
# Session expiration in days
#
# この日数をもとにDB側のexpires_atとCookieのmax_ageを計算する
# This value is used to calculate DB expires_at and Cookie max_age
SESSION_EXPIRES_DAYS = 7


# ------------------------------
# テーマ設定
# Theme settings
# ------------------------------

# 使用するテーマ名
# Active theme name
#
# themes/<name> に対応する
# Corresponds to themes/<name>
ACTIVE_THEME = "default"


# ------------------------------
# 投稿設定
# Post settings
# ------------------------------

# 一覧ページの表示件数
# Number of posts per list page
POSTS_PER_PAGE = 10

# ゴミ箱に入れてから完全削除されるまでの日数
# Number of days before trashed posts are permanently deleted
#
# delete時に purge_at = now + この日数 で設定される
# purge_at is set to now + this value when deleted
TRASH_RETENTION_DAYS = 30


# ------------------------------
# サイト設定
# Site settings
# ------------------------------

# サイトのベースURL
# Base URL of the site
#
# sitemap.xmlや絶対URL生成で使用する
# Used for sitemap.xml and absolute URL generation
SITE_URL = "https://wiwa.jp"


# ------------------------------
# 拡張機能設定
# Extension settings
# ------------------------------

# 有効化する拡張機能の一覧
# List of enabled extensions
ENABLED_EXTENSIONS = [
    "sitemap",
    "robots",
]


# ------------------------------
# セキュリティ設定
# Security settings
# ------------------------------

# CSRFトークン生成時のバイト長
# Byte length for CSRF token generation
CSRF_TOKEN_BYTES = 32


# ------------------------------
# アクセスログ設定
# Access log settings
# ------------------------------

# ログが自動削除されるまでの日数
# Number of days before access logs are automatically deleted
#
# MongoDB TTLインデックスで使用する
# Used by MongoDB TTL index
ACCESS_LOG_RETENTION_DAYS = 90


# ------------------------------
# 予約スラッグ設定
# Reserved slug settings
# ------------------------------

# 固定ページで使用できない予約済みスラッグ
# Reserved slugs that cannot be used for pages
#
# ルーティングや管理画面と衝突するURLを防ぐ
# Prevents conflicts with routing and admin URLs
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


# ------------------------------
# トップページ設定
# Home page settings
# ------------------------------

# トップページに表示する投稿数
# Number of posts shown on home page
HOME_POSTS_LIMIT = 5


# ------------------------------
# ファイルアップロード設定
# File upload settings
# ------------------------------

# 画像アップロード最大サイズ（バイト）
# Max upload size for images (bytes)
MAX_UPLOAD_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# ファイルアップロード最大サイズ（バイト）
# Max upload size for files (bytes)
MAX_UPLOAD_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 画像アップロード先ディレクトリ
# Directory for uploaded images
UPLOAD_IMG_DIR = UPLOAD_BASE / "image"

# 画像アップロードURLプレフィックス
# URL prefix for uploaded images
UPLOAD_IMG_URL_PREFIX = "/uploads/image"

# ファイルアップロード先ディレクトリ
# Directory for uploaded files
UPLOAD_FILE_DIR = UPLOAD_BASE / "file"

# ファイルアップロードURLプレフィックス
# URL prefix for uploaded files
UPLOAD_FILE_URL_PREFIX = "/uploads/file"

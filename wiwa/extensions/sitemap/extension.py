# パスとファイル名: wiwa/extensions/sitemap/extension.py
# Path and filename: wiwa/extensions/sitemap/extension.py

# sitemap.xml拡張
# Sitemap.xml extension
#
# 概要
# Summary
#   サイト内のURLを収集し、XML形式のsitemapを生成する
#   Collect site URLs and generate sitemap XML
#
# URL
# URL
#   /sitemap.xml
#
# 処理の流れ
# Flow
#   1. ルート登録
#      Register route
#   2. 静的ページ収集
#      Collect static pages
#   3. 投稿URL収集
#      Collect post URLs
#   4. 固定ページURL収集
#      Collect page URLs
#   5. XML生成
#      Build XML
#   6. レスポンス返却
#      Return response

from pathlib import Path
from xml.sax.saxutils import escape

from wiwa.config import SITE_URL
from wiwa.core.resolver import Resolver
from wiwa.core.response import Response
from wiwa.db.mongo import get_collection
from wiwa.db.post_repository import PostRepository


# 除外するトップレベルディレクトリ
# Excluded top-level directories
EXCLUDED_TOP_LEVEL_DIRS = {
    "admin",
    "auth",
}

# 除外する末尾パーツ
# Excluded last parts
EXCLUDED_LAST_PARTS = {
    "edit",
    "update",
    "delete",
    "create",
    "store",
    "login",
    "logout",
}


def register():
    """
    ルート登録
    Register extension route
    """
    return {
        "routes": [
            {
                "url": "/sitemap.xml",
                "method": "GET",
                "handler": "wiwa.extensions.sitemap.extension.index",
                "auth_required": False,
                "roles": [],
            }
        ]
    }


def get_controllers_dir() -> Path:
    """
    controllersディレクトリ取得
    Get controllers directory
    """
    return Path(__file__).resolve().parents[2] / "controllers"


def normalize_url_from_controller_path(path: Path, controllers_dir: Path) -> str | None:
    """
    controllerパスからURL生成
    Convert controller path to URL
    """
    if path.name == "__init__.py":
        return None

    relative = path.relative_to(controllers_dir)
    parts = list(relative.with_suffix("").parts)

    if not parts:
        return None

    if parts[0] in EXCLUDED_TOP_LEVEL_DIRS:
        return None

    if parts[-1] == "index":
        parts = parts[:-1]

    if parts and parts[-1] in EXCLUDED_LAST_PARTS:
        return None

    if not parts:
        return "/"

    return "/" + "/".join(parts)


def is_public_static_page(url: str, resolver: Resolver) -> bool:
    """
    公開静的ページ判定
    Check if public static page
    """
    resolved = resolver.resolve(url, "GET")
    if resolved is None:
        return False

    if resolved.get("auth_required"):
        return False

    params = resolved.get("params", {})
    if params:
        return False

    return True


def list_static_urls() -> list[str]:
    """
    静的URL一覧取得
    Collect static URLs
    """
    controllers_dir = get_controllers_dir()
    resolver = Resolver()
    urls = {"/", "/post"}

    for path in controllers_dir.rglob("*.py"):
        url = normalize_url_from_controller_path(path, controllers_dir)
        if not url:
            continue

        if is_public_static_page(url, resolver):
            urls.add(url)

    return sorted(urls)


def build_absolute_url(path: str) -> str:
    """
    絶対URL生成
    Build absolute URL
    """
    if path == "/":
        return f"{SITE_URL}/"
    return f"{SITE_URL}{path}"


def format_lastmod(value) -> str:
    """
    lastmodフォーマット
    Format lastmod value
    """
    if not value:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")

    return ""


def list_post_urls() -> list[dict]:
    """
    投稿URL一覧取得
    Collect post URLs
    """
    post_repo = PostRepository()
    posts = post_repo.list_published(limit=10000, skip=0)

    items = []

    for post in posts:
        slug = (post.get("slug") or "").strip()
        if not slug:
            continue

        updated_at = (
            post.get("updated_at")
            or post.get("published_at")
            or post.get("created_at")
        )

        items.append({
            "loc": f"{SITE_URL}/post/{slug}",
            "lastmod": format_lastmod(updated_at),
        })

    return items


def list_page_urls() -> list[dict]:
    """
    固定ページURL一覧取得
    Collect page URLs
    """
    pages = (
        get_collection("pages")
        .find({"status": "published"})
        .sort("updated_at", -1)
    )

    items = []

    for page in pages:
        slug = (page.get("slug") or "").strip()
        if not slug:
            continue

        updated_at = (
            page.get("updated_at")
            or page.get("published_at")
            or page.get("created_at")
        )

        items.append({
            "loc": f"{SITE_URL}/{slug}",
            "lastmod": format_lastmod(updated_at),
        })

    return items


def append_url(xml_lines: list[str], loc: str, lastmod: str = ""):
    """
    URL要素追加
    Append URL element
    """
    xml_lines.append("  <url>")
    xml_lines.append(f"    <loc>{escape(loc)}</loc>")
    if lastmod:
        xml_lines.append(f"    <lastmod>{lastmod}</lastmod>")
    xml_lines.append("  </url>")


def index(request, route=None, **params):
    """
    sitemap.xml生成
    Generate sitemap XML
    """
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # 静的ページ
    # Static pages
    for path in list_static_urls():
        append_url(xml_lines, build_absolute_url(path))

    # 投稿ページ
    # Post pages
    for item in list_post_urls():
        append_url(xml_lines, item["loc"], item["lastmod"])

    # 固定ページ
    # Page URLs
    for item in list_page_urls():
        append_url(xml_lines, item["loc"], item["lastmod"])

    xml_lines.append("</urlset>")

    body = "\n".join(xml_lines)

    return Response(
        body=body,
        status="200 OK",
        headers=[
            ("Content-Type", "application/xml; charset=UTF-8"),
        ],
    )
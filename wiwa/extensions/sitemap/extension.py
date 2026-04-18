# パスとファイル名: wiwa/extensions/sitemap/extension.py
from pathlib import Path
from xml.sax.saxutils import escape

from wiwa.config import SITE_URL
from wiwa.core.resolver import Resolver
from wiwa.core.response import Response
from wiwa.db.post_repository import PostRepository


EXCLUDED_TOP_LEVEL_DIRS = {
    "admin",
    "auth",
}

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
    return Path(__file__).resolve().parents[2] / "controllers"


def normalize_url_from_controller_path(path: Path, controllers_dir: Path) -> str | None:
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
    if path == "/":
        return f"{SITE_URL}/"
    return f"{SITE_URL}{path}"


def list_post_urls() -> list[dict]:
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
            "lastmod": updated_at.strftime("%Y-%m-%d") if updated_at else "",
        })

    return items


def index(request, route=None, **params):
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # 固定ページ
    for path in list_static_urls():
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{escape(build_absolute_url(path))}</loc>")
        xml_lines.append("  </url>")

    # 投稿ページ
    for item in list_post_urls():
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{escape(item['loc'])}</loc>")
        if item["lastmod"]:
            xml_lines.append(f"    <lastmod>{item['lastmod']}</lastmod>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    body = "\n".join(xml_lines)

    return Response(
        body=body,
        status="200 OK",
        headers=[
            ("Content-Type", "application/xml; charset=UTF-8"),
        ],
    )
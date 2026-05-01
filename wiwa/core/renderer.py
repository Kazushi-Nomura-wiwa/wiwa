# パスとファイル名: wiwa/core/renderer.py
# Path and filename: wiwa/core/renderer.py

# テンプレートレンダラー
# Template rendering utility
#
# 概要
# Summary
#   Jinja2を使用してテンプレートを描画し、共通コンテキストを付与する
#   Render templates using Jinja2 and inject common context
#
# 処理の流れ
# Flow
#   1. テンプレート環境初期化
#      Initialize template environment
#   2. t()をグローバル登録
#      Register t() globally
#   3. コンテキスト構築
#      Build render context
#   4. テンプレート描画
#      Render template

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from wiwa.config import ACTIVE_THEME, SITE_NAME, TEMPLATE_BASE
from wiwa.core.i18n import t
from wiwa.types.route import Route


class TemplateRenderer:
    def __init__(self):
        """
        テンプレートレンダラーを初期化
        Initialize template renderer
        """
        self.base_dir = Path(TEMPLATE_BASE)
        self.env = Environment(
            loader=FileSystemLoader(str(self.base_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Jinja2からt()を使えるようにする
        # Make t() available in Jinja2 templates
        self.env.globals["t"] = t

    def render(
        self,
        template_name: str,
        context: dict | None = None,
        request=None,
    ) -> str:
        """
        テンプレートを描画
        Render template
        """
        render_context = dict(context or {})

        # 共通コンテキスト設定
        # Set common context
        render_context["current_user"] = getattr(request, "user", None)
        render_context["active_theme"] = ACTIVE_THEME
        render_context["site_name"] = SITE_NAME
        render_context["csrf_token"] = None

        # CSRFトークン設定
        # Set CSRF token if available
        if request and getattr(request, "user", None):
            render_context["csrf_token"] = request.user.get("csrf_token")

        template = self.env.get_template(template_name)
        return template.render(**render_context)

    def render_route(
        self,
        route: Route | None,
        default_template: str,
        context: dict | None = None,
        request=None,
    ) -> str:
        """
        ルートに応じたテンプレートを描画
        Render template based on route
        """

        # テンプレート名決定
        # Determine template name
        template_name = (route or {}).get("template", default_template)

        return self.render(
            template_name,
            context,
            request=request,
        )
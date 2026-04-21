# パスとファイル名: wiwa/core/renderer.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from wiwa.config import ACTIVE_THEME, TEMPLATE_BASE


class TemplateRenderer:
    def __init__(self):
        self.base_dir = Path(TEMPLATE_BASE)
        self.env = Environment(
            loader=FileSystemLoader(str(self.base_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(
        self,
        template_name: str,
        context: dict | None = None,
        request=None,
    ) -> str:
        render_context = dict(context or {})
        render_context["current_user"] = getattr(request, "user", None)
        render_context["active_theme"] = ACTIVE_THEME
        render_context["csrf_token"] = None

        if request and getattr(request, "user", None):
            render_context["csrf_token"] = request.user.get("csrf_token")

        template = self.env.get_template(template_name)
        return template.render(**render_context)
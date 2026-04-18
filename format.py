# パスとファイル名: format.py
import json

from wiwa.config import ROUTES_JSON_PATH, SETTINGS_JSON_PATH
from wiwa.core.security import hash_password
from wiwa.db.route_repository import RouteRepository
from wiwa.db.settings_repository import SettingsRepository
from wiwa.db.users_repository import UsersRepository


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_routes() -> None:
    route_repository = RouteRepository()
    routes = load_json(ROUTES_JSON_PATH)

    if not isinstance(routes, list):
        raise ValueError("routes.json は配列である必要があります。")

    for route in routes:
        route_data = dict(route)
        route_data["method"] = route_data.get("method", "GET").upper()
        route_data["enabled"] = route_data.get("enabled", True)
        route_data["auth_required"] = route_data.get("auth_required", False)

        route_repository.upsert_route(route_data)

    print(f"[OK] routes seeded: {len(routes)}")


def seed_settings() -> None:
    settings_repository = SettingsRepository()
    settings = load_json(SETTINGS_JSON_PATH)

    if not settings:
        settings_repository.ensure_defaults()
        print("[OK] settings default ensured")
        return

    if isinstance(settings, dict):
        for key, value in settings.items():
            settings_repository.set(key, value)

        print(f"[OK] settings seeded: {len(settings)}")
        return

    if isinstance(settings, list):
        count = 0

        for row in settings:
            if not isinstance(row, dict):
                continue

            key = row.get("key")
            if not key:
                continue

            settings_repository.set(key, row.get("value"))
            count += 1

        settings_repository.ensure_defaults()
        print(f"[OK] settings seeded: {count}")
        return

    raise ValueError("settings.json は dict か list である必要があります。")


def seed_admin_user() -> None:
    users_repository = UsersRepository()

    if users_repository.has_admin():
        print("[SKIP] admin user already exists")
        return

    username = "admin"
    password = "admin1234"

    users_repository.create(
        username=username,
        password_hash=hash_password(password),
        role="admin",
    )

    print("[OK] default admin user created")
    print(f"[INFO] username={username} password={password}")


def main() -> None:
    seed_routes()
    seed_settings()
    seed_admin_user()
    print("[DONE] format completed")


if __name__ == "__main__":
    main()
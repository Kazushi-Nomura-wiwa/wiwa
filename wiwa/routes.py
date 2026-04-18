# パスとファイル名: wiwa/routes.py
from wiwa.controllers import admin, login, logout

ROUTES = {
    ("GET", "/login"): {
        "handler": login.index,
        "auth_required": False,
        "roles": [],
        "params": {},
    },
    ("POST", "/login"): {
        "handler": login.index,
        "auth_required": False,
        "roles": [],
        "params": {},
    },
    ("GET", "/logout"): {
        "handler": logout.index,
        "auth_required": True,
        "roles": ["admin", "editor"],
        "params": {},
    },
    ("GET", "/admin"): {
        "handler": admin.index,
        "auth_required": True,
        "roles": ["admin", "editor"],
        "params": {},
    },
    ("GET", "/admin/users"): {
        "handler": admin.users,
        "auth_required": True,
        "roles": ["admin"],
        "params": {},
    },
}
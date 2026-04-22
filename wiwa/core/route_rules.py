# パスとファイル名: wiwa/core/route_rules.py

from pathlib import Path


DYNAMIC_NAMES = {"_id", "id", "slug", "name", "query"}


def split_path(path: str) -> list[str]:
    return [part for part in path.strip("/").split("/") if part]


def is_dynamic_segment(name: str) -> bool:
    return name in DYNAMIC_NAMES


def module_path_to_url_parts(module_path: str, base_package: str = "wiwa.controllers") -> list[str]:
    if not module_path.startswith(base_package):
        raise ValueError(f"Unexpected module path: {module_path}")

    relative = module_path.removeprefix(base_package).strip(".")
    if not relative:
        return []

    return relative.split(".")


def build_url_path(module_path: str, function_name: str, base_package: str = "wiwa.controllers") -> str:
    parts = module_path_to_url_parts(module_path, base_package=base_package)

    if function_name == "index":
        return "/" + "/".join(parts) if parts else "/"

    return "/" + "/".join(parts + [function_name])


def normalize_route_path(path: str) -> str:
    if not path or path == "":
        return "/"
    if not path.startswith("/"):
        path = "/" + path
    return path


def guess_params_from_function_name(function_name: str) -> list[str]:
    if function_name in DYNAMIC_NAMES:
        return [function_name]
    return []


def build_route_info(module_path: str, function_name: str, methods: list[str] | None = None) -> dict:
    path = build_url_path(module_path, function_name)
    params = guess_params_from_function_name(function_name)

    return {
        "path": normalize_route_path(path),
        "module": module_path,
        "function": function_name,
        "methods": methods or ["GET"],
        "params": params,
    }
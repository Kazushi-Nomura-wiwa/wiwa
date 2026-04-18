# パスとファイル名: wiwa/utils/localtime.py
from datetime import UTC

from wiwa.config import TIMEZONE


def to_localtime(value):
    if not value:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)

    return value.astimezone(TIMEZONE)


def to_localtime_string(value, fmt="%Y-%m-%d %H:%M:%S"):
    local = to_localtime(value)
    if not local:
        return ""
    return local.strftime(fmt)
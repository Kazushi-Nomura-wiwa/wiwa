# パスとファイル名: wiwa/db/indexes.py
from pymongo import ASCENDING
from wiwa.config import ACCESS_LOG_RETENTION_DAYS


def ensure_indexes(db):
    # sessions（TTL: セッション期限）
    db.sessions.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,
        name="ttl_sessions_expires_at",
    )

    # access_logs（TTL: 保持日数分）
    db.access_logs.create_index(
        [("created_at", ASCENDING)],
        expireAfterSeconds=60 * 60 * 24 * ACCESS_LOG_RETENTION_DAYS,
    )

    # users（username一意）
    db.users.create_index(
        [("username", ASCENDING)],
        unique=True,
    )

    # posts（slug一意）
    db.posts.create_index(
        [("slug", ASCENDING)],
        unique=True,
    )

    # trash（purge_at 到達で削除）
    db.posts.create_index(
        [("purge_at", ASCENDING)],
        expireAfterSeconds=0,
    )
# パスとファイル名: wiwa/db/indexes.py
from pymongo import ASCENDING
from wiwa.config import ACCESS_LOG_RETENTION_DAYS

def ensure_indexes(db):
    # sessions（TTL）
    db.sessions.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,
    )

    # access_logs（TTL）
    db.access_logs.create_index(
        [("created_at", ASCENDING)],
        expireAfterSeconds=60 * 60 * 24 * ACCESS_LOG_RETENTION_DAYS,
    )

    # users
    db.users.create_index(
        [("username", ASCENDING)],
        unique=True,
    )

    # posts slug
    db.posts.create_index(
        [("slug", ASCENDING)],
        unique=True,
    )

    # posts trash TTL
    db.posts.create_index(
        [("purge_at", ASCENDING)],
        expireAfterSeconds=0,
    )
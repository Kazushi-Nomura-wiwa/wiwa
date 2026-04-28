# パスとファイル名: wiwa/db/indexes.py
# Path and filename: wiwa/db/indexes.py

# インデックス管理ユーティリティ
# Index management utility
#
# 概要
# Summary
#   MongoDBの各コレクションに必要なインデックスを作成する
#   Create required indexes for MongoDB collections
#
# 処理の流れ
# Flow
#   1. sessionsインデックス作成
#      Create sessions indexes
#   2. access_logsインデックス作成
#      Create access_logs indexes
#   3. usersインデックス作成
#      Create users indexes
#   4. postsインデックス作成
#      Create posts indexes

from pymongo import ASCENDING
from wiwa.config import ACCESS_LOG_RETENTION_DAYS


def ensure_indexes(db):
    """
    インデックス作成
    Ensure indexes
    """

    # sessions（TTL: セッション期限）
    # Sessions TTL index (expires_at)
    db.sessions.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,
        name="ttl_sessions_expires_at",
    )

    # access_logs（TTL: 保持日数分）
    # Access logs TTL index (retention period)
    db.access_logs.create_index(
        [("created_at", ASCENDING)],
        expireAfterSeconds=60 * 60 * 24 * ACCESS_LOG_RETENTION_DAYS,
    )

    # users（username一意）
    # Users unique index (username)
    db.users.create_index(
        [("username", ASCENDING)],
        unique=True,
        name="uniq_users_username",
    )

    # posts（slug一意）
    # Posts unique index (slug)
    db.posts.create_index(
        [("slug", ASCENDING)],
        unique=True,
        name="uniq_posts_slug",
    )

    # trash（purge_at 到達で削除）
    # Posts TTL index (purge_at)
    db.posts.create_index(
        [("purge_at", ASCENDING)],
        expireAfterSeconds=0,
        name="ttl_posts_purge_at",
    )
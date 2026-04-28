# パスとファイル名: wiwa/db/mongo.py
# Path and filename: wiwa/db/mongo.py

# MongoDB接続ユーティリティ
# MongoDB connection utilities
#
# 概要
# Summary
#   MongoDBクライアントとDBインスタンスを管理し、コレクション取得を提供する
#   Manage MongoDB client and database instance, and provide collection access
#
# 処理の流れ
# Flow
#   1. クライアント取得
#      Get MongoDB client
#   2. データベース取得
#      Get database
#   3. コレクション取得
#      Get collection
#   4. インデックス作成
#      Ensure indexes

from pymongo import MongoClient

from wiwa.config import MONGODB_URI, MONGODB_DB_NAME


_client = None
_db = None


def get_client():
    """
    MongoDBクライアント取得
    Get MongoDB client
    """
    global _client

    if _client is None:
        _client = MongoClient(MONGODB_URI)

    return _client


def get_db():
    """
    データベース取得
    Get database instance
    """
    global _db

    if _db is None:
        _db = get_client()[MONGODB_DB_NAME]

    return _db


def get_collection(name: str):
    """
    コレクション取得
    Get collection by name
    """
    return get_db()[name]


def ensure_indexes():
    """
    インデックス作成
    Ensure database indexes
    """
    from wiwa.db import indexes
    indexes.ensure_indexes(get_db())
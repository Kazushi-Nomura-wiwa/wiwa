# パスとファイル名: wiwa/db/mongo.py
from pymongo import MongoClient

from wiwa.config import MONGODB_URI, MONGODB_DB_NAME


_client = None
_db = None


def get_client():
    global _client

    if _client is None:
        _client = MongoClient(MONGODB_URI)

    return _client


def get_db():
    global _db

    if _db is None:
        _db = get_client()[MONGODB_DB_NAME]

    return _db


def get_collection(name: str):
    return get_db()[name]
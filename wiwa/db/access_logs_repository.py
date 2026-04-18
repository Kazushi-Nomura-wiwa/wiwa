# パスとファイル名: wiwa/db/access_logs_repository.py
from datetime import UTC, datetime

from wiwa.db.mongo import get_collection


class AccessLogsRepository:
    def __init__(self):
        self.collection = get_collection("access_logs")
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        indexes = self.collection.index_information()

        created_at_index = indexes.get("created_at_1")
        if created_at_index and "expireAfterSeconds" not in created_at_index:
            self.collection.drop_index("created_at_1")

        self.collection.create_index(
            "created_at",
            expireAfterSeconds=60 * 60 * 24 * 90,
        )
        self.collection.create_index("ip")
        self.collection.create_index("path")
        self.collection.create_index("status_code")

    def create(
        self,
        ip: str,
        method: str,
        path: str,
        query_string: str,
        status_code: int,
        user_agent: str = "",
        referer: str = "",
        host: str = "",
        user_id: str | None = None,
    ) -> None:
        self.collection.insert_one({
            "created_at": datetime.now(UTC),
            "ip": ip,
            "method": method,
            "path": path,
            "query_string": query_string,
            "status_code": status_code,
            "user_agent": user_agent,
            "referer": referer,
            "host": host,
            "user_id": user_id,
        })
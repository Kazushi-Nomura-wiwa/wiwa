# パスとファイル名: wiwa/db/access_logs_repository.py
# Path and filename: wiwa/db/access_logs_repository.py

# アクセスログリポジトリ
# Access logs repository
#
# 概要
# Summary
#   アクセスログの保存とインデックス管理を行う
#   Handle access log storage and index management
#
# 処理の流れ
# Flow
#   1. コレクション取得
#      Get collection
#   2. インデックス確認・作成
#      Ensure indexes
#   3. ログ保存
#      Insert log document

from datetime import UTC, datetime

from wiwa.db.mongo import get_collection


class AccessLogsRepository:
    def __init__(self):
        """
        リポジトリ初期化
        Initialize repository
        """
        self.collection = get_collection("access_logs")
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """
        インデックス確認・作成
        Ensure indexes
        """
        indexes = self.collection.index_information()

        # TTLインデックス再作成（不整合対策）
        # Recreate TTL index if invalid
        created_at_index = indexes.get("created_at_1")
        if created_at_index and "expireAfterSeconds" not in created_at_index:
            self.collection.drop_index("created_at_1")

        # TTLインデックス（90日）
        # TTL index (90 days)
        self.collection.create_index(
            "created_at",
            expireAfterSeconds=60 * 60 * 24 * 90,
        )

        # 検索用インデックス
        # Indexes for queries
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
        """
        アクセスログ保存
        Insert access log
        """
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
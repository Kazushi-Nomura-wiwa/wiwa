# パスとファイル名: wiwa/services/access_log_service.py
# Path and filename: wiwa/services/access_log_service.py

# アクセスログサービス
# Access log service
#
# 概要
# Summary
#   リクエスト情報からアクセスログを生成し、DBへ保存する
#   Build access log from request and store it in database
#
# 処理の流れ
# Flow
#   1. 除外パス判定
#      Check excluded paths
#   2. ユーザーID取得
#      Extract user id
#   3. ログ保存
#      Save log

from wiwa.core.request import Request
from wiwa.db.access_logs_repository import AccessLogsRepository


# アクセスログリポジトリ
# Access logs repository
access_logs = AccessLogsRepository()


def save_access_log(request: Request, status_code: int) -> None:
    """
    アクセスログ保存
    Save access log
    """

    # 静的ファイルは除外
    # Skip static files
    if request.path.startswith("/static/"):
        return

    # ユーザーID取得
    # Extract user id
    user_id = None

    if request.user:
        raw_user_id = request.user.get("_id")
        if raw_user_id:
            user_id = str(raw_user_id)

    # ログ保存
    # Save log
    access_logs.create(
        ip=request.remote_addr,
        method=request.method,
        path=request.path,
        query_string=request.query_string,
        status_code=status_code,
        user_agent=request.user_agent,
        referer=request.referer,
        host=request.host,
        user_id=user_id,
    )
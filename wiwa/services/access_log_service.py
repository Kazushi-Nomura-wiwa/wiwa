# パスとファイル名: wiwa/services/access_log_service.py
from wiwa.core.request import Request
from wiwa.db.access_logs_repository import AccessLogsRepository

access_logs = AccessLogsRepository()


def save_access_log(request: Request, status_code: int) -> None:
    if request.path.startswith("/static/"):
        return

    user_id = None
    if request.user:
        raw_user_id = request.user.get("_id")
        if raw_user_id:
            user_id = str(raw_user_id)

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
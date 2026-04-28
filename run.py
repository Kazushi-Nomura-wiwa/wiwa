# パスとファイル名: run.py

# WiWAアプリケーションのエントリーポイント
# Entry point for the WiWA application
#
# Usage:
#   python run.py
#
# Note:
#   このファイルは最小構成を維持する
#   Keep this file minimal by design

# サーバー起動関数をインポート
# Import the server runner
from wiwa.server import run


# スクリプトとして実行された場合のみサーバーを起動
# Start server only when executed as a script
if __name__ == "__main__":
    run()
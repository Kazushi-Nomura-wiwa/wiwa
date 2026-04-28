# パスとファイル名: script/create_admin.py

# 管理者ユーザーをCLIから作成するスクリプト
# CLI script to create an admin user

import getpass  # パスワード入力を非表示にする / Hide password input
import sys      # プロセス終了やパス操作に使用 / For exit and path handling
from pathlib import Path  # パス操作を扱う / Handle filesystem paths


# プロジェクトルートを取得（このファイルの2階層上）
# Get project root (two levels above this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pythonのモジュール検索パスにプロジェクトルートを追加
# Add project root to Python module search path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# パスワードハッシュ化関数
# Password hashing function
from wiwa.core.password import hash_password

# ユーザーリポジトリ（DB操作）
# User repository for database operations
from wiwa.db.users_repository import UsersRepository

# i18n翻訳関数
# i18n translation function
from wiwa.core.i18n import t


def main():
    """
    管理者ユーザーを作成する
    Create a new admin user

    Flow:
        1. 入力受付 / Receive input
        2. パスワード確認 / Confirm password
        3. ハッシュ化 / Hash password
        4. DB保存 / Save to database
    """

    # ユーザーリポジトリを初期化
    # Initialize user repository
    repo = UsersRepository()

    # ヘッダー表示
    # Display header
    print(t("create_admin_title"))
    print("----------------------")

    # ユーザー情報の入力
    # Receive user input
    username = input("username: ").strip()
    email = input("email: ").strip().lower()
    display_name = input("display_name: ").strip()

    # パスワード入力（非表示）
    # Input password (hidden)
    password = getpass.getpass("password: ").strip()
    password_confirm = getpass.getpass("password(confirm): ").strip()

    # パスワード一致チェック
    # Validate password confirmation
    if password != password_confirm:
        print(t("password_mismatch"))
        sys.exit(1)

    # display_name未入力時はusernameを使用
    # Use username if display_name is empty
    if not display_name:
        display_name = username

    try:
        # パスワードをハッシュ化
        # Hash the password
        password_hash = hash_password(password)

        # 管理者ユーザーを作成
        # Create admin user in database
        inserted_id = repo.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role="admin",
            display_name=display_name,
            is_active=True,
        )

        # 成功メッセージ
        # Success message
        print("")
        print(t("admin_created"))
        print(f"user_id: {inserted_id}")
        print(f"username: {username}")
        print("role: admin")

    except Exception as e:
        # エラーハンドリング
        # Error handling
        print(f"{t('error_prefix')}: {e}")
        sys.exit(1)


# スクリプトとして実行された場合のみmainを呼ぶ
# Execute main only when run as script
if __name__ == "__main__":
    main()
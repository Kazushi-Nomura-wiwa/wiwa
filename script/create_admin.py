# パスとファイル名: script/create_admin.py
# Path and filename: script/create_admin.py

# 管理者ユーザー作成CLIスクリプト
# CLI script to create an admin user
#
# 概要
# Summary
#   対話形式で管理者ユーザーを作成する
#   Create an admin user via interactive CLI
#
# 処理の流れ
# Flow
#   1. 入力受付
#      Receive input
#   2. パスワード確認
#      Confirm password
#   3. ハッシュ化
#      Hash password
#   4. DB保存
#      Save to database

import getpass
import sys
from pathlib import Path


# プロジェクトルートを取得
# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pythonのモジュール検索パスに追加
# Add project root to sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# モジュール読み込み
# Import modules
from wiwa.core.password import hash_password
from wiwa.db.users_repository import UsersRepository
from wiwa.core.i18n import t


def main():
    """
    管理者ユーザーを作成
    Create an admin user
    """

    repo = UsersRepository()

    # ヘッダー表示
    # Display header
    print(t("create_admin_title"))
    print("----------------------")

    # 入力受付
    # Receive input
    username = input(f"{t('input_username')}: ").strip()
    email = input(f"{t('input_email')}: ").strip().lower()
    display_name = input(f"{t('input_display_name')}: ").strip()

    # パスワード入力（非表示）
    # Input password (hidden)
    password = getpass.getpass(f"{t('input_password')}: ").strip()
    password_confirm = getpass.getpass(f"{t('input_password_confirm')}: ").strip()

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
        # パスワードハッシュ化
        # Hash password
        password_hash = hash_password(password)

        # ユーザー作成
        # Create user
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
        # エラー表示
        # Error handling
        print(f"{t('error_prefix')}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
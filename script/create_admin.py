# パスとファイル名: script/create_admin.py
import getpass
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from wiwa.core.password import hash_password
from wiwa.db.users_repository import UsersRepository


def main():
    repo = UsersRepository()

    print("WiWA 管理者ユーザー作成")
    print("----------------------")

    username = input("username: ").strip()
    email = input("email: ").strip().lower()
    display_name = input("display_name: ").strip()

    password = getpass.getpass("password: ").strip()
    password_confirm = getpass.getpass("password(confirm): ").strip()

    if password != password_confirm:
        print("エラー: パスワードが一致しません。")
        sys.exit(1)

    if not display_name:
        display_name = username

    try:
        password_hash = hash_password(password)

        inserted_id = repo.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role="admin",
            display_name=display_name,
            is_active=True,
        )

        print("")
        print("管理者ユーザーを作成しました。")
        print(f"user_id: {inserted_id}")
        print(f"username: {username}")
        print("role: admin")

    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
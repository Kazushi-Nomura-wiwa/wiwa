# WiWA

No magic. Just code.()
One path. One route. One truth.

Pythonが書ければ、そのまま運用・拡張できるCMSです。
A CMS you can run and extend as-is, if you can write Python.

---

## 要件 / Requirements

### 対応環境 / Environment

* Ubuntu 24.04（推奨）
  Ubuntu 24.04 (recommended)

* Python 3.12 以上
  Python 3.12+

---

## セットアップ / Setup

### 必須パッケージ / Required packages

```bash id="g3sfq9"
sudo apt update
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    libmagic1
```

---

### 推奨パッケージ / Recommended packages

```bash id="l8n7kq"
sudo apt install -y \
    nginx \
    git
```

---

## MongoDB のインストール / Install MongoDB

WiWAはMongoDBを使用します。
WiWA uses MongoDB.

### リポジトリ追加 / Add repository

```bash id="c1q5yx"
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
```

```bash id="y3k9ah"
echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] \
https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/7.0 multiverse" | \
    sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

---

### インストール / Install

```bash id="3nq1k9"
sudo apt update
sudo apt install -y mongodb-org
```

---

### 起動 / Start

```bash id="2r7jpw"
sudo systemctl start mongod
sudo systemctl enable mongod
```

---

### 確認 / Verify

```bash id="j8m4wv"
mongosh
```

---

## プロジェクトセットアップ / Project setup

### クローン / Clone

```bash id="q1y8vh"
git clone https://github.com/your-repo/wiwa.git
cd wiwa
```

---

### 仮想環境 / Virtual environment

```bash id="y9c2kx"
python3 -m venv venv
source venv/bin/activate
```

---

### Pythonパッケージ / Python packages

```bash id="t6w9oz"
pip install -r requirements.txt
```

---

## 起動 / Run

```bash id="k2d8qs"
python run.py
```

---

## アクセス / Access

```txt id="z8r4hp"
http://127.0.0.1:8000
```

---

## 管理機能 / Admin

```txt id="b7y6lo"
/admin
/mypage
```

---

## ファイルアップロード / File upload

* admin / author のみアップロード可能
  Only admin / author can upload

* 対応形式 / Allowed MIME

```txt id="y5n2rx"
image/png
image/jpeg
image/webp
image/gif
application/pdf
```

* 保存先 / Storage

```txt id="r8k3jp"
/uploads/file/
```

---

## 設計思想 / Philosophy

* No magic. Just code.()
* URLと処理は1対1
  One URL maps to one handler
* Pythonが書ければ理解できる
  If you can write Python, you can understand everything
* ソースコードがそのままドキュメント
  The source code is the documentation

---

## 注意事項 / Notes

* SVGはセキュリティ上禁止
  SVG is disabled for security reasons

* 大容量ファイルは対象外
  Large files (video, zip, etc.) are out of scope

* サイズ制限あり（config.py参照）
  File size limits are defined in config.py

---

## ライセンス / License

MIT License

# Nsystem デプロイガイド

## 概要
このガイドでは、WSL上で動作確認済みのDjangoアプリケーション「Nsystem」を本番環境にデプロイする手順を説明します。

## デプロイオプション

### 1. Linux VPS（推奨）
Ubuntu/Debian系のVPSを使用した本番デプロイ

#### 必要な環境
- Ubuntu 20.04 LTS以上 または Debian 11以上
- Python 3.8以上
- nginx
- gunicorn または uWSGI
- systemd（サービス管理用）

#### デプロイ手順

##### 1.1 サーバー準備
```bash
# システムパッケージの更新
sudo apt update && sudo apt upgrade -y

# 必要なパッケージのインストール
sudo apt install -y python3-pip python3-venv nginx git

# MS SQL Serverドライバーのインストール（必要な場合）
sudo apt install -y unixodbc-dev
```

##### 1.2 アプリケーションのセットアップ
```bash
# アプリケーション用ディレクトリの作成
sudo mkdir -p /opt/nsystem
cd /opt/nsystem

# コードのデプロイ（GitまたはSCPで転送）
# 例: git clone [リポジトリURL] .
# または: scp -r local/path/* user@server:/opt/nsystem/

# 仮想環境の作成とアクティベート
python3 -m venv venv
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
pip install gunicorn

# 環境変数の設定（.envファイルを作成）
cat > .env << EOF
DEBUG=False
SECRET_KEY=本番用の安全なシークレットキー
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
DATABASE_PORT=1433
EOF

# 静的ファイルの収集
python manage.py collectstatic --noinput

# データベースマイグレーション
python manage.py migrate
```

##### 1.3 Gunicornの設定
```bash
# Gunicornサービスファイルの作成
sudo nano /etc/systemd/system/nsystem.service
```

内容:
```ini
[Unit]
Description=Nsystem Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/nsystem
Environment="PATH=/opt/nsystem/venv/bin"
ExecStart=/opt/nsystem/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/nsystem/nsystem.sock \
    nimura_subsystems.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# サービスの有効化と起動
sudo systemctl daemon-reload
sudo systemctl enable nsystem
sudo systemctl start nsystem
```

##### 1.4 Nginxの設定
```bash
sudo nano /etc/nginx/sites-available/nsystem
```

内容:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /opt/nsystem;
    }
    
    location /media/ {
        root /opt/nsystem;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/nsystem/nsystem.sock;
    }
}
```

```bash
# サイトの有効化
sudo ln -s /etc/nginx/sites-available/nsystem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

##### 1.5 SSL証明書の設定（Let's Encrypt）
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### 2. Dockerデプロイ

#### Dockerfileの作成
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "nimura_subsystems.wsgi:application"]
```

#### docker-compose.ymlの作成
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - DATABASE_HOST=${DATABASE_HOST}
      - DATABASE_PORT=${DATABASE_PORT}
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
```

#### デプロイ実行
```bash
docker-compose up -d --build
```

---

### 3. クラウドプラットフォーム

#### 3.1 AWS Elastic Beanstalk
```bash
# EB CLIのインストール
pip install awsebcli

# 初期設定
eb init -p python-3.9 nsystem-app

# 環境の作成とデプロイ
eb create nsystem-env
eb deploy
```

#### 3.2 Google Cloud Platform (App Engine)
app.yamlファイルの作成:
```yaml
runtime: python39

env_variables:
  DEBUG: "False"
  SECRET_KEY: "your-secret-key"

handlers:
- url: /static
  static_dir: static/
- url: /.*
  script: auto
```

デプロイ:
```bash
gcloud app deploy
```

#### 3.3 Heroku
Procfileの作成:
```
web: gunicorn nimura_subsystems.wsgi
```

デプロイ:
```bash
heroku create nsystem-app
heroku config:set SECRET_KEY="your-secret-key"
git push heroku main
heroku run python manage.py migrate
```

---

## セキュリティ設定

### 本番環境のsettings.py調整
```python
# nimura_subsystems/settings.py の本番用設定

import os
from dotenv import load_dotenv

load_dotenv()

# セキュリティ設定
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# HTTPS設定
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# 静的ファイル設定
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## デプロイ前チェックリスト

- [ ] DEBUG=Falseに設定
- [ ] SECRET_KEYを安全な値に変更
- [ ] ALLOWED_HOSTSに本番ドメインを設定
- [ ] データベース接続情報を本番用に更新
- [ ] 静的ファイルを収集（collectstatic）
- [ ] データベースマイグレーション完了
- [ ] SSL証明書の設定
- [ ] ファイアウォール設定（80, 443ポートのみ開放）
- [ ] バックアップ設定
- [ ] ログ設定とモニタリング

---

## トラブルシューティング

### よくある問題と解決方法

1. **静的ファイルが表示されない**
   - `python manage.py collectstatic`を実行
   - Nginx設定で静的ファイルパスを確認

2. **データベース接続エラー**
   - ファイアウォール設定を確認
   - データベースサーバーのリモート接続許可を確認
   - 接続文字列とポート番号を確認

3. **500エラーが発生**
   - ログファイルを確認: `/var/log/nginx/error.log`
   - Djangoログを確認
   - `DEBUG=True`で一時的にデバッグ情報を表示

4. **パフォーマンスが遅い**
   - Gunicornのワーカー数を調整
   - データベースインデックスを最適化
   - キャッシュ（Redis/Memcached）の導入を検討

---

## 運用・保守

### 定期メンテナンス
- システムパッケージの更新: 月1回
- Pythonパッケージの更新: 脆弱性対応時
- データベースバックアップ: 日次
- ログローテーション設定

### モニタリング推奨ツール
- New Relic
- Datadog
- Prometheus + Grafana
- Sentry（エラートラッキング）

---

## お問い合わせ
デプロイに関する質問や問題がある場合は、プロジェクト管理者にご連絡ください。
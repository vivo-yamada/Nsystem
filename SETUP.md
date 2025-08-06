# Nimura_SubSystems セットアップガイド

## 環境構築手順

### 1. 前提条件
- Python 3.8以上がインストールされていること
- SQL Serverにアクセス可能であること
- ODBC Driver 17 for SQL Serverがインストールされていること

### 2. 仮想環境のセットアップ
```bash
# 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定
1. `.env.example`をコピーして`.env`ファイルを作成
```bash
cp .env.example .env
```

2. `.env`ファイルを編集して、実際の値を設定
```
DB_HOST=your_sql_server_host
DB_PORT=1433
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
NETWORK_DRIVE_PATH=\\\\your_server\\share\\photos
```

### 4. データベース接続の確認
```bash
python manage.py dbshell
```

### 5. 開発サーバーの起動
```bash
python manage.py runserver
```

ブラウザで http://localhost:8000 にアクセス

## トラブルシューティング

### SQL Server接続エラーの場合
- ODBC Driver 17 for SQL Serverがインストールされているか確認
- ファイアウォール設定を確認（ポート1433）
- SQL Server認証が有効になっているか確認

### ネットワークドライブにアクセスできない場合
- Djangoサーバーを実行するユーザーがネットワークドライブへのアクセス権限を持っているか確認
- パスの形式が正しいか確認（バックスラッシュのエスケープに注意）
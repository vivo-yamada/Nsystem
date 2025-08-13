#!/bin/bash

echo "WSL内でDjangoサーバーを起動します..."
echo "仮想環境をアクティベートしてサーバーを起動中..."

# プロジェクトディレクトリに移動
cd /mnt/c/ClaudeCode/APPS/Nsystem

# 仮想環境をアクティベート
source venv/bin/activate

# データベースマイグレーション
echo "マイグレーションを実行中..."
python manage.py migrate

# Djangoサーバーを起動
echo "Djangoサーバーを起動中..."
echo "サーバー起動後は、ブラウザで http://127.0.0.1:8080/ にアクセスしてください"
echo "注意: http://0.0.0.0:8080/ ではなく、http://127.0.0.1:8080/ を使用してください"
python manage.py runserver 0.0.0.0:8080

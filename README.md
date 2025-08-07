# Nimura_SubSystems

製造現場での検査作業支援システム。製作手配書のバーコードから製品情報を読み取り、該当製品の写真をモバイル端末で確認できるWebアプリケーションです。

## 📋 機能概要

- 製品コード検索による画像一覧表示
- モバイル対応レスポンシブデザイン
- 画像の拡大表示とナビゲーション機能
- 既存SQL Serverデータベースとの連携

## 🚀 クイックスタート

### 1. 環境設定
```bash
# 仮想環境の有効化
source venv/bin/activate

# 環境変数ファイルの作成
cp .env.example .env
# .envファイルを編集してデータベース接続情報を設定
```

### 2. 開発サーバーの起動
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. アクセス
- トップページ: http://localhost:8000/
- 検索テスト: http://localhost:8000/search/?product_code=005062

## 🛠️ 開発・保守用スクリプト

### データベース接続確認
```bash
# SQL Server基本接続テスト
python database_connection_test.py

# Django経由でのデータベース動作確認
python verify_database.py
```

### システム動作確認
```bash
# パス変換機能の確認
python verify_paths.py
```

### テストデータ管理
```bash
# テスト用画像の作成
python tools/create_test_images.py

# テストデータの更新
python tools/update_test_data.py
```

## 📁 プロジェクト構造

```
Nsystem/
├── manage.py                    # Django管理コマンド
├── requirements.txt             # 依存関係
├── requirements_document.md     # 要件定義書
├── SETUP.md                    # 環境構築手順
├── .env.example                # 環境変数テンプレート
│
├── nimura_subsystems/          # Djangoプロジェクト設定
│   ├── settings.py             # Django設定
│   ├── urls.py                 # URLルーティング
│   └── db_router.py            # データベースルーター
│
├── product_viewer/             # メインアプリケーション
│   ├── models.py               # データモデル
│   ├── services.py             # ビジネスロジック
│   ├── views.py                # ビューロジック
│   ├── urls.py                 # URLパターン
│   └── templates/              # HTMLテンプレート
│
├── tools/                      # 開発・保守ツール
│   ├── create_test_images.py   # テスト画像作成
│   └── update_test_data.py     # テストデータ更新
│
├── database_connection_test.py  # DB接続テスト
├── verify_database.py          # データ取得確認
└── verify_paths.py             # パス変換確認
```

## 🔧 技術スタック

- **Backend**: Django 4.2.7
- **Database**: SQL Server (pymssql接続)
- **Frontend**: Bootstrap 5 + JavaScript
- **Image Processing**: Pillow

## 📱 対応ブラウザ・デバイス

- デスクトップ: Chrome, Firefox, Edge, Safari
- モバイル: iOS Safari, Android Chrome
- タブレット: iPad, Android タブレット

## 🎯 使用方法

1. 製品コードを入力フォームに入力
2. 検索ボタンをクリック
3. 表示された画像をクリックで拡大表示
4. 拡大表示中は矢印ボタンやキーボード、スワイプで画像切り替え

## 🔍 トラブルシューティング

### データベース接続エラー
```bash
python database_connection_test.py
```
でSQL Server接続を確認してください。

### 画像が表示されない
```bash
python verify_paths.py
```
でパス変換とファイル存在を確認してください。

## 📄 ライセンス

社内システム用プロジェクト
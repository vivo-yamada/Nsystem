# Nsystem IISデプロイ手順書

## 目次
1. [はじめに](#はじめに)
2. [システム要件](#システム要件)
3. [事前準備](#事前準備)
4. [Python環境のセットアップ](#python環境のセットアップ)
5. [IISのインストールと設定](#iisのインストールと設定)
6. [アプリケーションのデプロイ](#アプリケーションのデプロイ)
7. [IISとDjangoの連携設定](#iisとdjangoの連携設定)
8. [データベースと写真データの配置](#データベースと写真データの配置)
9. [動作確認](#動作確認)
10. [トラブルシューティング](#トラブルシューティング)
11. [運用・メンテナンス](#運用メンテナンス)

---

## はじめに

このガイドは、SubSystems製品写真管理システムを社内ネットワークのWindowsサーバー上で、IIS（Internet Information Services）を使用して運用するための手順書です。

### 対象環境
- 社内ネットワーク（インターネット非公開）
- Windows Server（2016/2019/2022）またはWindows 10/11 Pro
- IIS 10.0以降

### このガイドの目的
既存のWindowsサーバーにIISをインストールし、DjangoアプリケーションであるSubSystemsを社内で利用できるように設定します。

---

## システム要件

### 最小要件
- **OS**: Windows Server 2016以降 または Windows 10 Pro以降
- **メモリ**: 4GB以上（推奨8GB）
- **ディスク**: 10GB以上の空き容量（写真データ除く）
- **CPU**: 2コア以上

### 必要なソフトウェア
- Python 3.10以降
- IIS 10.0以降
- wfastcgi（PythonとIISの連携モジュール）
- Microsoft Visual C++ 再頒布可能パッケージ

---

## 事前準備

### 1. 管理者権限の確認
すべての作業は**管理者権限**で実行する必要があります。

### 2. ファイアウォールの設定
社内ネットワークからアクセスできるよう、必要に応じてポートを開放します：
- HTTP: 80番ポート
- HTTPS: 443番ポート（SSL使用時）

### 3. 作業用フォルダの作成
以下のフォルダ構造を作成します：

```
C:\
├── inetpub\
│   └── Nsystem\              # アプリケーション配置場所
├── ProgramData\
│   └── Nsystem\
│       ├── logs\              # ログファイル
│       ├── database\          # データベース
│       └── media\             # アップロードファイル
└── NAS_mount\                 # 製品写真データ
```

コマンドプロンプト（管理者として実行）で作成：

```cmd
mkdir C:\inetpub\Nsystem
mkdir C:\ProgramData\Nsystem
mkdir C:\ProgramData\Nsystem\logs
mkdir C:\ProgramData\Nsystem\database
mkdir C:\ProgramData\Nsystem\media
mkdir C:\NAS_mount
```

---

## Python環境のセットアップ

### 1. Pythonのインストール

1. [Python公式サイト](https://www.python.org/downloads/)から Python 3.10以降をダウンロード
2. インストーラーを管理者として実行
3. **重要**: 「Add Python to PATH」にチェックを入れる
4. 「Install Now」をクリック

### 2. Pythonインストールの確認

コマンドプロンプト（管理者として実行）で確認：

```cmd
python --version
# Python 3.10.x と表示されればOK
```

### 3. 仮想環境の作成

```cmd
cd C:\inetpub\Nsystem
python -m venv venv
```

### 4. 仮想環境の有効化

```cmd
C:\inetpub\Nsystem\venv\Scripts\activate
```

### 5. 必要なパッケージのインストール

```cmd
# 仮想環境が有効な状態で実行
pip install django==4.2.0
pip install pillow==10.0.0
pip install openpyxl==3.1.2
pip install wfastcgi==3.0.0
```

---

## IISのインストールと設定

### 1. IISの有効化

#### Windows Serverの場合：

1. サーバーマネージャーを開く
2. 「役割と機能の追加」をクリック
3. 「役割ベースまたは機能ベースのインストール」を選択
4. 対象サーバーを選択
5. 「Web サーバー (IIS)」にチェック
6. 以下の機能を追加でチェック：
   - Web サーバー → アプリケーション開発 → CGI
   - Web サーバー → パフォーマンス → 動的コンテンツの圧縮
   - Web サーバー → セキュリティ → 要求フィルター
7. インストール

#### Windows 10/11 Proの場合：

1. コントロールパネル → プログラム → Windowsの機能の有効化または無効化
2. 「インターネット インフォメーション サービス」を展開
3. 以下にチェック：
   - Web 管理ツール → IIS 管理コンソール
   - World Wide Web サービス → アプリケーション開発機能 → CGI
   - World Wide Web サービス → HTTP 共通機能（すべて）
4. 「OK」をクリック

### 2. IISの動作確認

ブラウザで `http://localhost` にアクセスし、IISのデフォルトページが表示されることを確認。

---

## アプリケーションのデプロイ

### 1. プロジェクトファイルのコピー

SubSystemsのプロジェクトファイルを `C:\inetpub\Nsystem` にコピー：

```cmd
# 既存のプロジェクトフォルダから必要なファイルをコピー
xcopy /E /I "元のプロジェクトパス\*" "C:\inetpub\Nsystem"
```

### 2. 本番環境用設定ファイルの作成

`C:\inetpub\Nsystem\Nsystem\settings_production.py` を作成：

```python
from .settings import *
import os

# セキュリティ設定
DEBUG = False  # 本番環境では必ずFalse
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'サーバーのIPアドレス', 'サーバーのホスト名']

# 例: ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100', 'SERVER01']

# シークレットキー（必ず変更してください）
SECRET_KEY = 'django-insecure-新しいランダムな文字列をここに設定'

# データベース設定
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': r'C:\ProgramData\Nsystem\database\db.sqlite3',
    }
}

# 静的ファイルの設定
STATIC_URL = '/static/'
STATIC_ROOT = r'C:\inetpub\Nsystem\static'
STATICFILES_DIRS = []

# メディアファイルの設定
MEDIA_URL = '/media/'
MEDIA_ROOT = r'C:\ProgramData\Nsystem\media'

# ログ設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': r'C:\ProgramData\Nsystem\logs\django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# セッション設定（社内利用向け）
SESSION_COOKIE_SECURE = False  # HTTPSを使わない場合
CSRF_COOKIE_SECURE = False     # HTTPSを使わない場合

# ファイルアップロードサイズ制限（必要に応じて調整）
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### 3. 静的ファイルの収集

```cmd
cd C:\inetpub\Nsystem
venv\Scripts\activate
python manage.py collectstatic --noinput --settings=Nsystem.settings_production
```

---

## IISとDjangoの連携設定

### 1. wfastcgiの設定

管理者権限のコマンドプロンプトで実行：

```cmd
cd C:\inetpub\Nsystem
venv\Scripts\activate
wfastcgi-enable
```

表示される設定情報（PYTHONPATH と WSGI_HANDLER）をメモしておく。

### 2. web.configファイルの作成

`C:\inetpub\Nsystem\web.config` を作成：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="Python FastCGI" 
                 path="*" 
                 verb="*" 
                 modules="FastCgiModule" 
                 scriptProcessor="C:\inetpub\Nsystem\venv\Scripts\python.exe|C:\inetpub\Nsystem\venv\Lib\site-packages\wfastcgi.py" 
                 resourceType="Unspecified" 
                 requireAccess="Script" />
        </handlers>
        
        <staticContent>
            <mimeMap fileExtension=".webp" mimeType="image/webp" />
            <mimeMap fileExtension=".woff2" mimeType="font/woff2" />
        </staticContent>
        
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="104857600" />
            </requestFiltering>
        </security>
    </system.webServer>
    
    <appSettings>
        <add key="PYTHONPATH" value="C:\inetpub\Nsystem" />
        <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
        <add key="DJANGO_SETTINGS_MODULE" value="Nsystem.settings_production" />
    </appSettings>
</configuration>
```

### 3. IISサイトの設定

1. IISマネージャーを開く（`inetmgr`を実行）
2. 左側のツリーで「サイト」を右クリック → 「Webサイトの追加」
3. 以下を設定：
   - **サイト名**: Nsystem
   - **物理パス**: C:\inetpub\Nsystem
   - **ポート**: 8080（または任意の空いているポート）
   - **ホスト名**: （空欄でOK）

### 4. アプリケーションプールの設定

1. IISマネージャーで「アプリケーション プール」をクリック
2. 「Nsystem」を右クリック → 「詳細設定」
3. 以下を設定：
   - **32ビットアプリケーションの有効化**: False
   - **マネージド パイプライン モード**: 統合
   - **プロセス ID**: ApplicationPoolIdentity

### 5. フォルダーのアクセス権限設定

```cmd
# IIS_IUSRSにアクセス権限を付与
icacls C:\inetpub\Nsystem /grant "IIS_IUSRS:(OI)(CI)RX"
icacls C:\ProgramData\Nsystem /grant "IIS_IUSRS:(OI)(CI)M"
icacls C:\NAS_mount /grant "IIS_IUSRS:(OI)(CI)RX"
```

---

## データベースと写真データの設定

### 1. SQL Server接続の設定

SQL ServerはWebサーバーと同じ端末にインストールされているため、`settings_production.py`で接続情報を設定：

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost\\SQLEXPRESS',  # または 'localhost,1433'
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

必要に応じてODBCドライバーをインストール：
```cmd
# Microsoft ODBC Driver for SQL Serverのインストール
# https://docs.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### 2. ネットワークドライブへのアクセス設定

写真ファイルは別の端末に保存されており、データベースにそのパス情報が格納されています。
IISがネットワークドライブにアクセスできるように設定が必要です。

#### 方法1: ネットワークドライブのマウント（推奨）

```cmd
# 管理者権限のコマンドプロンプトで実行
# IISサービスアカウント用にネットワークドライブをマウント
net use Z: \\ファイルサーバー\写真フォルダ /persistent:yes
```

#### 方法2: UNCパスの直接使用

IISアプリケーションプールの実行アカウントを、ネットワークドライブにアクセス権限のあるドメインアカウントに変更：

1. IISマネージャーを開く
2. アプリケーションプール → Nsystem → 詳細設定
3. プロセスID → カスタムアカウントを設定
   - ユーザー名: DOMAIN\ServiceAccount
   - パスワード: アカウントのパスワード

### 3. アクセス権限の確認

```cmd
# ネットワークドライブへのアクセス権限を確認
icacls "\\ファイルサーバー\写真フォルダ"

# IISワーカープロセスがアクセスできるか確認
# PowerShellで実行
Test-Path "\\ファイルサーバー\写真フォルダ" -Credential (Get-Credential DOMAIN\ServiceAccount)
```

### 4. パス変換設定の確認

システムはWindows形式のパス（例：`C:\Photos\...`）とUNCパス（例：`\\server\share\...`）の両方に対応しています。
データベースに格納されているパス形式を確認し、必要に応じて`services.py`のパス変換ロジックを調整してください。

---

## 動作確認

### 1. IISサービスの再起動

```cmd
iisreset
```

### 2. アプリケーションへのアクセス

ブラウザで以下にアクセス：
- `http://localhost:8080`（ローカルから）
- `http://サーバーのIPアドレス:8080`（他のPCから）

### 3. 機能確認チェックリスト

- [ ] トップページが表示される
- [ ] バーコード読み取りが機能する
- [ ] 手動検索が機能する
- [ ] 写真が正しく表示される
- [ ] 写真の拡大表示（モーダル）が動作する

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. 「500 Internal Server Error」が表示される

**確認事項：**
- `C:\ProgramData\Nsystem\logs\django_error.log` を確認
- イベントビューアーでIISのエラーログを確認

**解決方法：**
```cmd
# 設定の再確認
cd C:\inetpub\Nsystem
venv\Scripts\activate
python manage.py check --settings=Nsystem.settings_production
```

#### 2. 「403 Forbidden」エラー

**原因：** フォルダーのアクセス権限不足

**解決方法：**
```cmd
# アクセス権限の再設定
icacls C:\inetpub\Nsystem /grant "IIS_IUSRS:(OI)(CI)RX" /T
```

#### 3. 写真が表示されない

**確認事項：**
- 写真ファイルのパスが正しいか確認
- `C:\NAS_mount` フォルダーに写真があるか確認

**解決方法：**
1. IISマネージャーで仮想ディレクトリを追加：
   - サイト「Nsystem」を右クリック → 「仮想ディレクトリの追加」
   - エイリアス: `images`
   - 物理パス: `C:\NAS_mount`

#### 4. 静的ファイル（CSS/JS）が読み込まれない

**解決方法：**
1. IISマネージャーで仮想ディレクトリを追加：
   - エイリアス: `static`
   - 物理パス: `C:\inetpub\Nsystem\static`

#### 5. データベースエラー

**確認事項：**
```cmd
# データベースの存在確認
dir C:\ProgramData\Nsystem\database\db.sqlite3

# 権限確認
icacls C:\ProgramData\Nsystem\database\db.sqlite3
```

### ログファイルの確認

#### Djangoのエラーログ：
```cmd
type C:\ProgramData\Nsystem\logs\django_error.log
```

#### IISのログ：
```cmd
type C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log
```

#### Windowsイベントログ：
1. イベントビューアーを開く（`eventvwr`）
2. Windowsログ → アプリケーション
3. ソース「IIS」のエラーを確認

---

## 運用・メンテナンス

### 定期的なバックアップ

#### バックアップスクリプト（backup.bat）:

```batch
@echo off
set BACKUP_DIR=C:\Backup\Nsystem
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%

echo Nsystemのバックアップを開始します...

REM データベースのバックアップ
mkdir "%BACKUP_DIR%\%DATE%\database" 2>nul
copy "C:\ProgramData\Nsystem\database\db.sqlite3" "%BACKUP_DIR%\%DATE%\database\"

REM 設定ファイルのバックアップ
mkdir "%BACKUP_DIR%\%DATE%\config" 2>nul
xcopy /Y "C:\inetpub\Nsystem\Nsystem\settings*.py" "%BACKUP_DIR%\%DATE%\config\"

echo バックアップが完了しました: %BACKUP_DIR%\%DATE%
pause
```

### アプリケーションの更新手順

1. **IISの停止**
```cmd
iisreset /stop
```

2. **ファイルの更新**
```cmd
# 更新ファイルをコピー
xcopy /Y /E "更新ファイルのパス\*" "C:\inetpub\Nsystem\"
```

3. **静的ファイルの再収集**
```cmd
cd C:\inetpub\Nsystem
venv\Scripts\activate
python manage.py collectstatic --noinput --settings=Nsystem.settings_production
```

4. **IISの再起動**
```cmd
iisreset /start
```

### パフォーマンスの監視

#### パフォーマンスモニターの設定：

1. `perfmon`を実行
2. データコレクターセット → ユーザー定義 → 新規作成
3. 以下のカウンターを追加：
   - Process\% Processor Time (w3wp)
   - Process\Private Bytes (w3wp)
   - Web Service\Current Connections
   - ASP.NET\Requests Current

### セキュリティの推奨事項

#### 社内ネットワーク向けの設定：

1. **IPアドレス制限**（特定のIPからのみアクセス許可）
   - IISマネージャー → サイト → IP アドレスとドメインの制限

2. **Windows認証の有効化**（必要に応じて）
   - IISマネージャー → 認証 → Windows認証を有効化

3. **定期的なWindowsアップデート**
   - 月次でセキュリティパッチを適用

4. **アクセスログの監視**
   - 不審なアクセスパターンがないか定期的に確認

### よく使うコマンド一覧

```cmd
# IISの再起動
iisreset

# アプリケーションプールのリサイクル
%windir%\system32\inetsrv\appcmd recycle apppool /apppool.name:"Nsystem"

# サイトの開始/停止
%windir%\system32\inetsrv\appcmd start site /site.name:"Nsystem"
%windir%\system32\inetsrv\appcmd stop site /site.name:"Nsystem"

# ログの確認
type C:\ProgramData\Nsystem\logs\django_error.log | more
```

---

## 付録: 推奨される構成

### 高可用性構成（オプション）

複数のサーバーで冗長化する場合：

1. **ロードバランサー**の設置
2. **共有ストレージ**（NAS）の利用
3. **データベース**の外部化（SQL Server等）

### SSL証明書の設定（社内CA使用）

社内でHTTPS通信を行う場合：

1. 社内認証局（CA）から証明書を取得
2. IISマネージャーでバインディングを追加
3. HTTPSポート（443）でアクセス可能に設定

---

## サポート連絡先

システムに関する問題が発生した場合は、以下の情報を準備して連絡してください：

- エラーメッセージの詳細
- 発生した操作の手順
- ログファイル（django_error.log）
- スクリーンショット

**このガイドは社内利用を前提としています。外部公開する場合は、追加のセキュリティ対策が必要です。**
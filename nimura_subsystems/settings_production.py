from nimura_subsystems.settings import *
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# セキュリティ設定
DEBUG = False  # 本番環境では必ずFalse
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.19', 'VIVO-PC19']  

# 例: ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100', 'SERVER01']

# シークレットキー（必ず変更してください）
SECRET_KEY = 'django-insecure-adepophjelk'

# データベース設定（SQL Server）
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME', 'your_database_name'),
        'USER': os.getenv('DB_USER', 'your_username'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_password'),
        'HOST': os.getenv('DB_HOST', 'your_server_name'),
        'PORT': '',  # SQL Server Expressは動的ポートを使用
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

# データベースルーター設定
DATABASE_ROUTERS = ['nimura_subsystems.db_router.ProductViewerRouter']

# 静的ファイルの設定
STATIC_URL = '/static/'
STATIC_ROOT = r'C:\inetpub\Nsystem\static'
STATICFILES_DIRS = []

# メディアファイルの設定
MEDIA_URL = '/media/'
MEDIA_ROOT = r'C:\ProgramData\Nsystem\media'

# ログ設定（一時的に無効化）
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': r'C:\ProgramData\Nsystem\logs\django_error.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }

# セッション設定（社内利用向け）
SESSION_COOKIE_SECURE = False  # HTTPSを使わない場合
CSRF_COOKIE_SECURE = False     # HTTPSを使わない場合

# ファイルアップロードサイズ制限（必要に応じて調整）
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
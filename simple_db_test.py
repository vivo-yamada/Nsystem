import pymssql
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# 接続情報を取得
server = os.getenv('DB_HOST', '').replace('\\', ',')  # インスタンス名の形式を変換
if ',' in server:
    # インスタンス名がある場合は、サーバー名とインスタンス名に分割
    server_parts = server.split(',')
    server = server_parts[0]
    instance = server_parts[1]
    print(f"サーバー: {server}, インスタンス: {instance}")
else:
    instance = None
    
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
port = int(os.getenv('DB_PORT', '1433'))

print(f"接続情報:")
print(f"  サーバー: {server}")
print(f"  データベース: {database}")
print(f"  ユーザー: {username}")
print(f"  ポート: {port}")

try:
    # SQL Server Expressの場合、動的ポートを使用している可能性があるため
    # インスタンス名を含めて接続を試みる
    if instance:
        # インスタンス名がある場合は、サーバー\インスタンスの形式で接続
        server_with_instance = f"{server}\\{instance}"
        print(f"\n接続先: {server_with_instance}")
        conn = pymssql.connect(
            server=server_with_instance,
            user=username,
            password=password,
            database=database
        )
    else:
        conn = pymssql.connect(
            server=server,
            port=port,
            user=username,
            password=password,
            database=database
        )
    
    cursor = conn.cursor()
    
    # 接続確認
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print("\n✅ SQL Serverへの接続に成功しました！")
    print(f"SQL Server バージョン: {row[0][:50]}...")
    
    # T_製品写真サブテーブルの確認
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'T_製品写真サブ'
    """)
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("\n✅ T_製品写真サブテーブルが見つかりました")
        
        # 列情報を取得
        cursor.execute("""
            SELECT TOP 5 COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'T_製品写真サブ'
            ORDER BY ORDINAL_POSITION
        """)
        
        print("\nテーブル構造:")
        for row in cursor:
            col_name, data_type, max_length = row
            if max_length:
                print(f"  - {col_name}: {data_type}({max_length})")
            else:
                print(f"  - {col_name}: {data_type}")
                
        # サンプルデータの確認
        cursor.execute("SELECT TOP 1 * FROM T_製品写真サブ")
        sample = cursor.fetchone()
        if sample:
            print("\nサンプルデータが存在します")
        else:
            print("\nテーブルは空です")
    else:
        print("\n⚠️  T_製品写真サブテーブルが見つかりません")
        
        # 既存のテーブル一覧を表示
        cursor.execute("""
            SELECT TOP 10 TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        print("\n既存のテーブル（上位10件）:")
        for row in cursor:
            print(f"  - {row[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
    print(f"エラーの種類: {type(e).__name__}")
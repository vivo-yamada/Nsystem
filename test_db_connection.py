import os
import sys
import django
from django.db import connection

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nimura_subsystems.settings')
django.setup()

def test_connection():
    try:
        # データベース接続をテスト
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            print("✅ SQL Serverへの接続に成功しました！")
            print(f"SQL Server バージョン: {row[0]}")
            
            # T_製品写真サブテーブルの存在確認
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'T_製品写真サブ'
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                print("✅ T_製品写真サブテーブルが見つかりました")
                
                # テーブルの列情報を取得
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'T_製品写真サブ'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = cursor.fetchall()
                print("\nテーブル構造:")
                for col_name, data_type in columns:
                    print(f"  - {col_name}: {data_type}")
            else:
                print("⚠️  T_製品写真サブテーブルが見つかりません")
                
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print(f"エラーの詳細: {type(e).__name__}")

if __name__ == "__main__":
    test_connection()
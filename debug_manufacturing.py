#!/usr/bin/env python
"""
製造番号の処理フローデバッグスクリプト
"""

import os
import sys
import pymssql
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 環境変数を読み込み
load_dotenv()

def get_connection():
    """データベース接続を取得"""
    host = os.getenv('DB_HOST', '').replace('\\', ',')
    server_parts = host.split(',')
    server = server_parts[0]
    instance = server_parts[1] if len(server_parts) > 1 else None
    
    if instance:
        server = f"{server}\\{instance}"
        
    return pymssql.connect(
        server=server,
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def check_order_master_structure():
    """T_受注マスタテーブルの構造を確認"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("=== T_受注マスタテーブルの構造を確認 ===")
        
        # カラム情報を取得
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'T_受注マスタ'
            ORDER BY ORDINAL_POSITION
        """
        
        cursor.execute(query)
        columns = cursor.fetchall()
        
        print("\nカラム一覧:")
        manufacturing_column_found = False
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - NULL可: {col[2]}")
            if '製造番号' in col[0] or 'manufacturing' in col[0].lower():
                manufacturing_column_found = True
                print(f"    *** 製造番号関連カラム発見: {col[0]} ***")
        
        if not manufacturing_column_found:
            print("\n⚠️ 製造番号関連のカラムが見つかりません")
        
        # サンプルデータを取得
        print("\n=== サンプルデータ (TOP 5) ===")
        query = "SELECT TOP 5 * FROM T_受注マスタ"
        cursor.execute(query)
        
        # カラム名を取得
        col_names = [desc[0] for desc in cursor.description]
        print(f"\nカラム: {col_names}")
        
        rows = cursor.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"\n行 {i}:")
            for j, (col_name, value) in enumerate(zip(col_names, row)):
                if value is not None and str(value).strip():  # 空でない値のみ表示
                    print(f"  {col_name}: {value}")
        
        return col_names
        
    except Exception as e:
        print(f"エラー: {e}")
        return None
    finally:
        if conn:
            conn.close()

def test_manufacturing_number_search(manufacturing_number):
    """製造番号での検索をテスト"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        
        print(f"\n=== 製造番号 '{manufacturing_number}' で検索 ===")
        
        # 複数の可能性を試す
        possible_columns = ['製造番号', 'manufacturing_number', 'Manufacturing_Number']
        
        for col_name in possible_columns:
            try:
                query = f"""
                    SELECT TOP 5 受注コード, 製品コード, {col_name}
                    FROM T_受注マスタ
                    WHERE {col_name} = %s
                """
                
                cursor.execute(query, (manufacturing_number,))
                results = cursor.fetchall()
                
                if results:
                    print(f"\n✅ カラム '{col_name}' で検索成功:")
                    for r in results:
                        print(f"  - 受注コード: {r.get('受注コード', 'N/A')}")
                        print(f"    製品コード: {r.get('製品コード', 'N/A')}")
                        print(f"    {col_name}: {r.get(col_name, 'N/A')}")
                    return
                else:
                    print(f"❌ カラム '{col_name}' では見つかりませんでした")
                    
            except Exception as e:
                print(f"❌ カラム '{col_name}' でエラー: {e}")
        
        # 部分一致で検索
        print(f"\n=== 部分一致検索 ===")
        query = """
            SELECT TOP 5 受注コード, 製品コード, 製造番号
            FROM T_受注マスタ
            WHERE 製造番号 LIKE %s
        """
        
        try:
            cursor.execute(query, (f'%{manufacturing_number}%',))
            results = cursor.fetchall()
            
            if results:
                print(f"部分一致で見つかりました:")
                for r in results:
                    print(f"  - 受注コード: {r.get('受注コード', 'N/A')}")
                    print(f"    製品コード: {r.get('製品コード', 'N/A')}")
                    print(f"    製造番号: {r.get('製造番号', 'N/A')}")
            else:
                print("部分一致でも見つかりませんでした")
                
        except Exception as e:
            print(f"部分一致検索エラー: {e}")
                
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        if conn:
            conn.close()

def main():
    print("製造番号処理フローのデバッグを開始...\n")
    
    # テーブル構造を確認
    col_names = check_order_master_structure()
    
    if col_names:
        # テスト用の製造番号
        test_manufacturing_numbers = [
            "25-52616",   # ユーザーの例
            "25-52618",   # 製作工程コードから抽出される例
        ]
        
        for manufacturing_num in test_manufacturing_numbers:
            test_manufacturing_number_search(manufacturing_num)
    
    print("\n=== デバッグ完了 ===")

if __name__ == "__main__":
    main()
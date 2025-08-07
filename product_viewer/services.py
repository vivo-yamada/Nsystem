import os
import pymssql
from django.conf import settings
from typing import List, Dict, Optional

class ProductPhotoService:
    """
    製品写真データを取得するサービスクラス
    """
    
    @staticmethod
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
    
    @classmethod
    def get_photos_by_product_code(cls, product_code: str) -> List[Dict]:
        """
        製品コードで写真情報を取得
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            query = """
                SELECT 
                    製品写真コード as product_photo_code,
                    製品コード as product_code,
                    HNO as hno,
                    PATH as path,
                    備考 as remarks
                FROM T_製品写真サブ
                WHERE 製品コード = %s
                ORDER BY HNO
            """
            
            cursor.execute(query, (product_code,))
            results = cursor.fetchall()
            
            return results
            
        except Exception as e:
            print(f"データベースエラー: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_photo_by_id(cls, photo_code: str) -> Optional[Dict]:
        """
        製品写真コードで特定の写真情報を取得
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            query = """
                SELECT 
                    製品写真コード as product_photo_code,
                    製品コード as product_code,
                    HNO as hno,
                    PATH as path,
                    備考 as remarks
                FROM T_製品写真サブ
                WHERE 製品写真コード = %s
            """
            
            cursor.execute(query, (photo_code,))
            result = cursor.fetchone()
            
            return result
            
        except Exception as e:
            print(f"データベースエラー: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def search_products(cls, keyword: str) -> List[Dict]:
        """
        製品コードで部分一致検索
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            query = """
                SELECT DISTINCT 製品コード as product_code
                FROM T_製品写真サブ
                WHERE 製品コード LIKE %s
                ORDER BY 製品コード
            """
            
            cursor.execute(query, (f'%{keyword}%',))
            results = cursor.fetchall()
            
            return results
            
        except Exception as e:
            print(f"データベースエラー: {e}")
            return []
        finally:
            if conn:
                conn.close()
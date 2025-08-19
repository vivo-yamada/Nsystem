import os
import pymssql
from django.conf import settings
from typing import List, Dict, Optional
import re

class ProductPhotoService:
    """
    製品写真データを取得するサービスクラス
    """
    
    @staticmethod
    def convert_windows_path_to_wsl(windows_path: str) -> str:
        r"""
        WindowsパスをWSL形式に変換
        例: C:\Users\... -> /mnt/c/Users/...
        """
        if not windows_path:
            return windows_path
            
        # Windowsパスの正規表現パターン  
        windows_pattern = r'^([A-Za-z]):(.*)$'
        match = re.match(windows_pattern, windows_path)
        
        if match:
            drive_letter = match.group(1).lower()
            path_part = match.group(2).replace('\\', '/')
            return f"/mnt/{drive_letter}{path_part}"
        
        return windows_path
    
    @staticmethod
    def get_accessible_image_path(original_path: str) -> str:
        """
        アクセス可能な画像パスを取得
        """
        if not original_path:
            return None
            
        # WSL形式に変換
        wsl_path = ProductPhotoService.convert_windows_path_to_wsl(original_path)
        
        # ファイルが存在するか確認
        if os.path.exists(wsl_path):
            return wsl_path
        
        # 元のパスが存在するか確認
        if os.path.exists(original_path):
            return original_path
            
        return None
    
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
            
            # 各結果にアクセス可能なパス情報を追加
            for result in results:
                result['accessible_path'] = cls.get_accessible_image_path(result['path'])
                result['path_exists'] = result['accessible_path'] is not None
            
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
            
            if result:
                result['accessible_path'] = cls.get_accessible_image_path(result['path'])
                result['path_exists'] = result['accessible_path'] is not None
            
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


class ProductMasterService:
    """
    製品マスタデータを取得するサービスクラス
    """
    
    @staticmethod
    def get_connection():
        """データベース接続を取得"""
        return ProductPhotoService.get_connection()
    
    @classmethod
    def get_product_code_by_part_number(cls, part_number: str) -> Optional[str]:
        """
        品番から製品コードを取得
        T_製品マスタから品番が一致する最初の製品コードを返す
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            # 品番から製品コードを取得
            query = """
                SELECT TOP 1 製品コード as product_code
                FROM T_製品マスタ
                WHERE 品番 = %s
                ORDER BY 製品コード
            """
            
            cursor.execute(query, (part_number,))
            result = cursor.fetchone()
            
            return result['product_code'] if result else None
            
        except Exception as e:
            print(f"製品マスタ取得エラー: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_photos_by_part_number(cls, part_number: str) -> List[Dict]:
        """
        品番から製品写真情報を取得
        """
        # まず品番から製品コードを取得
        product_code = cls.get_product_code_by_part_number(part_number)
        
        if not product_code:
            return []
        
        # 製品コードから写真情報を取得
        return ProductPhotoService.get_photos_by_product_code(product_code)


class OrderMasterService:
    """
    受注マスタデータを取得するサービスクラス
    """
    
    @staticmethod
    def get_connection():
        """データベース接続を取得"""
        return ProductPhotoService.get_connection()
    
    @classmethod
    def get_product_code_by_order_code(cls, order_code: str) -> Optional[str]:
        """
        受注コードから製品コードを取得
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            query = """
                SELECT 製品コード as product_code
                FROM T_受注マスタ
                WHERE 受注コード = %s
            """
            
            cursor.execute(query, (order_code,))
            result = cursor.fetchone()
            
            return result['product_code'] if result else None
            
        except Exception as e:
            print(f"受注マスタ取得エラー: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_order_code_by_manufacturing_number(cls, manufacturing_number: str) -> Optional[str]:
        """
        製造番号から受注コードを取得
        """
        conn = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(as_dict=True)
            
            query = """
                SELECT 受注コード as order_code
                FROM T_受注マスタ
                WHERE 製造番号 = %s
            """
            
            cursor.execute(query, (manufacturing_number,))
            result = cursor.fetchone()
            
            return result['order_code'] if result else None
            
        except Exception as e:
            print(f"製造番号から受注コード取得エラー: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def get_photos_by_order_code(cls, order_code: str) -> List[Dict]:
        """
        受注コードから製品写真情報を取得
        """
        # まず受注コードから製品コードを取得
        product_code = cls.get_product_code_by_order_code(order_code)
        
        if not product_code:
            return []
        
        # 製品コードから写真情報を取得
        return ProductPhotoService.get_photos_by_product_code(product_code)
    
    @classmethod
    def get_photos_by_manufacturing_number(cls, manufacturing_number: str) -> List[Dict]:
        """
        製造番号から製品写真情報を取得
        """
        # 製造番号から受注コードを取得
        order_code = cls.get_order_code_by_manufacturing_number(manufacturing_number)
        
        if not order_code:
            return []
        
        # 受注コードから製品写真を取得
        return cls.get_photos_by_order_code(order_code)
    
    @classmethod
    def get_photos_by_production_process_code(cls, production_process_code: str) -> List[Dict]:
        """
        製作工程コードから製品写真情報を取得
        """
        # 製作工程コードの上8桁が製造番号
        if len(production_process_code) >= 8:
            manufacturing_number = production_process_code[:8]
            return cls.get_photos_by_manufacturing_number(manufacturing_number)
        
        return []
import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Pythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_viewer.services import ProductPhotoService
import pymssql

def update_remarks():
    """テスト用に備考情報を更新"""
    
    try:
        conn = ProductPhotoService.get_connection()
        cursor = conn.cursor()
        
        # テスト用の備考データ
        remarks_data = [
            ('005062-01', '正面からの写真'),
            ('005062-02', '側面からの角度'),
            ('005062-03', '細部の拡大写真'),
        ]
        
        print("備考情報を更新しています...")
        
        for photo_code, remark in remarks_data:
            try:
                cursor.execute("""
                    UPDATE T_製品写真サブ 
                    SET 備考 = %s 
                    WHERE 製品写真コード = %s
                """, (remark, photo_code))
                print(f"✅ {photo_code}: {remark}")
            except Exception as e:
                print(f"❌ {photo_code}: {e}")
        
        # コミット
        conn.commit()
        print("\n✅ 備考情報の更新が完了しました")
        
        # 更新結果を確認
        print("\n=== 更新結果の確認 ===")
        photos = ProductPhotoService.get_photos_by_product_code('005062')
        for photo in photos:
            print(f"写真コード: {photo['product_photo_code']}")
            print(f"備考: {photo.get('remarks', 'なし')}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_remarks()
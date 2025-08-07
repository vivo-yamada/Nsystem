import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Pythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_viewer.services import ProductPhotoService

def test_service():
    try:
        print("ProductPhotoServiceのテスト...")
        
        # 製品コード一覧を取得（最初の10件）
        print("\n1. 製品コード検索テスト（空文字で全件検索）")
        products = ProductPhotoService.search_products('')
        
        if products:
            print(f"✅ {len(products)} 件の製品が見つかりました")
            print("最初の5件:")
            for i, product in enumerate(products[:5]):
                print(f"  {i+1}. {product['product_code']}")
            
            # 最初の製品コードで写真を検索
            first_product_code = products[0]['product_code']
            print(f"\n2. 製品コード '{first_product_code}' の写真を検索")
            
            photos = ProductPhotoService.get_photos_by_product_code(first_product_code)
            
            if photos:
                print(f"✅ {len(photos)} 件の写真が見つかりました")
                for photo in photos:
                    print(f"\n  製品写真コード: {photo['product_photo_code']}")
                    print(f"  製品コード: {photo['product_code']}")
                    print(f"  HNO: {photo['hno']}")
                    print(f"  PATH: {photo['path']}")
                    print(f"  備考: {photo['remarks']}")
                    
                # 特定の写真情報を取得
                if photos:
                    first_photo_code = photos[0]['product_photo_code']
                    print(f"\n3. 製品写真コード '{first_photo_code}' の詳細を取得")
                    
                    photo_detail = ProductPhotoService.get_photo_by_id(first_photo_code)
                    if photo_detail:
                        print("✅ 写真情報を取得しました")
                        print(f"  PATH: {photo_detail['path']}")
            else:
                print("⚠️  写真が見つかりませんでした")
        else:
            print("⚠️  製品が見つかりませんでした")
            
        print("\n✅ サービスのテストが正常に完了しました")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
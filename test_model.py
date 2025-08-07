import os
import sys
import django

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nimura_subsystems.settings')
django.setup()

from product_viewer.models import ProductPhoto

def test_model():
    try:
        # ProductPhotoモデルでデータを取得
        print("ProductPhotoモデルのテスト...")
        
        # 総レコード数を確認
        count = ProductPhoto.objects.count()
        print(f"\n✅ 総レコード数: {count}")
        
        # 最初の5件を取得
        photos = ProductPhoto.objects.all()[:5]
        
        if photos:
            print("\n最初の5件のデータ:")
            print("-" * 80)
            for photo in photos:
                print(f"製品写真コード: {photo.product_photo_code}")
                print(f"製品コード: {photo.product_code}")
                print(f"HNO: {photo.hno}")
                print(f"PATH: {photo.path}")
                print(f"備考: {photo.remarks}")
                print("-" * 80)
        
        # 特定の製品コードで検索テスト
        if photos:
            sample_product_code = photos[0].product_code
            filtered_photos = ProductPhoto.objects.filter(product_code=sample_product_code)
            print(f"\n製品コード '{sample_product_code}' の写真数: {filtered_photos.count()}")
            
        print("\n✅ モデルのテストが正常に完了しました")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print(f"エラーの種類: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model()
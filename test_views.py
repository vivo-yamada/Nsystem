import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nimura_subsystems.settings')
django.setup()

def test_views():
    """ビューの動作をテスト"""
    client = Client()
    
    try:
        # トップページのテスト
        print("1. トップページのテスト")
        response = client.get('/')
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ トップページが正常に表示されました")
        else:
            print(f"❌ エラー: {response.status_code}")
            return
        
        # 検索ページのテスト（製品コードなし）
        print("\n2. 空の検索テスト")
        response = client.get('/search/')
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 空の検索ページが正常に表示されました")
        
        # 検索ページのテスト（存在する製品コード）
        print("\n3. 製品コード '005062' の検索テスト")
        response = client.get('/search/', {'product_code': '005062'})
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if '005062' in content:
                print("✅ 製品コード 005062 の検索結果が表示されました")
            else:
                print("⚠️ 製品が見つからないか、表示に問題があります")
        
        # 検索ページのテスト（存在しない製品コード）
        print("\n4. 存在しない製品コード 'NONEXIST' の検索テスト")
        response = client.get('/search/', {'product_code': 'NONEXIST'})
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'が見つかりませんでした' in content:
                print("✅ 適切にエラーメッセージが表示されました")
        
        # 画像配信のテスト
        print("\n5. 画像配信テスト（005062-01）")
        response = client.get('/image/005062-01/')
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 画像が正常に配信されました")
            print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
        elif response.status_code == 404:
            print("⚠️ 画像ファイルが見つかりません（パスの問題の可能性）")
        else:
            print(f"❌ 予期しないエラー: {response.status_code}")
        
        print("\n✅ ビューのテストが完了しました")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_views()
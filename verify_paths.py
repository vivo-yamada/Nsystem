"""
パス変換機能の動作確認スクリプト

このスクリプトは以下の動作確認を行います：
- WindowsパスからWSL形式への変換機能
- 画像ファイルの存在確認
- データベース内のパス情報とファイルシステムの整合性確認

実行方法:
    python verify_paths.py
"""

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Pythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_viewer.services import ProductPhotoService

def verify_path_conversion():
    """パス変換のテスト"""
    
    print("=== パス変換テスト ===")
    
    # テストケース
    test_paths = [
        "C:\\Users\\k_yam\\OneDrive\\デスクトップ\\IMG_8495.jpg",
        "C:\\Users\\k_yam\\OneDrive\\デスクトップ\\IMG_8497.jpg", 
        "D:\\Photos\\test.jpg",
        "/mnt/c/Users/test/image.jpg",
        ""
    ]
    
    for original_path in test_paths:
        print(f"\n原パス: {original_path}")
        
        # WSL形式に変換
        wsl_path = ProductPhotoService.convert_windows_path_to_wsl(original_path)
        print(f"WSL形式: {wsl_path}")
        
        # アクセス可能なパスを取得
        accessible_path = ProductPhotoService.get_accessible_image_path(original_path)
        print(f"アクセス可能: {accessible_path}")
        print(f"存在する: {accessible_path is not None}")
        
        if accessible_path:
            print(f"ファイル確認: {os.path.exists(accessible_path)}")
    
    print("\n=== データベースからの実データテスト ===")
    
    # 実際のデータベースからデータを取得してテスト
    photos = ProductPhotoService.get_photos_by_product_code('005062')
    
    for photo in photos:
        print(f"\n写真コード: {photo['product_photo_code']}")
        print(f"元パス: {photo['path']}")
        print(f"アクセス可能パス: {photo.get('accessible_path', 'N/A')}")
        print(f"パス存在: {photo.get('path_exists', False)}")

if __name__ == "__main__":
    verify_path_conversion()
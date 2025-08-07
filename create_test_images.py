from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(width, height, text, filename):
    """テスト用の画像を作成"""
    # 画像を作成
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # テキストを描画
    try:
        # デフォルトフォントを使用
        font_size = min(width, height) // 10
        # PIL のデフォルトフォントは限られているため、エラーハンドリング
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # テキストの位置を計算
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # テキストを描画
    draw.text((x, y), text, fill='darkblue', font=font)
    
    # 境界線を描画
    draw.rectangle([(0, 0), (width-1, height-1)], outline='darkblue', width=3)
    
    # 保存
    img.save(filename, 'JPEG', quality=90)
    print(f"テスト画像を作成しました: {filename}")

def main():
    """テスト用画像を作成"""
    base_path = "/mnt/c/Users/k_yam/OneDrive/デスクトップ/"
    
    # テスト画像のデータ
    test_images = [
        ("IMG_8495.jpg", "製品写真 005062-01"),
        ("IMG_8497.jpg", "製品写真 005062-02"), 
        ("IMG_8498.jpg", "製品写真 005062-03"),
    ]
    
    # 各画像を作成
    for filename, text in test_images:
        full_path = os.path.join(base_path, filename)
        create_test_image(600, 400, text, full_path)

if __name__ == "__main__":
    main()
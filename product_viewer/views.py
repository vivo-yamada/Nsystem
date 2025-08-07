from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import View
from .services import ProductPhotoService
import os
import mimetypes

def index(request):
    """製品コード入力画面"""
    return render(request, 'product_viewer/index.html')

def search_product(request):
    """製品コードで検索して画像一覧を表示"""
    product_code = request.GET.get('product_code', '').strip()
    
    if not product_code:
        return render(request, 'product_viewer/search.html', {
            'error': '製品コードを入力してください'
        })
    
    # 製品写真を検索
    photos = ProductPhotoService.get_photos_by_product_code(product_code)
    
    if not photos:
        return render(request, 'product_viewer/search.html', {
            'error': f'製品コード {product_code} の写真が見つかりませんでした',
            'product_code': product_code
        })
    
    return render(request, 'product_viewer/search.html', {
        'photos': photos,
        'product_code': product_code
    })

def serve_image(request, product_photo_code):
    """ネットワークドライブから画像を配信"""
    # 製品写真情報を取得
    photo = ProductPhotoService.get_photo_by_id(product_photo_code)
    
    if not photo:
        raise Http404("画像が見つかりません")
    
    # アクセス可能なパスを使用
    image_path = photo.get('accessible_path')
    
    if not image_path:
        raise Http404(f"画像ファイルにアクセスできません: {photo['path']}")
    
    # MIMEタイプを推測
    content_type, _ = mimetypes.guess_type(image_path)
    if content_type is None:
        content_type = 'image/jpeg'
    
    try:
        with open(image_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            # キャッシュヘッダーを追加
            response['Cache-Control'] = 'public, max-age=3600'
            return response
    except Exception as e:
        raise Http404(f"画像の読み込みに失敗しました: {str(e)}")

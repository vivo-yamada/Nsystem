from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import ProductPhotoService, OrderMasterService
import os
import mimetypes
import json

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


@csrf_exempt
def search_by_barcode(request):
    """バーコード（受注コード）で検索してJSONレスポンスを返す"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        order_code = data.get('order_code', '').strip()
        
        if not order_code:
            return JsonResponse({'error': '受注コードが必要です'}, status=400)
        
        # 受注コードから製品写真を取得
        photos = OrderMasterService.get_photos_by_order_code(order_code)
        
        if not photos:
            return JsonResponse({
                'success': False,
                'error': f'受注コード {order_code} に対応する製品写真が見つかりませんでした'
            })
        
        # JSON形式でレスポンス（画像URLを含む）
        photos_with_urls = []
        for photo in photos:
            photo_dict = dict(photo)
            photo_dict['image_url'] = f'/image/{photo["product_photo_code"]}/'
            photos_with_urls.append(photo_dict)
        
        return JsonResponse({
            'success': True,
            'order_code': order_code,
            'product_code': photos[0]['product_code'],
            'photos': photos_with_urls
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def search_by_product_code(request):
    """製品コードで検索してJSONレスポンスを返す"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        product_code = data.get('product_code', '').strip()
        
        if not product_code:
            return JsonResponse({'error': '製品コードが必要です'}, status=400)
        
        # 製品写真を検索
        photos = ProductPhotoService.get_photos_by_product_code(product_code)
        
        if not photos:
            return JsonResponse({
                'success': False,
                'error': f'製品コード {product_code} の写真が見つかりませんでした'
            })
        
        # JSON形式でレスポンス（画像URLを含む）
        photos_with_urls = []
        for photo in photos:
            photo_dict = dict(photo)
            photo_dict['image_url'] = f'/image/{photo["product_photo_code"]}/'
            photos_with_urls.append(photo_dict)
        
        return JsonResponse({
            'success': True,
            'product_code': product_code,
            'order_code': '',  # 製品コード検索の場合は受注コードなし
            'photos': photos_with_urls
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

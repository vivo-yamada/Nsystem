from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import ProductPhotoService, OrderMasterService, ProductMasterService
from .barcode_utils import detect_and_format_barcode_info, BarcodeDetector
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
    """バーコードで自動判別して検索してJSONレスポンスを返す"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        barcode = data.get('order_code', '').strip()  # パラメータ名は保持（互換性のため）
        
        if not barcode:
            return JsonResponse({'error': 'バーコードが必要です'}, status=400)
        
        # バーコードの種類を判別
        barcode_info = detect_and_format_barcode_info(barcode)
        barcode_type = barcode_info['type']
        
        photos = []
        product_code = None
        order_code = None
        manufacturing_number = None
        
        # デバッグ情報を記録するための辞書
        debug_info = {
            'steps': [],
            'errors': []
        }
        
        # バーコード種類に応じて処理
        if barcode_type == 'order_code':
            # 受注コードの場合
            order_code = barcode
            debug_info['steps'].append(f'受注コード: {order_code}')
            
            # 製品コードを取得
            product_code = OrderMasterService.get_product_code_by_order_code(order_code)
            if product_code:
                debug_info['steps'].append(f'製品コード: {product_code}')
                photos = ProductPhotoService.get_photos_by_product_code(product_code)
                debug_info['steps'].append(f'写真数: {len(photos)}枚')
            else:
                debug_info['errors'].append('製品コードが取得できませんでした')
            
        elif barcode_type == 'manufacturing_number':
            # 製造番号の場合
            manufacturing_number = barcode
            debug_info['steps'].append(f'製造番号: {manufacturing_number}')
            
            # 製造番号から受注コードを取得
            order_code = OrderMasterService.get_order_code_by_manufacturing_number(manufacturing_number)
            if order_code:
                debug_info['steps'].append(f'受注コード: {order_code}')
                
                # 受注コードから製品コードを取得
                product_code = OrderMasterService.get_product_code_by_order_code(order_code)
                if product_code:
                    debug_info['steps'].append(f'製品コード: {product_code}')
                    photos = ProductPhotoService.get_photos_by_product_code(product_code)
                    debug_info['steps'].append(f'写真数: {len(photos)}枚')
                else:
                    debug_info['errors'].append('製品コードが取得できませんでした')
            else:
                debug_info['errors'].append('受注コードが取得できませんでした')
            
        elif barcode_type == 'production_process_code':
            # 製作工程コードの場合
            debug_info['steps'].append(f'製作工程コード: {barcode}')
            
            # 上8桁を製造番号として抽出
            manufacturing_number = BarcodeDetector.get_manufacturing_number_from_production_process_code(barcode)
            debug_info['steps'].append(f'抽出した製造番号: {manufacturing_number}')
            
            # 製造番号から受注コードを取得
            order_code = OrderMasterService.get_order_code_by_manufacturing_number(manufacturing_number)
            if order_code:
                debug_info['steps'].append(f'受注コード: {order_code}')
                
                # 受注コードから製品コードを取得
                product_code = OrderMasterService.get_product_code_by_order_code(order_code)
                if product_code:
                    debug_info['steps'].append(f'製品コード: {product_code}')
                    photos = ProductPhotoService.get_photos_by_product_code(product_code)
                    debug_info['steps'].append(f'写真数: {len(photos)}枚')
                else:
                    debug_info['errors'].append('製品コードが取得できませんでした')
            else:
                debug_info['errors'].append('受注コードが取得できませんでした')
                
        elif barcode_type == 'part_number':
            # 品番の場合
            debug_info['steps'].append(f'品番: {barcode}')
            
            # 品番から製品コードを取得
            product_code = ProductMasterService.get_product_code_by_part_number(barcode)
            if product_code:
                debug_info['steps'].append(f'製品コード: {product_code}')
                photos = ProductPhotoService.get_photos_by_product_code(product_code)
                debug_info['steps'].append(f'写真数: {len(photos)}枚')
            else:
                debug_info['errors'].append('製品コードが取得できませんでした')
        
        if not photos:
            # エラーメッセージにデバッグ情報を含める
            error_message = f'{barcode_info["display_name"]} {barcode} に対応する製品写真が見つかりませんでした'
            
            # デバッグ情報を追加
            if debug_info['steps']:
                error_message += '\n\n処理ステップ:\n' + '\n'.join([f'{i+1}. {step}' for i, step in enumerate(debug_info['steps'])])
            
            if debug_info['errors']:
                error_message += '\n\nエラー詳細:\n' + '\n'.join([f'• {error}' for error in debug_info['errors']])
            
            return JsonResponse({
                'success': False,
                'error': error_message,
                'barcode_info': barcode_info,
                'debug_info': debug_info
            })
        
        # 製品コードを取得（まだ取得できていない場合）
        if not product_code and photos:
            product_code = photos[0]['product_code']
        
        # JSON形式でレスポンス（画像URLを含む）
        photos_with_urls = []
        for photo in photos:
            photo_dict = dict(photo)
            photo_dict['image_url'] = f'/image/{photo["product_photo_code"]}/'
            photos_with_urls.append(photo_dict)
        
        return JsonResponse({
            'success': True,
            'barcode_info': barcode_info,
            'order_code': order_code or '',
            'manufacturing_number': manufacturing_number or '',
            'product_code': product_code or '',
            'part_number': barcode if barcode_type == 'part_number' else '',
            'photos': photos_with_urls,
            'debug_info': debug_info  # デバッグ情報を追加
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


@csrf_exempt
def search_by_part_number(request):
    """品番で検索してJSONレスポンスを返す"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        part_number = data.get('part_number', '').strip()
        
        if not part_number:
            return JsonResponse({'error': '品番が必要です'}, status=400)
        
        # 品番から製品コードを取得
        product_code = ProductMasterService.get_product_code_by_part_number(part_number)
        
        if not product_code:
            return JsonResponse({
                'success': False,
                'error': f'品番 {part_number} に対応する製品が見つかりませんでした'
            })
        
        # 製品写真を検索
        photos = ProductPhotoService.get_photos_by_product_code(product_code)
        
        if not photos:
            return JsonResponse({
                'success': False,
                'error': f'品番 {part_number} (製品コード: {product_code}) の写真が見つかりませんでした'
            })
        
        # JSON形式でレスポンス（画像URLを含む）
        photos_with_urls = []
        for photo in photos:
            photo_dict = dict(photo)
            photo_dict['image_url'] = f'/image/{photo["product_photo_code"]}/'
            photos_with_urls.append(photo_dict)
        
        return JsonResponse({
            'success': True,
            'part_number': part_number,
            'product_code': product_code,
            'order_code': '',  # 品番検索の場合は受注コードなし
            'photos': photos_with_urls
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

"""
バーコード種類判別ユーティリティ
"""

import re
from typing import Tuple, Optional


class BarcodeDetector:
    """
    バーコードの種類を自動判別するクラス
    """
    
    @staticmethod
    def detect_barcode_type(barcode: str) -> Tuple[str, Optional[str]]:
        """
        バーコードの種類を判別する
        
        Args:
            barcode: 読み取ったバーコード文字列
        
        Returns:
            Tuple[str, Optional[str]]: (バーコード種類, 判別理由)
        """
        barcode = barcode.strip()
        
        # 受注コード判別: XXXXXX-XXXXXX-XX 形式
        if BarcodeDetector._is_order_code(barcode):
            return "order_code", "XXXXXX-XXXXXX-XX形式"
        
        # 製作工程コード判別: XX-XXXXX-XXXX-XX 形式（13桁以上）
        if BarcodeDetector._is_production_process_code(barcode):
            return "production_process_code", "XX-XXXXX-XXXX-XX形式（13桁以上）"
        
        # 製造番号判別: XX-XXXXX 形式（8桁）
        if BarcodeDetector._is_manufacturing_number(barcode):
            return "manufacturing_number", "XX-XXXXX形式（8桁）"
        
        # 品番判別: 上記に該当しない場合
        return "part_number", "その他の形式（品番として処理）"
    
    @staticmethod
    def _is_order_code(barcode: str) -> bool:
        """
        受注コード形式かチェック
        パターン: 037525-250801-01 (XXXXXX-XXXXXX-XX)
        """
        pattern = r'^\d{6}-\d{6}-\d{2}$'
        return bool(re.match(pattern, barcode))
    
    @staticmethod
    def _is_manufacturing_number(barcode: str) -> bool:
        """
        製造番号形式かチェック
        パターン: 25-52616 (XX-XXXXX) 8桁
        """
        pattern = r'^\d{2}-\d{5}$'
        return bool(re.match(pattern, barcode))
    
    @staticmethod
    def _is_production_process_code(barcode: str) -> bool:
        """
        製作工程コード形式かチェック
        パターン: 25-52618-0301-03 (XX-XXXXX-XXXX-XX) 13桁以上
        """
        # ハイフンを除いた長さが13桁以上で、XX-XXXXX-で始まる
        no_hyphens = barcode.replace('-', '')
        if len(no_hyphens) >= 13:
            pattern = r'^\d{2}-\d{5}-'
            return bool(re.match(pattern, barcode))
        return False
    
    @staticmethod
    def get_manufacturing_number_from_production_process_code(production_process_code: str) -> str:
        """
        製作工程コードから製造番号を抽出
        """
        return production_process_code[:8]


def detect_and_format_barcode_info(barcode: str) -> dict:
    """
    バーコードを判別して詳細情報を返す
    """
    barcode_type, reason = BarcodeDetector.detect_barcode_type(barcode)
    
    result = {
        'barcode': barcode,
        'type': barcode_type,
        'reason': reason,
        'display_name': _get_display_name(barcode_type)
    }
    
    # 製作工程コードの場合は製造番号も抽出
    if barcode_type == "production_process_code":
        manufacturing_number = BarcodeDetector.get_manufacturing_number_from_production_process_code(barcode)
        result['extracted_manufacturing_number'] = manufacturing_number
    
    return result


def _get_display_name(barcode_type: str) -> str:
    """
    バーコード種類の表示名を取得
    """
    display_names = {
        'order_code': '受注コード',
        'manufacturing_number': '製造番号',
        'production_process_code': '製作工程コード',
        'part_number': '品番'
    }
    return display_names.get(barcode_type, 'unknown')
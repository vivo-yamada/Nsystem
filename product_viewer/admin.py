from django.contrib import admin
from .models import ProductPhoto

@admin.register(ProductPhoto)
class ProductPhotoAdmin(admin.ModelAdmin):
    list_display = ['product_photo_code', 'product_code', 'hno', 'path', 'remarks']
    list_filter = ['product_code']
    search_fields = ['product_code', 'product_photo_code', 'path']
    readonly_fields = ['product_photo_code', 'product_code', 'hno', 'path', 'remarks']
    
    def has_add_permission(self, request):
        # 既存テーブルなので新規追加は禁止
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 既存テーブルなので削除は禁止
        return False
    
    def has_change_permission(self, request, obj=None):
        # 既存テーブルなので変更は禁止（読み取り専用）
        return False

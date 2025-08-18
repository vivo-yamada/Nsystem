from django.urls import path
from . import views

app_name = 'product_viewer'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_product, name='search'),
    path('api/barcode-search/', views.search_by_barcode, name='barcode_search'),
    path('api/product-search/', views.search_by_product_code, name='product_search'),
    path('image/<str:product_photo_code>/', views.serve_image, name='serve_image'),
]
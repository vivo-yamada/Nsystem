from django.urls import path
from . import views

app_name = 'product_viewer'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_product, name='search'),
    path('image/<str:product_photo_code>/', views.serve_image, name='serve_image'),
]
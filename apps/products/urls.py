from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('urunler/', views.product_list, name='list'),
    path('urun/<slug:slug>/', views.product_detail, name='detail'),
    path('api/urun/<int:pk>/fiyat/', views.product_price_api, name='price_api'),
]

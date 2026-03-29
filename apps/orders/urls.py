from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('sepet/', views.cart_view, name='cart'),
    path('sepet/ekle/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('sepet/guncelle/<int:product_id>/', views.update_cart, name='update_cart'),
    path('sepet/sil/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('siparislerim/', views.order_list, name='order_list'),
]

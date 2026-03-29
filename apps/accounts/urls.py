from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('giris/', views.login_view, name='login'),
    path('kayit/', views.register_view, name='register'),
    path('cikis/', views.logout_view, name='logout'),
    path('hesabim/', views.dashboard, name='dashboard'),
    path('adres/ekle/', views.add_address, name='add_address'),
    path('adres/<int:pk>/sil/', views.delete_address, name='delete_address'),
]

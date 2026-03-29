from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('yonetim/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('hesap/', include('apps.accounts.urls')),
    path('siparis/', include('apps.orders.urls')),
    path('lokasyon/', include('apps.logistics.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'Yalıtım Deposu Yönetim Paneli'
admin.site.site_title = 'Yalıtım Deposu Admin'
admin.site.index_title = 'Yönetim Paneli'

from django.urls import path
from . import views

app_name = 'logistics'

urlpatterns = [
    path('sehir-sec/', views.set_city, name='set_city'),
    path('ilceler/<int:city_id>/', views.get_districts, name='get_districts'),
]

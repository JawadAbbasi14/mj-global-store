# cart/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.detail, name='detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add'),
]

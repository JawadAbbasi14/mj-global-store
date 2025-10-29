# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('payment/<int:order_id>/', views.Payment, name='payment'),  # ✅ ID accept karega
]
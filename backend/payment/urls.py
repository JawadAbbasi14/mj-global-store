# payment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('select/', views.payment_method, name='payment_method'),
    # path('success/', views.payment_success, name='payment_success'),  # optional
]
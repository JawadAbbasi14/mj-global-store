# payment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('select/', views.payment_method, name='payment_method'),      # form dikhaye
    path('success/', views.payment_success, name='payment_success'),   # success page
    path('failed/', views.payment_failed, name='payment_failed'),      # error page
    # Optional: gateway page for Easypaisa/JazzCash
    path('gateway/', views.payment_gateway, name='payment_gateway'),
]
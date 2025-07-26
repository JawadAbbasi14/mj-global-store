# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # yeh view 127.0.0.1:8000/ handle kare ga
    path('signup/', views.signup, name='signup'),
]

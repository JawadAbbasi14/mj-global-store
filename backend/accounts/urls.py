# accounts/urls.py
from django.urls import path
from . import views
from accounts.views import test_error

urlpatterns = [
    path('', views.home, name='home'),  # yeh view 127.0.0.1:8000/ handle kare ga
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('test-error/', test_error),
]




from django.db import models
from . import views
from django.urls import path

urlpatterns = [
    path('',views.cart_home,name="cart-1")
]
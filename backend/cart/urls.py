from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('detail/', views.detail, name='detail'),
    path('confirm/', views.confirm_cart, name='confirm_cart'),
    path('remove/<int:product_id>/',views.remove_item,name='remove-item')
]
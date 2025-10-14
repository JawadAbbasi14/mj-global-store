# The corrected admin.py
from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key',  'created_at')
    search_fields = ('user__username', 'session_key')
    list_filter = ('created_at',) # FIXED: Added a trailing comma

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'unit_price', 'total_price')
    search_fields = ('product__name',)
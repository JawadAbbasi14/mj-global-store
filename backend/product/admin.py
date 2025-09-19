from django.contrib import admin
from .models import Products

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock','image')   # list view
    search_fields = ('name',)                        # search option
    list_filter = ('price',)                         # filter option


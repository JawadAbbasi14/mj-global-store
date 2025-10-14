# cart/views.py (example)
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart
from product.models import Products

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, pk=product_id)
    cart = Cart.get_or_create_cart(request)
    qty = int(request.POST.get('qty', 1)) if request.method=='POST' else 1
    cart.add_product(product, qty=qty)
    return redirect('cart:detail')

def detail(request):
    cart = Cart.get_or_create_cart(request)
    return render(request, 'cart/detial.html', {'cart': cart})

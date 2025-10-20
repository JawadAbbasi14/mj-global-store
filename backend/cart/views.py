from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Cart, CartAuthority,CartItem
from django.shortcuts import get_object_or_404
from product.models import Products

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, pk=product_id)
    cart = Cart.get_or_create_cart(request)

    if not cart.user and request.user.is_authenticated:
        cart.user = request.user

    qty = int(request.POST.get('qty', 1)) if request.method == 'POST' else 1
    cart.is_active = True
    cart.add_product(product, qty=qty)
    cart.save()

    return redirect('cart:detail')


def remove_item(request, product_id):
    product = get_object_or_404(Products, pk=product_id)
    cart = Cart.objects.get(user=request.user)  # ya session-based logic agar user-login nahi
    CartItem.objects.filter(cart=cart, product=product).delete()
    return redirect('cart:detail')



def detail(request):
    cart = Cart.get_or_create_cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

User = get_user_model()

@login_required
def confirm_cart(request):
    if request.method == 'POST':
        user = request.user

        # 1. User ka active cart identify karo
        try:
            cart = Cart.objects.get(user=user, is_active=True)  # Assume 'is_active' field hai
        except Cart.DoesNotExist:
            messages.error(request, "Active cart not found.")
            return redirect('cart:detail')  # Ya jahan se aaya hai

        # 2. Cart ka total calculate karo (agar model mein method hai toh)
        total = sum(item.total_price for item in cart.items.all())
 
        # 3. CartAuthority record create karo
        CartAuthority.objects.create(
            user=user,
            cart=cart,
            status=CartAuthority.Status.PENDING,
            total=total
        )

        # Optional: cart ko inactive kar do
        cart.is_active = False
        cart.save()

        # 4. Redirect karo success page pe
        messages.success(request, "Cart confirmed successfully!")
        return  redirect('cart:detail')

    return  redirect('product/product.html')  # Apna URL name daal dein
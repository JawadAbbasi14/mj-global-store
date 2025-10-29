# orders/views.py
from django.shortcuts import redirect, render
from .models import Order
from cart.models import Cart

def create_order(request):
    if not request.user.is_authenticated:
        return redirect('login_view')

    # ✅ Use get_or_create_cart to ensure merged cart
    cart = Cart.get_or_create_cart(request)

    total = cart.total_price
    print(f"DEBUG: Creating order with total = {total}")  # Should print 2700.00

    # Create order and capture its ID
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        payment_method="COD",
        payment_status=False
    )

    # ✅ Redirect with order ID
    return redirect('payment', order_id=order.id)

# orders/views.py
def Payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        cart = Cart.objects.get(user=request.user, ordered=False, is_active=True)
    except (Order.DoesNotExist, Cart.DoesNotExist):
        return render(request, 'orders/error.html', {'message': 'Order or cart not found'})

    return render(request, 'orders/orders.html', {'order': order, 'cart': cart})
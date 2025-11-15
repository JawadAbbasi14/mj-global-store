# payment/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from orders.models import Order
from cart.models import Cart


@login_required
def payment_method(request):
    if request.method == "POST":
        selected_method = request.POST.get('method')
        if selected_method not in ['easypaisa', 'jazzcash', 'cod']:
            return redirect('payment_failed')

        # 🧩 Active cart check
        cart = Cart.objects.filter(user=request.user, is_active=True, ordered=False).first()
        if not cart or not cart.items.exists():
            return redirect('payment_failed')

        # 🧩 Total calculate
        total_amount = sum(item.unit_price * item.quantity for item in cart.items.all())

        # 🧩 Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            payment_method=selected_method,
            payment_status=(selected_method == 'cod')
        )

        # 🧩 Mark cart as ordered
        cart.ordered = True
        cart.save()

        # 🧩 Redirect accordingly
        if selected_method == 'cod':
            return redirect('payment_success')
        else:
            return redirect('payment_gateway')

    # ⚙️ For GET (page render)
    order = Order.objects.filter(user=request.user).order_by('-id').first()
    if not order:
        return redirect('create_order')

    return render(request, 'payment/payment_select.html', {'order': order})

# Success page view
def payment_success(request):
    return render(request, 'payment/payment_success.html')


# Failure page view
def payment_failed(request):
    return render(request, 'payment/payment_failed.html')


# Gateway placeholder (for future integration)
@login_required
def payment_gateway(request):
    # Later: send to Easypaisa/JazzCash API
    return render(request, 'payment/gateway.html')
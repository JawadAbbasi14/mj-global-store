# payment/views.py
import logging
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from orders.models import Order
from cart.models import Cart

logger = logging.getLogger(__name__)


@login_required
def payment_method(request):
    if request.method == "POST":
        selected_method = request.POST.get('method')
        if selected_method not in ['easypaisa', 'jazzcash', 'cod']:
            return redirect('payment_failed')

        cart = Cart.objects.filter(user=request.user, is_active=True, ordered=False).first()
        if not cart or not cart.items.exists():
            return redirect('payment_failed')

        total_amount = sum(item.unit_price * item.quantity for item in cart.items.all())

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            payment_method=selected_method,
            payment_status=(selected_method == 'cod')
        )

        cart.ordered = True
        cart.save()

        if selected_method == 'cod':
            return redirect('payment_success')
        else:
            return redirect('payment_gateway')

    order = Order.objects.filter(user=request.user).order_by('-id').first()
    if not order:
        return redirect('create_order')
    return render(request, 'payment/payment_select.html', {'order': order})


@login_required
def payment_gateway(request):
    order = Order.objects.filter(user=request.user, payment_status=False).order_by('-id').first()
    if not order:
        return redirect('payment_failed')

    method = order.payment_method
    if method not in ['easypaisa', 'jazzcash']:
        return redirect('payment_failed')

    if not order.customer_phone:
        order.customer_phone = getattr(request.user.profile, 'phone', '')
    if not order.customer_email:
        order.customer_email = request.user.email
    order.save()

    # ✅ Convert to string to avoid JSON serialization error
    amount = str(order.total_amount)
    order_id = str(order.id)

    if method == 'easypaisa':
        payload = {
            "store_id": settings.EASYPASA_STORE_ID,
            "merchant_key": settings.EASYPASA_SECRET_KEY,
            "amount": amount,
            "order_id": order_id,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "postBackURL": settings.EASYPASA_CALLBACK_URL,  # ✅ Correct key
            "productDetail": "Online Order Payment",
            "transactionType": "MWALLET",
        }
        url = "https://easypay.easypaisa.com.pk/easypay/Index.jsf"  # ✅ No trailing spaces
        post_type = 'json'

    elif method == 'jazzcash':
        payload = {
            "merchant_id": settings.JAZZCASH_MERCHANT_ID,
            "password": settings.JAZZCASH_PASSWORD,
            "amount": amount,
            "bill_reference": f"ORDER-{order_id}",
            "description": "Order Payment",
            "return_url": settings.JAZZCASH_RETURN_URL,
        }
        url = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction"  # ✅ No spaces
        post_type = 'data'

    try:
        if post_type == 'json':
            response = requests.post(url, json=payload, timeout=10)
        else:
            response = requests.post(url, data=payload, timeout=10)
        json_data = response.json()
    except Exception as e:
        logger.error(f"Payment gateway error: {e}")
        return redirect('payment_failed')

    redirect_url = json_data.get("redirect_url") or json_data.get("pp_GatewayURL")
    if not redirect_url:
        logger.error(f"No redirect URL in response: {json_data}")
        return redirect('payment_failed')

    return redirect(redirect_url)


# -------------------------
# CALLBACKS (MUST be public, no login, CSRF exempt)
# -------------------------

@csrf_exempt
def easypaisa_callback(request):
    data = request.GET  # ✅ EasyPaisa uses GET
    order_id = data.get('order_id')
    status = data.get('status', '').lower()

    if not order_id:
        return redirect('payment_failed')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('payment_failed')

    if status == 'success':
        order.payment_status = True
        order.save()
        return redirect('payment_success')
    else:
        return redirect('payment_failed')


@csrf_exempt
def jazzcash_callback(request):
    data = request.GET
    response_code = data.get('pp_ResponseCode')
    bill_ref = data.get('pp_BillReference')

    if response_code != '000' or not bill_ref:
        return redirect('payment_failed')

    try:
        if not bill_ref.startswith('ORDER-'):
            return redirect('payment_failed')
        order_id = int(bill_ref.split('-')[1])
        order = Order.objects.get(id=order_id)
    except (ValueError, Order.DoesNotExist):
        return redirect('payment_failed')

    order.payment_status = True
    order.save()
    return redirect('payment_success')


def payment_success(request):
    return render(request, 'payment/payment_success.html')


def payment_failed(request):
    return render(request, 'payment/payment_failed.html')
# payment/views.py - Updated version
import logging
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from orders.models import Order
from cart.models import Cart
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def payment_method(request):
    if request.method == "POST":
        selected_method = request.POST.get('method')
        if selected_method not in ['easypaisa', 'jazzcash', 'cod']:
            return redirect(reverse('payment_failed') + '?reason=invalid_method')

        cart = Cart.objects.filter(user=request.user, is_active=True, ordered=False).first()
        if not cart or not cart.items.exists():
            return redirect(reverse('payment_failed') + '?reason=empty_cart')

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
        return redirect(reverse('payment_failed') + '?reason=order_not_found')

    method = order.payment_method
    if method not in ['easypaisa', 'jazzcash']:
        return redirect(reverse('payment_failed') + '?reason=invalid_gateway')

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
            "postBackURL": settings.EASYPASA_CALLBACK_URL,
            "productDetail": "Online Order Payment",
            "transactionType": "MWALLET",
        }
        url = "https://easypay.easypaisa.com.pk/easypay/Index.jsf"
        post_type = 'json'
        gateway_name = "EasyPaisa"

    elif method == 'jazzcash':
        payload = {
            "merchant_id": settings.JAZZCASH_MERCHANT_ID,
            "password": settings.JAZZCASH_PASSWORD,
            "amount": amount,
            "bill_reference": f"ORDER-{order_id}",
            "description": "Order Payment",
            "return_url": settings.JAZZCASH_RETURN_URL,
        }
        url = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction"
        post_type = 'data'
        gateway_name = "JazzCash"

    try:
        if post_type == 'json':
            response = requests.post(url, json=payload, timeout=10)
        else:
            response = requests.post(url, data=payload, timeout=10)
        
        # Log gateway response for debugging
        logger.info(f"{gateway_name} Response Status: {response.status_code}")
        logger.info(f"{gateway_name} Response Content: {response.text[:200]}")
        
        json_data = response.json()
        
        # Check for specific gateway errors
        if method == 'easypaisa' and json_data.get('response_code') != '200':
            return redirect(reverse('payment_failed') + f'?reason=gateway_error&code={json_data.get("response_code")}&message={json_data.get("response_message", "Unknown error")}')
        
        if method == 'jazzcash' and json_data.get('pp_ResponseCode') != '000':
            return redirect(reverse('payment_failed') + f'?reason=gateway_error&code={json_data.get("pp_ResponseCode")}&message={json_data.get("pp_ResponseMessage", "Unknown error")}')
            
    except requests.exceptions.Timeout:
        return redirect(reverse('payment_failed') + '?reason=gateway_timeout')
    except requests.exceptions.ConnectionError:
        return redirect(reverse('payment_failed') + '?reason=network_error')
    except Exception as e:
        logger.error(f"Payment gateway error: {e}")
        return redirect(reverse('payment_failed') + f'?reason=gateway_exception&error={str(e)}')

    redirect_url = json_data.get("redirect_url") or json_data.get("pp_GatewayURL")
    if not redirect_url:
        logger.error(f"No redirect URL in response: {json_data}")
        return redirect(reverse('payment_failed') + '?reason=no_redirect_url')

    return redirect(redirect_url)


# -------------------------
# CALLBACKS (MUST be public, no login, CSRF exempt)
# -------------------------

@csrf_exempt
def easypaisa_callback(request):
    data = request.GET
    order_id = data.get('order_id')
    status = data.get('status', '').lower()
    response_code = data.get('response_code')
    response_message = data.get('response_message', 'No message')

    if not order_id:
        return redirect(reverse('payment_failed') + f'?reason=callback_error&code=NO_ORDER_ID&message=Order ID missing')

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect(reverse('payment_failed') + f'?reason=callback_error&code=ORDER_NOT_FOUND&message=Order {order_id} not found')

    if status == 'success' and response_code == '200':
        order.payment_status = True
        order.save()
        return redirect('payment_success')
    else:
        return redirect(reverse('payment_failed') + f'?reason=easypaisa_failed&code={response_code}&message={response_message}')


@csrf_exempt
def jazzcash_callback(request):
    data = request.GET
    response_code = data.get('pp_ResponseCode')
    bill_ref = data.get('pp_BillReference')
    response_message = data.get('pp_ResponseMessage', 'No message')
    transaction_id = data.get('pp_TxnRefNo')

    if response_code != '000' or not bill_ref:
        return redirect(reverse('payment_failed') + f'?reason=jazzcash_failed&code={response_code}&message={response_message}&txn={transaction_id}')

    try:
        if not bill_ref.startswith('ORDER-'):
            return redirect(reverse('payment_failed') + f'?reason=callback_error&code=INVALID_REF&message=Invalid bill reference')
        order_id = int(bill_ref.split('-')[1])
        order = Order.objects.get(id=order_id)
    except (ValueError, Order.DoesNotExist) as e:
        return redirect(reverse('payment_failed') + f'?reason=callback_error&code=ORDER_ERROR&message={str(e)}')

    order.payment_status = True
    order.save()
    return redirect('payment_success')


def payment_success(request):
    return render(request, 'payment/payment_success.html')


def payment_failed(request):
    # Extract error details from GET parameters
    reason = request.GET.get('reason', 'unknown')
    error_code = request.GET.get('code', '')
    error_message = request.GET.get('message', '')
    transaction_id = request.GET.get('txn', '')
    
    context = {
        'reason': reason,
        'error_code': error_code,
        'error_message': error_message,
        'transaction_id': transaction_id,
        'all_params': dict(request.GET)  # For debugging
    }
    
    # Log the failure for debugging
    logger.warning(f"Payment failed - Reason: {reason}, Code: {error_code}, Message: {error_message}")
    
    return render(request, 'payment/payment_failed.html', context)
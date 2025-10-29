# payment/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def payment_method(request):
    if request.method == "POST":
        selected_method = request.POST.get('method')
        # Yahan tum order fetch karoge (jaise session/cart se)
        # Aur phir COD/EasyPaisa logic chalao

        if selected_method in ['easypaisa', 'jazzcash', 'cod']:
            # Example: Save to DB ya redirect to confirmation
            # For now, just print or redirect to success
            return redirect('payment_success')  # ya koi aur URL name

    # GET request → form dikhao
    return render(request, 'payment/payment_select.html')
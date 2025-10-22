from django.http import HttpResponse
from .models import Order
from django.shortcuts import redirect,render


def Payment(request):
    order = Order.objects.filter(user=request.user).last()
   
    
    if order is not None:
         total_bill =order.total_amount
    else:
         total_bill=0
      

    return render(request,'orders/orders.html',{'orders':order,})
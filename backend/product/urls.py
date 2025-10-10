
from django.urls import path
from . import views

urlpatterns = [

      path("",views.product_list,name="products"),
      # path("mjcollections/",views.mjcollections,name='specialcollections')
]




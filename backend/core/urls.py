# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("product/", include("product.urls")),

    # root URL ko redirect kar do login page pe
    path("", lambda request: HttpResponseRedirect("product")),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from api_integration import payment


urlpatterns = [
    path("",include("home.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("product/", include("product.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
     # API Payment routes
    path('api_logic/payment/', include('api_logic.payment.urls')),
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



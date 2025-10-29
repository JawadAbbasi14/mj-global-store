# cart/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


# Replace with your real product model import if different:
from product.models import Products

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    ordered = models.BooleanField(default=False)   # agar order flow use karoge
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart(user={self.user})" if self.user else f"Cart(session={self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def add_product(self, product, qty=1):
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': 0, 'unit_price': getattr(product, 'price', 0)}
        )
        item.quantity += int(qty)
        item.unit_price = getattr(product, 'price', item.unit_price)  # snapshot price
        item.save()
        return item

    def remove_product(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()

    def set_quantity(self, product, qty):
        item = CartItem.objects.filter(cart=self, product=product).first()
        if not item: return None
        if int(qty) <= 0:
            item.delete()
            return None
        item.quantity = int(qty)
        item.save()
        return item

    def clear(self):
        self.items.all().delete()

    @classmethod
    def get_or_create_cart(cls, request):
        # ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        if request.user.is_authenticated:
            cart, _ = cls.objects.get_or_create(user=request.user, ordered=False)
            # merge session cart -> user cart (if exists)
            try:
                session_cart = cls.objects.get(session_key=session_key, ordered=False)
            except cls.DoesNotExist:
                session_cart = None
            if session_cart:
                for item in session_cart.items.all():
                    existing = cart.items.filter(product=item.product).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                session_cart.delete()
            return cart
        else:
            cart, _ = cls.objects.get_or_create(session_key=session_key, ordered=False)
            return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)   # snapshot price
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = str(self.product)
        if not self.unit_price:
            self.unit_price = getattr(self.product, 'price', 0)
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.unit_price * self.quantity


User = get_user_model()  # Best practice for user model

class CartAuthority(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)  # Agar Cart model same file mein nahi, toh quotes mein likho
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CartAuthority for {self.user.username} - {self.status}"
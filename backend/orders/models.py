from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ Sahi field
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    PAYMENT_CHOICES = [
    ('easypaisa', 'EasyPaisa'),
    ('jazzcash', 'JazzCash'),
    ('cod', 'Cash on Delivery'),
]

    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.total_amount}"

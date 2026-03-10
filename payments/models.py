from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('success', 'Успешно'),
        ('failed', 'Неудачно'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    card_last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'Платёж #{self.id} — {self.status}'


class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=20, unique=True)
    promo_code = models.CharField(max_length=20, blank=True, default='')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'

    def __str__(self):
        return f'Чек {self.receipt_number}'
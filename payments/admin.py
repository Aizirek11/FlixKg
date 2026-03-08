from django.contrib import admin
from django.contrib import admin
from .models import Payment, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'status', 'card_last4', 'created_at']
    list_filter = ['status']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment', 'created_at']
# Register your models here.

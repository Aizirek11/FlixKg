from django.urls import path
from .views import PayView, MyReceiptsView, ReceiptDetailView

urlpatterns = [
    path('pay/', PayView.as_view(), name='pay'),
    path('receipts/', MyReceiptsView.as_view(), name='my-receipts'),
    path('receipts/<str:receipt_number>/', ReceiptDetailView.as_view(), name='receipt-detail'),
]
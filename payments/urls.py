from django.urls import path
from .views import PayView, MyReceiptsView, ReceiptDetailView
from . import views

urlpatterns = [
    # API
    path('pay/', PayView.as_view(), name='pay'),
    path('receipts/', MyReceiptsView.as_view(), name='my-receipts'),
    path('receipts/<str:receipt_number>/', ReceiptDetailView.as_view(), name='receipt-detail'),

    # HTML страницы
    path('payment/<int:pk>/', views.payment_view, name='payment'),
    path('receipt/<str:receipt_number>/', views.receipt_view, name='receipt'),
    path('ticket/<int:pk>/pdf/', views.ticket_pdf_view, name='ticket-pdf'),
]
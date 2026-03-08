from django.urls import path
from .views import (
    HallListCreateView, HallDetailView,
    SeatListCreateView, SeatDetailView,
    SessionListCreateView, SessionDetailView,
    BookingCreateView, BookingCancelView,
    MyTicketsView, TicketDetailView
)

urlpatterns = [
    # Залы
    path('halls/', HallListCreateView.as_view(), name='hall-list'),
    path('halls/<int:pk>/', HallDetailView.as_view(), name='hall-detail'),

    # Места
    path('seats/', SeatListCreateView.as_view(), name='seat-list'),
    path('seats/<int:pk>/', SeatDetailView.as_view(), name='seat-detail'),

    # Сеансы
    path('sessions/', SessionListCreateView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),

    # Бронирование
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),

    # Билеты
    path('tickets/', MyTicketsView.as_view(), name='my-tickets'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
]
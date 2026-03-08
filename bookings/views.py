from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hall, Seat, Session, Booking, Ticket
from .serializers import (
    HallSerializer, HallCreateSerializer, SeatSerializer,
    SessionSerializer, SessionCreateSerializer,
    BookingSerializer, TicketSerializer
)
from payments.utils import generate_ticket
from notifications.models import Notification


class HallListCreateView(generics.ListCreateAPIView):
    queryset = Hall.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HallCreateSerializer
        return HallSerializer


class HallDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hall.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HallCreateSerializer
        return HallSerializer


class SeatListCreateView(generics.ListCreateAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAdminUser]


class SeatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAdminUser]


class SessionListCreateView(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SessionCreateSerializer
        return SessionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SessionCreateSerializer
        return SessionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        return booking


class BookingCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.user != request.user:
            raise PermissionDenied('Это не ваша бронь!')
        if booking.status == 'paid':
            return Response({'error': 'Оплаченную бронь нельзя отменить!'}, status=400)
        booking.status = 'cancelled'
        booking.save()
        return Response({'message': 'Бронь отменена!'})


class MyTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            booking__user=self.request.user
        ).order_by('-created_at')


class TicketDetailView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        if ticket.booking.user != self.request.user:
            raise PermissionDenied('Это не ваш билет!')
        return ticket


def seat_selection_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    seats = Seat.objects.filter(hall=session.hall).order_by('row', 'number')
    booked_seats = list(
        session.bookings.filter(status__in=['pending', 'paid'])
        .values_list('seats__id', flat=True)
    )
    return render(request, 'bookings/seat_selection.html', {
        'session': session,
        'seats': seats,
        'booked_seats': booked_seats,
    })


@login_required
def create_booking_view(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        seat_ids_str = request.POST.get('seat_ids', '')

        if not seat_ids_str:
            messages.error(request, 'Выберите места!')
            return redirect(f'/sessions/{session_id}/seats/')

        seat_ids = [int(x) for x in seat_ids_str.split(',') if x]
        session = get_object_or_404(Session, pk=session_id)
        seats = Seat.objects.filter(id__in=seat_ids)

        total = 0
        for seat in seats:
            if seat.seat_type == 'vip':
                total += session.price_vip
            else:
                total += session.price_standard

        booking = Booking.objects.create(
            user=request.user,
            session=session,
            total_price=total
        )
        booking.seats.set(seats)
        return redirect(f'/payment/{booking.id}/')

    return redirect('/')
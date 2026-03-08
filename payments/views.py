from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics
from bookings.models import Booking, Ticket
from .models import Payment, Receipt
from .serializers import PaymentSerializer, ReceiptSerializer
from .utils import generate_ticket, generate_receipt_number
from notifications.models import Notification

User = get_user_model()


class PayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        booking = get_object_or_404(Booking, id=data['booking_id'], user=request.user)

        if booking.status != 'pending':
            return Response({'error': 'Эта бронь уже обработана!'}, status=400)

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='success',
            card_last4=data['card_number'][-4:]
        )

        booking.status = 'paid'
        booking.save()

        ticket = generate_ticket(booking)

        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=generate_receipt_number()
        )

        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f'{request.user.username} купил билет на "{booking.session.movie.title}" '
                        f'({booking.session.date} {booking.session.start_time}) — '
                        f'{booking.total_price} сом'
            )

        return Response({
            'message': 'Оплата прошла успешно!',
            'ticket_number': ticket.ticket_number,
            'receipt_number': receipt.receipt_number,
        })


class MyReceiptsView(generics.ListAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Receipt.objects.filter(
            payment__booking__user=self.request.user
        ).order_by('-created_at')


class ReceiptDetailView(generics.RetrieveAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            Receipt,
            receipt_number=self.kwargs['receipt_number'],
            payment__booking__user=self.request.user
        )


@login_required
def payment_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        card_number = request.POST.get('card_number', '').replace(' ', '')
        card_expiry = request.POST.get('card_expiry', '')
        card_cvv = request.POST.get('card_cvv', '')

        card_clean = card_number.replace(' ', '').replace('-', '')
        if not card_clean.isdigit() or len(card_clean) != 16:
            messages.error(request, 'Введите 16 цифр карты!')
            return redirect(f'/payment/{pk}/')

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='success',
            card_last4=card_number[-4:]
        )

        booking.status = 'paid'
        booking.save()

        ticket = generate_ticket(booking)

        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=generate_receipt_number()
        )

        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f'{request.user.username} купил билет на "{booking.session.movie.title}" '
                        f'({booking.session.date} {booking.session.start_time}) — '
                        f'{booking.total_price} сом'
            )

        return redirect(f'/receipt/{receipt.receipt_number}/')

    return render(request, 'payments/payment.html', {'booking': booking})


@login_required
def receipt_view(request, receipt_number):
    receipt = get_object_or_404(
        Receipt,
        receipt_number=receipt_number,
        payment__booking__user=request.user
    )
    return render(request, 'payments/receipt.html', {'receipt': receipt})


@login_required
def ticket_pdf_view(request, pk):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from django.http import HttpResponse
    import io

    ticket = get_object_or_404(Ticket, pk=pk, booking__user=request.user)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFillColorRGB(0, 0, 0)
    p.rect(0, 0, 595, 842, fill=1)

    p.setFillColorRGB(0.9, 0.04, 0.08)
    p.setFont("Helvetica-Bold", 32)
    p.drawString(50, 750, "FlixKG")

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, 700, ticket.booking.session.movie.title)

    p.setFont("Helvetica", 14)
    p.drawString(50, 660, f"Дата: {ticket.booking.session.date}")
    p.drawString(50, 635, f"Время: {ticket.booking.session.start_time}")
    p.drawString(50, 610, f"Зал: {ticket.booking.session.hall.name}")

    seats = ticket.booking.seats.all()
    seats_str = ', '.join([f"Р{s.row}М{s.number}" for s in seats])
    p.drawString(50, 585, f"Места: {seats_str}")
    p.drawString(50, 560, f"Сумма: {ticket.booking.total_price} сом")
    p.drawString(50, 535, f"Билет: {ticket.ticket_number}")

    if ticket.qr_code:
        p.drawImage(ticket.qr_code.path, 400, 500, width=150, height=150)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.pdf"'
    return response
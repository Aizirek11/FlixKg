from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics
from bookings.models import Booking, Ticket
from .models import Payment, Receipt
from .serializers import PaymentSerializer, ReceiptSerializer
from .utils import generate_ticket, generate_receipt_number
from notifications.models import Notification
from decimal import Decimal

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

        Notification.objects.create(
            recipient=request.user,
            message=f'✅ Вы успешно купили билет на "{booking.session.movie.title}" '
                    f'({booking.session.date} {booking.session.start_time}) — '
                    f'{booking.total_price} сом. Билет №{ticket.ticket_number}'
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
def check_promo_view(request):
    code = request.GET.get('code', '').strip().upper()
    username = request.GET.get('username', '').strip()

    if not code:
        return JsonResponse({'valid': False, 'error': 'Промокод не указан'})

    try:
        User.objects.get(username=username, pensioner_promo_code=code, is_pensioner=True)
        return JsonResponse({'valid': True})
    except User.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Промокод недействителен или не принадлежит вам'})


@login_required
def check_promo_view_page(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        promo_code = request.POST.get('promo_code', '').strip().upper()
        try:
            User.objects.get(
                username=request.user.username,
                pensioner_promo_code=promo_code,
                is_pensioner=True
            )
            request.session[f'promo_{pk}'] = promo_code
            messages.success(request, '✅ Промокод применён! Скидка 20%')
        except User.DoesNotExist:
            request.session[f'promo_{pk}'] = ''
            messages.error(request, '❌ Промокод недействителен!')

    return redirect(f'/payment/{pk}/')


@login_required
def payment_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if booking.status == 'paid':
        messages.error(request, 'Эта бронь уже оплачена!')
        return redirect('/')

    promo_code = request.session.get(f'promo_{pk}', '')
    discount_amount = 0
    final_price = booking.total_price

    if promo_code:
        try:
            User.objects.get(
                username=request.user.username,
                pensioner_promo_code=promo_code,
                is_pensioner=True
            )
            discount_amount = round(booking.total_price * Decimal('0.20'), 2)
            final_price = round(booking.total_price - discount_amount, 2)
        except User.DoesNotExist:
            promo_code = ''
            request.session[f'promo_{pk}'] = ''

    if request.method == 'POST' and 'pay' in request.POST:
        card_number = request.POST.get('card_number', '').replace(' ', '').replace('-', '')

        if not card_number.isdigit() or len(card_number) != 16:
            messages.error(request, 'Введите 16 цифр карты!')
            return redirect(f'/payment/{pk}/')

        Payment.objects.filter(booking=booking).delete()

        payment = Payment.objects.create(
            booking=booking,
            amount=final_price,
            status='success',
            card_last4=card_number[-4:]
        )

        booking.status = 'paid'
        booking.save()

        ticket = generate_ticket(booking)

        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=generate_receipt_number(),
            promo_code=promo_code,
            discount_amount=discount_amount,
            original_amount=booking.total_price if promo_code else 0,
        )

        request.session[f'promo_{pk}'] = ''

        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                message=f'{request.user.username} купил билет на "{booking.session.movie.title}" '
                        f'({booking.session.date} {booking.session.start_time}) — {final_price} сом'
            )

        Notification.objects.create(
            recipient=request.user,
            message=f'✅ Вы успешно купили билет на "{booking.session.movie.title}" '
                    f'({booking.session.date} {booking.session.start_time}) — '
                    f'{final_price} сом. Билет №{ticket.ticket_number}'
        )

        return redirect(f'/receipt/{receipt.receipt_number}/')

    return render(request, 'payments/payment.html', {
        'booking': booking,
        'promo_code': promo_code,
        'discount_amount': discount_amount,
        'final_price': final_price if promo_code else None,
    })


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
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from django.http import HttpResponse
    import os
    import io

    ticket = get_object_or_404(Ticket, pk=pk, booking__user=request.user)

    font_path = os.path.join(settings.BASE_DIR, 'DejaVuSans.ttf')
    font_bold_path = os.path.join(settings.BASE_DIR, 'DejaVuSans-Bold.ttf')

    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_bold_path))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFillColorRGB(0, 0, 0)
    p.rect(0, 0, 595, 842, fill=1)

    p.setFillColorRGB(0.9, 0.04, 0.08)
    p.setFont('DejaVu-Bold', 36)
    p.drawString(50, 760, 'FlixKG')

    p.setFillColorRGB(1, 1, 1)
    p.setFont('DejaVu-Bold', 22)
    p.drawString(50, 710, ticket.booking.session.movie.title)

    p.setFont('DejaVu', 14)
    p.drawString(50, 670, f'Дата: {ticket.booking.session.date}')
    p.drawString(50, 645, f'Время: {ticket.booking.session.start_time}')
    p.drawString(50, 620, f'Зал: {ticket.booking.session.hall.name}')

    p.drawString(50, 595, 'Места:')
    seats = ticket.booking.seats.all()
    y = 572
    for s in seats:
        seat_type_ru = 'VIP' if s.seat_type == 'vip' else 'Обычное'
        p.drawString(70, y, f'Ряд {s.row},  Место {s.number}  — {seat_type_ru}')
        y -= 22

    p.drawString(50, y - 15, f'Сумма: {ticket.booking.total_price} сом')

    p.setStrokeColorRGB(0.9, 0.04, 0.08)
    p.setLineWidth(2)
    p.line(50, y - 35, 545, y - 35)

    p.setFont('DejaVu', 12)
    p.setFillColorRGB(0.7, 0.7, 0.7)
    p.drawString(50, y - 55, f'Билет №: {ticket.ticket_number}')

    if ticket.qr_code:
        p.drawImage(ticket.qr_code.path, 390, 580, width=160, height=160)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.pdf"'
    return response
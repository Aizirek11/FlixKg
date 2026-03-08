import qrcode
import uuid
import os
from io import BytesIO
from django.core.files import File
from django.conf import settings


def generate_ticket_number():
    return f'TKT-{uuid.uuid4().hex[:8].upper()}'


def generate_receipt_number():
    return f'RCP-{uuid.uuid4().hex[:8].upper()}'


def generate_qr_code(ticket):
    data = f'Билет: {ticket.ticket_number} | Фильм: {ticket.booking.session.movie.title} | {ticket.booking.session.date} {ticket.booking.session.start_time}'
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    filename = f'qr_{ticket.ticket_number}.png'
    ticket.qr_code.save(filename, File(buffer), save=True)


def generate_ticket(booking):
    from bookings.models import Ticket
    ticket = Ticket.objects.create(
        booking=booking,
        ticket_number=generate_ticket_number()
    )
    generate_qr_code(ticket)
    return ticket
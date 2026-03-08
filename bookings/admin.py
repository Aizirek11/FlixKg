from django.contrib import admin
from django.contrib import admin
from .models import Hall, Seat, Session, Booking, Ticket


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_rows', 'total_seats']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['hall', 'row', 'number', 'seat_type']
    list_filter = ['hall', 'seat_type']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['movie', 'hall', 'date', 'start_time', 'price_standard', 'price_vip']
    list_filter = ['date', 'movie']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session', 'status', 'total_price', 'created_at']
    list_filter = ['status']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'booking', 'created_at']
# Register your models here.

from django.db import models
from django.db import models
from movies.models import Movie
from users.models import User


class Hall(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название зала')
    total_rows = models.PositiveIntegerField(verbose_name='Количество рядов')
    total_seats = models.PositiveIntegerField(verbose_name='Мест в ряду')
    address = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

    def __str__(self):
        return self.name


class Seat(models.Model):
    SEAT_TYPES = [
        ('standard', 'Обычное'),
        ('vip', 'VIP'),
    ]
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats')
    row = models.PositiveIntegerField(verbose_name='Ряд')
    number = models.PositiveIntegerField(verbose_name='Место')
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES, default='standard')

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        unique_together = ['hall', 'row', 'number']

    def __str__(self):
        return f'{self.hall.name} | Ряд {self.row} | Место {self.number} ({self.seat_type})'


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата')
    start_time = models.TimeField(verbose_name='Время начала')
    price_standard = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена обычного')
    price_vip = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена VIP')

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'

    def __str__(self):
        return f'{self.movie.title} | {self.date} {self.start_time}'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='bookings')
    seats = models.ManyToManyField(Seat, verbose_name='Места')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'

    def __str__(self):
        return f'Бронь #{self.id} — {self.user.username}'


class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    ticket_number = models.CharField(max_length=20, unique=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'

    def __str__(self):
        return f'Билет {self.ticket_number}'

    def is_active(self):
        from django.utils import timezone
        import datetime
        session = self.booking.session
        session_datetime = datetime.datetime.combine(session.date, session.start_time)
        session_datetime = timezone.make_aware(session_datetime)
        return timezone.now() < session_datetime
# Create your models here.

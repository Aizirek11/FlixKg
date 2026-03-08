from rest_framework import serializers
from .models import Hall, Seat, Session, Booking, Ticket
from movies.serializers import MovieListSerializer


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'seat_type']


class HallSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Hall
        fields = ['id', 'name', 'total_rows', 'total_seats', 'seats']


class HallCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = ['id', 'name', 'total_rows', 'total_seats']


class SessionSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    hall = HallSerializer(read_only=True)
    booked_seats = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'movie', 'hall', 'date', 'start_time',
                  'price_standard', 'price_vip', 'booked_seats']

    def get_booked_seats(self, obj):
        booked = obj.bookings.filter(status__in=['pending', 'paid']).values_list('seats__id', flat=True)
        return list(booked)


class SessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    session_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'session_id', 'seat_ids', 'status', 'total_price', 'created_at']
        read_only_fields = ['status', 'total_price', 'created_at']

    def validate(self, attrs):
        session_id = attrs.get('session_id')
        seat_ids = attrs.get('seat_ids')

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            raise serializers.ValidationError('Сеанс не найден!')

        booked_seats = session.bookings.filter(
            status__in=['pending', 'paid']
        ).values_list('seats__id', flat=True)

        for seat_id in seat_ids:
            if seat_id in booked_seats:
                raise serializers.ValidationError(f'Место {seat_id} уже занято!')

        attrs['session'] = session
        return attrs

    def create(self, validated_data):
        seat_ids = validated_data.pop('seat_ids')
        validated_data.pop('session_id', None)
        session = validated_data.pop('session')

        seats = Seat.objects.filter(id__in=seat_ids)
        total = 0
        for seat in seats:
            if seat.seat_type == 'vip':
                total += session.price_vip
            else:
                total += session.price_standard

        booking = Booking.objects.create(
            session=session,
            total_price=total,
            **validated_data
        )
        booking.seats.set(seats)
        return booking


class TicketSerializer(serializers.ModelSerializer):
    movie = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    session_time = serializers.SerializerMethodField()
    hall = serializers.SerializerMethodField()
    seats = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'qr_code', 'movie', 'session_date',
                  'session_time', 'hall', 'seats', 'total_price', 'is_active', 'created_at']

    def get_movie(self, obj):
        return obj.booking.session.movie.title

    def get_session_date(self, obj):
        return obj.booking.session.date

    def get_session_time(self, obj):
        return obj.booking.session.start_time

    def get_hall(self, obj):
        return obj.booking.session.hall.name

    def get_seats(self, obj):
        return [
            {'row': s.row, 'number': s.number, 'type': s.seat_type}
            for s in obj.booking.seats.all()
        ]

    def get_total_price(self, obj):
        return obj.booking.total_price

    def get_is_active(self, obj):
        return obj.is_active()
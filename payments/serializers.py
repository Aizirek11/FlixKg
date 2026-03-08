from rest_framework import serializers
from .models import Payment, Receipt


class PaymentSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    card_number = serializers.CharField(max_length=16, min_length=16)
    card_expiry = serializers.CharField(max_length=5)
    card_cvv = serializers.CharField(max_length=3, min_length=3)

    def validate_card_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('Номер карты должен содержать только цифры!')
        return value

    def validate_card_cvv(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('CVV должен содержать только цифры!')
        return value


class ReceiptSerializer(serializers.ModelSerializer):
    movie = serializers.SerializerMethodField()
    session_date = serializers.SerializerMethodField()
    session_time = serializers.SerializerMethodField()
    hall = serializers.SerializerMethodField()
    seats = serializers.SerializerMethodField()
    seats_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = [
            'receipt_number', 'created_at', 'movie', 'session_date',
            'session_time', 'hall', 'seats', 'seats_count',
            'total_price', 'payment_status'
        ]

    def get_movie(self, obj):
        return obj.payment.booking.session.movie.title

    def get_session_date(self, obj):
        return obj.payment.booking.session.date

    def get_session_time(self, obj):
        return obj.payment.booking.session.start_time

    def get_hall(self, obj):
        return obj.payment.booking.session.hall.name

    def get_seats(self, obj):
        seats = obj.payment.booking.seats.all()
        return [
            {
                'row': s.row,
                'number': s.number,
                'type': s.seat_type,
                'price': str(
                    obj.payment.booking.session.price_vip
                    if s.seat_type == 'vip'
                    else obj.payment.booking.session.price_standard
                )
            }
            for s in seats
        ]

    def get_seats_count(self, obj):
        return obj.payment.booking.seats.count()

    def get_total_price(self, obj):
        return obj.payment.amount

    def get_payment_status(self, obj):
        return obj.payment.get_status_display()
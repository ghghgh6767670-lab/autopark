from rest_framework import serializers
from .models import Vehicle, Booking

class VehicleSerializer(serializers.ModelSerializer):
    price_per_day = serializers.DecimalField(source="price.base_per_day", max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Vehicle
        fields = ["id","title","type","transmission","fuel","seats","location","features","price_per_day","is_active"]

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["vehicle","date_from","date_to"]

    def validate(self, data):
        # TODO: проверить доступность авто и пересечение интервалов
        return data

    def create(self, validated):
        vehicle = validated["vehicle"]
        days = (validated["date_to"] - validated["date_from"]).days or 1
        total = days * vehicle.price.base_per_day
        return Booking.objects.create(
            user=self.context["request"].user,
            total_price=total,
            status="pending_payment",
            **validated
        )
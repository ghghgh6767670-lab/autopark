import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class VehicleType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Тип транспорта"))

    class Meta:
        verbose_name = _("Тип транспорта")
        verbose_name_plural = _("Типы транспорта")

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Особенность")
        verbose_name_plural = _("Особенности")


class Location(models.Model):
    city = models.CharField(max_length=80, verbose_name=_('Город'))
    address = models.CharField(max_length=200, blank=True, verbose_name=_('Адрес'))

    def __str__(self):
        return f"{self.city}, {self.address}"

    class Meta:
        verbose_name = _("Адрес")
        verbose_name_plural = _("Адресы")


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    title = models.CharField(max_length=120)
    plate = models.CharField(max_length=16, unique=True)
    transmission = models.CharField(max_length=20, choices=[("AT", "AT"), ("MT", "MT")])
    fuel = models.CharField(
        max_length=20,
        choices=[("petrol", _("Бензин")), ("diesel", _("Дизель")), ("hybrid", _("Гибрид")), ("ev", _("Электро"))]
    )
    seats = models.PositiveSmallIntegerField(default=5)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    features = models.ManyToManyField(Feature, blank=True)
    is_active = models.BooleanField(default=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title

    def get_price_for_dates(self, start, end):
        days = (end - start).days + 1
        return (self.price_per_day * Decimal(days)).quantize(Decimal("0.01"))

    def is_available(self, start_date, end_date):
        # Проверяем уже существующие брони с оплатой или ожидающие оплату
        overlapping_bookings = self.bookings.filter(
            status__in=["pending_payment", "paid"],
            date_from__lte=end_date,
            date_to__gte=start_date
        )
        return not overlapping_bookings.exists()

    class Meta:
        verbose_name = _("Транспортное средство")
        verbose_name_plural = _("Транспортные средствы")

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicles/")

    def __str__(self):
        return f"Фото для {self.vehicle}"


class VehicleAvailability(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="availabilities")
    date_from = models.DateField()
    date_to = models.DateField()
    reason = models.CharField(max_length=120, blank=True)  # maintenance/hold

    class Meta:
        verbose_name = _("Недоступность авто")
        verbose_name_plural = _("Недоступности авто")

    def __str__(self):
        return f"{self.vehicle} недоступен с {self.date_from} по {self.date_to}"


class Booking(models.Model):
    STATUS = [
        ("new", "Новый"),
        ("pending_payment", "Ожидает оплаты"),
        ("paid", "Оплачен"),
        ("canceled", "Отменён"),
        ("completed", "Завершён"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='bookings')
    date_from = models.DateField()
    date_to = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Бронирование")
        verbose_name_plural = _("Бронирования")
        indexes = [models.Index(fields=["vehicle", "date_from", "date_to"])]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_to__gte=models.F("date_from")),
                name="booking_valid_dates"
            )
        ]

    def __str__(self):
        return f"Бронь {self.vehicle} {self.date_from}–{self.date_to}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.vehicle.get_price_for_dates(self.date_from, self.date_to)
        super().save(*args, **kwargs)


class Payment(models.Model):
    STATUS = [
        ("requires_action", "Требует действия"),
        ("succeeded", "Успешно"),
        ("failed", "Ошибка"),
        ("refunded", "Возврат"),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=40)  # stripe/paybox/...
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="KGS")
    status = models.CharField(max_length=20, choices=STATUS)
    provider_intent_id = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} - {self.amount} {self.currency} ({self.status})"

    class Meta:
        verbose_name = _("Оплата")
        verbose_name_plural = _("Оплаты")


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)  # один отзыв на бронь
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1..5
    text = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Обзор")
        verbose_name_plural = _("Обзоры")
        unique_together = ("user", "vehicle")  # нельзя дважды отзыв на одно авто

    def __str__(self):
        return f"Отзыв {self.user} - {self.vehicle}"


class RentalPolicy(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    rules = models.TextField(verbose_name="Условия проката")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Условие проката")
        verbose_name_plural = _("Условия проката")

    def __str__(self):
        return self.title

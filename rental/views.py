import json
import uuid
from datetime import timedelta, datetime
from decimal import Decimal

from django.contrib import messages
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import VehicleSerializer, BookingCreateSerializer

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle, Booking, Payment
from .forms import BookingForm, DemoPaymentForm


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.filter(is_active=True).select_related("price","type","location").prefetch_related("features")
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["type","transmission","fuel","location"]
    search_fields = ["title","plate"]

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingCreateSerializer  # для краткости

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("vehicle")


def home(request):
    vehicles = Vehicle.objects.filter(is_active=True).order_by('-id')[:6]
    return render(request, 'rental/base.html', {'vehicles': vehicles})

def vehicles_list(request):
    vehicles = Vehicle.objects.filter(is_active=True)

    query = request.GET.get('q')
    if query:
        vehicles = vehicles.filter(title__icontains=query)  # поиск по названию авто

    return render(request, 'rental/home.html', {'vehicles': vehicles})

def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    return render(request, 'rental/vehicle_detail.html', {'vehicle': vehicle})


@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).select_related("vehicle")
    return render(request, "rental/profile.html", {
        "bookings": bookings,
        "user": request.user
    })


@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "provider": "demo",
            "amount": booking.total_price,
            "currency": "KGS",
            "status": "requires_action",
            "provider_intent_id": str(uuid.uuid4())
        }
    )

    if request.method == "POST":
        form = DemoPaymentForm(request.POST)
        if form.is_valid():
            # --- демо-логика: симулируем ответ провайдера ---
            card = form.cleaned_data["card_number"]
            # простое правило: если заканчивается на 4242 — успех, иначе — decline
            if card.endswith("4242"):
                payment.status = "succeeded"
                payment.provider_intent_id = str(uuid.uuid4())
                payment.provider_response = "demo_approved"
                payment.save()
                messages.success(request, "Оплата прошла успешно (демо).")
                return redirect("profile")  # поменяй имя если у тебя другое
            else:
                payment.status = "failed"
                payment.provider_response = "demo_declined"
                payment.save()
                messages.error(request, "Платёж отклонён (демо). Используйте тестовую карту 4242 4242 4242 4242.")
                return render(request, "rental/payment_page.html", {"form": form, "booking": booking, "payment": payment})
    else:
        form = DemoPaymentForm()

    return render(request, "rental/payment_page.html", {"form": form, "booking": booking, "payment": payment})


@login_required
def create_booking(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # собираем все занятые даты для текущего автомобиля
    booked_dates = []
    bookings = Booking.objects.filter(vehicle=vehicle, status__in=["pending_payment", "paid"])
    for b in bookings:
        current = b.date_from
        while current <= b.date_to:
            booked_dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            # проверка занятости
            conflict = any(
                date_from <= datetime.strptime(d, "%Y-%m-%d").date() <= date_to
                for d in booked_dates
            )
            if conflict:
                form.add_error(None, "Автомобиль недоступен на выбранные даты")
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.vehicle = vehicle
                booking.total_price = vehicle.get_price_for_dates(date_from, date_to)
                booking.status = "pending_payment"
                booking.save()
                return redirect('payment_page', booking.id)
    else:
        form = BookingForm()

    return render(request, "rental/booking_form.html", {
        "form": form,
        "vehicle": vehicle,
        "booked_dates": json.dumps(booked_dates)
    })
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    Vehicle, VehicleType, Feature, Location,
    VehicleAvailability, Booking, Payment, Review, RentalPolicy, VehicleImage
)
from django.utils.translation import gettext_lazy as _


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(VehicleType)
class VehicleTypeAdmin(TranslationAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
    verbose_name = _("Тип транспорта")
    verbose_name_plural = _("Типы транспорта")


@admin.register(Feature)
class FeatureAdmin(TranslationAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
    verbose_name = _("Особенность")
    verbose_name_plural = _("Особенности")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "address")
    search_fields = ("city", "address")
    verbose_name = _("Локация")
    verbose_name_plural = _("Локации")


class VehicleAvailabilityInline(admin.TabularInline):
    model = VehicleAvailability
    extra = 1
    fields = ("date_from", "date_to", "reason")
    verbose_name = _("Недоступность")
    verbose_name_plural = _("Недоступности")


@admin.register(Vehicle)
class VehicleAdmin(TranslationAdmin):
    list_display = ("title", "type", "plate", "seats", "location", "is_active", "price_per_day", "deposit")
    list_filter = ("type", "transmission", "fuel", "is_active", "location")
    search_fields = ("title", "plate", "type__name", "location__city")
    ordering = ("title",)
    autocomplete_fields = ("type", "location")
    filter_horizontal = ("features",)
    inlines = [VehicleAvailabilityInline, VehicleImageInline]

    fieldsets = (
        (_("Основная"), {"fields": ("title", "type", "plate", "is_active", "price_per_day", "deposit")}),
        (_("Характеристики"), {"fields": ("transmission", "fuel", "seats", "features")}),
        (_("Локация"), {"fields": ("location",)}),
    )


@admin.register(VehicleAvailability)
class VehicleAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "date_from", "date_to", "reason")
    list_filter = ("vehicle", "date_from", "date_to")
    search_fields = ("vehicle__title", "reason")
    autocomplete_fields = ("vehicle",)
    verbose_name = _("Недоступность транспорта")
    verbose_name_plural = _("Недоступности транспорта")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "user", "date_from", "date_to", "total_price", "status", "created_at")
    list_filter = ("status", "vehicle")
    search_fields = ("vehicle__title", "user__email", "user__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("vehicle", "user")
    ordering = ("-created_at",)
    verbose_name = _("Бронирование")
    verbose_name_plural = _("Бронирования")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "provider", "amount", "currency", "status", "created_at", "updated_at")
    list_filter = ("provider", "status")
    search_fields = ("booking__id", "provider_intent_id")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("booking",)
    verbose_name = _("Оплата")
    verbose_name_plural = _("Оплаты")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "vehicle", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("user__username", "vehicle__title", "booking__id")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "vehicle")

    actions = ["approve_reviews"]

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _("Отмечено как одобренные: %(count)d") % {"count": updated})
    approve_reviews.short_description = _("Одобрить выбранные отзывы")


@admin.register(RentalPolicy)
class RentalPolicyAdmin(TranslationAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    verbose_name = _("Политика аренды")
    verbose_name_plural = _("Политики аренды")

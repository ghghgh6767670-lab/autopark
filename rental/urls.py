from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path('', views.home, name='home'),
    path('vehicles/', views.vehicles_list, name='vehicles'),
    path('vehicle/<uuid:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicle/<uuid:vehicle_id>/booking/', views.create_booking, name='create_booking'),
    path('profile/', views.profile, name='profile'),
    path('booking/<uuid:booking_id>/payment/', views.payment_page, name='payment_page'),
]

urlpatterns += router.urls
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from autopark.views import AuthView, CustomLoginView, CustomRegisterView, CustomLogoutView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('rental.urls')),
]

urlpatterns += [
    path('auth/', AuthView.as_view(), name='auth'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('accounts/', include('allauth.urls')),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('auth/social/', include('allauth.socialaccount.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
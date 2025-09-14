from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView
from autopark.forms import CustomLoginForm, CustomRegisterForm
from django.contrib.auth import logout, update_session_auth_hash, login
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/"
    client_class = OAuth2Client

class AuthView(View):
    template_name = 'auth/login_register.html'

    def get(self, request):
        # Передаем обе формы в контекст
        login_form = CustomLoginForm()
        register_form = CustomRegisterForm()
        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })


class CustomLoginView(View):
    template_name = 'auth/login_register.html'

    def post(self, request):
        login_form = CustomLoginForm(request.POST)
        register_form = CustomRegisterForm()

        if login_form.is_valid():
            login(request, login_form.get_user())
            return redirect('home')

        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })

    def get(self, request):
        return render(request, self.template_name, {
            'login_form': CustomLoginForm(),
            'register_form': CustomRegisterForm()
        })


class CustomRegisterView(View):
    template_name = 'auth/login_register.html'

    def post(self, request):
        register_form = CustomRegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')

        login_form = CustomLoginForm()
        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
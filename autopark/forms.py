from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'id': 'id_username'
        }),
        label=_("Email")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password-input',
            'placeholder': _('Введите пароль')
        }),
        label=_("Пароль")
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(_("Неверный email или пароль"))

            user = authenticate(username=user.username, password=password)
            if user is None:
                raise forms.ValidationError(_("Неверный email или пароль"))

            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)



class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'title@example.com'
        }),
        label=_("Email")
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("Пароль")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_("Повторите пароль")
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']   # username = email
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

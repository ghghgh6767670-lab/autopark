from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }


class DemoPaymentForm(forms.Form):
    card_number = forms.CharField(max_length=19, label="Номер карты", widget=forms.TextInput(attrs={
        "inputmode": "numeric", "placeholder": "4242 4242 4242 4242", "autocomplete": "cc-number", "class": "form-control"
    }))
    exp_month = forms.IntegerField(min_value=1, max_value=12, label="Месяц", widget=forms.NumberInput(attrs={
        "placeholder": "MM", "class": "form-control", "inputmode": "numeric"
    }))
    exp_year = forms.IntegerField(min_value=2025, max_value=2100, label="Год", widget=forms.NumberInput(attrs={
        "placeholder": "YYYY", "class": "form-control", "inputmode": "numeric"
    }))
    cvc = forms.CharField(max_length=4, label="CVC", widget=forms.PasswordInput(attrs={
        "placeholder": "CVC", "class": "form-control", "inputmode": "numeric", "autocomplete": "cc-csc"
    }))

    def clean_card_number(self):
        v = self.cleaned_data["card_number"].replace(" ", "")
        if not v.isdigit() or len(v) < 12:
            raise forms.ValidationError("Неверный номер карты")
        return v

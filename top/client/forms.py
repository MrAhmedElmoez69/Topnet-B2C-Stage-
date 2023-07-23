from django import forms
from .models import Client, ScoreParameters

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Client
        fields = ['username', 'first_name', 'last_name', 'CIN', 'phone_number', 'password']

class ScoreParametersForm(forms.ModelForm):
    class Meta:
        model = ScoreParameters
        fields = "__all__"

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide all fields by default
        for field in self.fields.values():
            field.widget = forms.HiddenInput()

    def show_fields_for_criteres(self, criteres):
        # Show relevant fields based on the selected value of 'criteres'
        if criteres == 'valeur_commerciale':
            self.fields['categorie_client'].widget = forms.Select()
            self.fields['offre'].widget = forms.Select()
            self.fields['debit'].widget = forms.Select()
            self.fields['engagement_contractuel'].widget = forms.Select()
        elif criteres == 'engagement_client':
            self.fields['anciennete'].widget = forms.Select()

# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Client

class ClientCreationForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ('username', 'CIN', 'phone_number', 'first_name', 'last_name', 'is_staff', 'password1', 'password2')

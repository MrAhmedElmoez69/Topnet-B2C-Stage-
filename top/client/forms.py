from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

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



class ClientCreationForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ('username', 'CIN', 'phone_number', 'first_name', 'last_name', 'is_staff', 'password1', 'password2')


class ValeurCommercialeInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.client:
            self.fields['valeur_commerciale'].queryset = ValeurCommerciale.objects.filter(client=self.instance.client)

class EngagementTopnetInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.client:
            self.fields['engagement_topnet'].queryset = EngagementTopnet.objects.filter(client=self.instance.client)

class EngagementClientInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.client:
            self.fields['engagement_client'].queryset = EngagementClient.objects.filter(client=self.instance.client)

class ComportementClientInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.client:
            self.fields['comportement_client'].queryset = ComportementClient.objects.filter(client=self.instance.client)
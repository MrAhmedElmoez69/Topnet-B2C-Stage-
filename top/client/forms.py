from django import forms
from .models import Client
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
class LoginForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('username','password')
    password = forms.CharField(widget=forms.PasswordInput) #lezem nzidouha sinon ywali texte yetchef par l user

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model() #champs obligatoir
        fields = [
            'phone_number',
            'CIN',
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        ] #champs obligatoir
    def save(self,commit=True):
        client = super(UserCreationForm, self).save(commit)
        return client
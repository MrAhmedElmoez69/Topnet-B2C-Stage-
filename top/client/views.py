from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.db import models
from .forms import *
from django.contrib.auth import authenticate, login

@login_required
def enter_score_parameters(request):
    client = request.user.client
    if request.method == 'POST':
        # Récupérer les paramètres du score depuis le formulaire POST
        # et les sauvegarder dans la base de données pour le client
        # Exemple : 
        client.score_parameters.set([1, 2, 3])  # Remplacez param1, param2, param3 par les objets ScoreParameters correspondants
        return redirect('client:view_score')

    return render(request, 'client/calculate_score.html')

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            CIN = form.cleaned_data['CIN']
            user = authenticate(request, username=phone_number, password=CIN)
            if user is not None:
                login(request, user)

    return render(request, 'client/login.html', {'form': form})


def register(request):
    form = UserRegistrationForm()

    if request.method =='POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('client:view_score')
    
    return render(request,'client/login.html',{'form':form})


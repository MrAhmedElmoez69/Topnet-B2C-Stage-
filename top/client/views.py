from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.db import models
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib import messages

@login_required
def enter_score_parameters(request):
    client = request.user
    score_parameters = ScoreParameters.objects.all()

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('view_score')
    else:
        form = ClientForm(instance=client)
    return render(request, 'client/calculate_score.html', {"form": form})


from django.contrib import messages

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('view_score')
        else:
            messages.error(request, 'Incorrect username or password. Please try again.')

    return render(request, 'client/login.html', {'form': form})

def register(request):
    form = UserRegistrationForm()

    if request.method =='POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('enter_score_parameters')
    
    return render(request,'client/login.html',{'form':form})

@login_required
def view_score(request):
    client = request.user
    score_parameters = client.score_parameters.all()
    total_weight = sum(param.poids for param in score_parameters)
    total_score = sum((param.objectif / total_weight) * param.poids for param in score_parameters)
    niveau_classe = calculate_niveau_classe(total_score)
    return render(request, 'client/view_score.html', {'score_parameters': score_parameters, 'total_score': total_score, 'niveau_classe': niveau_classe})


def calculate_niveau_classe(total_score):
    niveau_classe_mapping = {
        (0, 20): 'classe 4. Signaux clairs de failles. Risque avéré.',
        (21, 40): 'niveau 3. Quelques alertes ont été remontées. Risque probable.',
        (41, 70): 'niveau 2. Bonne santé dans l’ensemble. Risque limité.',
        (71, 100): 'niveau 1. Excellente santé financière. Risque très peu probable.',
    }
    for (lower, upper), niveau_classe in niveau_classe_mapping.items():
        if lower <= total_score <= upper:
            return niveau_classe
    return None


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.db import models


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


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.db import models
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator

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

        if user is not None and user.is_superuser:  # Check if the user is a superuser
            login(request, user)
            return redirect('view_tables')
        else:
            messages.error(request, 'Access restricted. Only Topnet Agent can log in.')

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




def view_tables(request):
    # Retrieve clients with their related "ValeurCommerciale" instances
    clients_with_valeur_commerciale = Client.objects.filter(valeur_commerciale__isnull=False)
    
    # Search by Client Username
    search_query = request.GET.get('search')
    if search_query:
        clients_with_valeur_commerciale = clients_with_valeur_commerciale.filter(username__icontains=search_query)

    # Filter by Date Joined
    filter_option = request.GET.get('filter', 'all')
    if filter_option == 'today':
        clients_with_valeur_commerciale = clients_with_valeur_commerciale.filter(date_joined__date=timezone.now().date())
    elif filter_option == 'past7days':
        past_week = timezone.now() - timezone.timedelta(days=7)
        clients_with_valeur_commerciale = clients_with_valeur_commerciale.filter(date_joined__gte=past_week)
    elif filter_option == 'thismonth':
        clients_with_valeur_commerciale = clients_with_valeur_commerciale.filter(date_joined__year=timezone.now().year, date_joined__month=timezone.now().month)
    elif filter_option == 'thisyear':
        clients_with_valeur_commerciale = clients_with_valeur_commerciale.filter(date_joined__year=timezone.now().year)

    # Update the number of clients per page (change to 2)
    paginator = Paginator(clients_with_valeur_commerciale, 2)

    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)

    print("Filter Option:", filter_option)
    print("Clients:", clients)
    
    return render(request, 'client/view_tables.html', {'clients': clients, 'search_query': search_query, 'filter_option': filter_option})

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


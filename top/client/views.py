from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Client
from django.db import models
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
import pandas as pd
from .models import Axes  # Import the Axes model
import openpyxl
from django.http import HttpResponse




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
            return redirect('view_axes')
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




@login_required
def view_tables(request):
    # Retrieve clients with their related "ValeurCommerciale" instances
    clients_with_valeur_commerciale = Client.objects.filter(valeur_commerciale__isnull=False)
    
    # Filter out superusers
    clients_with_valeur_commerciale = clients_with_valeur_commerciale.exclude(is_superuser=True)
    
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



@login_required
def view_axes(request):
    # Retrieve Axes objects with their related Client instances
    axes_with_clients = Axes.objects.select_related('client').filter(client__valeur_commerciale__isnull=False)
    
    # Filter out superusers
    axes_with_clients = axes_with_clients.exclude(client__is_superuser=True)
    
    # Search by Client Username
    search_query = request.GET.get('search')
    if search_query:
        axes_with_clients = axes_with_clients.filter(client__username__icontains=search_query)

    # Filter by Date Joined
    filter_option = request.GET.get('filter', 'all')
    if filter_option == 'today':
        axes_with_clients = axes_with_clients.filter(client__date_joined__date=timezone.now().date())
    elif filter_option == 'past7days':
        past_week = timezone.now() - timezone.timedelta(days=7)
        axes_with_clients = axes_with_clients.filter(client__date_joined__gte=past_week)
    elif filter_option == 'thismonth':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year, client__date_joined__month=timezone.now().month)
    elif filter_option == 'thisyear':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year)

    # Update the number of items per page (change to 2)
    paginator = Paginator(axes_with_clients, 2)

    page_number = request.GET.get('page')
    axes = paginator.get_page(page_number)

    # print("Filter Option:", filter_option)
    # print("Axes:", axes)

    
    return render(request, 'client/view_axes.html', {'axes': axes, 'search_query': search_query, 'filter_option': filter_option})

def client_scores(request, client_id):
    clients_with_scores = []

    search_query = request.GET.get('search')
    filter_option = request.GET.get('filter', 'all')

    axes_with_clients = Axes.objects.select_related('client').filter(client_id=client_id, client__valeur_commerciale__isnull=False).exclude(client__is_superuser=True)

    if search_query:
        axes_with_clients = axes_with_clients.filter(client__username__icontains=search_query)

    if filter_option == 'today':
        axes_with_clients = axes_with_clients.filter(client__date_joined__date=timezone.now().date())
    elif filter_option == 'past7days':
        past_week = timezone.now() - timezone.timedelta(days=7)
        axes_with_clients = axes_with_clients.filter(client__date_joined__gte=past_week)
    elif filter_option == 'thismonth':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year, client__date_joined__month=timezone.now().month)
    elif filter_option == 'thisyear':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year)

    paginator = Paginator(axes_with_clients, 2)  # Change the number of items per page as needed

    page_number = request.GET.get('page')
    axes = paginator.get_page(page_number)

    for axis in axes_with_clients:
        valeur_commerciale_score = axis.valeur_commerciale.calculate_total_score()
        engagement_topnet_score = axis.engagement_topnet.calculate_total_score()
        engagement_client_score = axis.engagement_client.calculate_total_score()
        comportement_client_score = axis.comportement_client.calculate_total_score()

        total_score = (
            valeur_commerciale_score
            + engagement_topnet_score
            + engagement_client_score
            + comportement_client_score
        )
        score_level = get_score_level(total_score)
        decision = get_decision(total_score)

        client_with_score = {
            'client': axis.client,
            'total_score': total_score,
            'score_level': score_level,
            'decision': decision,
        }

        clients_with_scores.append(client_with_score)

    return render(
        request,
        'client/client_scores.html',
        {'clients_with_scores': clients_with_scores,
         'search_query': search_query,
         'filter_option': filter_option,}
    )


def get_score_level(total_score):
    if total_score <= 20:
        return "Niveau 4: Signaux clairs de failles."
    elif total_score <= 40:
        return "Niveau 3: Quelques alertes ont été remontées."
    elif total_score <= 70:
        return "Niveau 2: Bonne santé dans l'ensemble."
    else:
        return "Niveau 1: Excellente santé financière."

def get_decision(total_score):
    if total_score <= 20:
        return "Risque avéré."
    elif total_score <= 40:
        return "Risque probable."
    elif total_score <= 70:
        return "Risque limité."
    else:
        return "Risque très peu probable."


# -------------------------------- Pdf All --------------------------------



def generate_excel(request):
    from .models import EngagementClient, ValeurCommerciale, ComportementClient, EngagementTopnet  # Import your models
    # Query your models to get the data for clients
    engagement_clients = EngagementClient.objects.all()
    valeur_commerciales = ValeurCommerciale.objects.all()
    comportement_clients = ComportementClient.objects.all()
    engagement_topnets = EngagementTopnet.objects.all()

    # Create a DataFrame with the client data
    data = []
    for engagement_client, valeur_commerciale, comportement_client, engagement_topnet in zip(
        engagement_clients, valeur_commerciales, comportement_clients, engagement_topnets
    ):
        total_score_comportement_client = comportement_client.calculate_total_score()
        total_score_engagement_client = engagement_client.calculate_total_score()  # Add this line

        data.append({
            'Client Name': engagement_client.client.username,
            'Anciennete': engagement_client.calculate_anciennete(),
            'Nombre Suspension': engagement_client.calculate_nombre_suspension(),
            'Montant en Cours': engagement_client.calculate_montant_en_cours(),
            'Categorie Client': valeur_commerciale.categorie_client,
            'Engagement Contractuel': valeur_commerciale.engagement_contractuel,
            'Offre': valeur_commerciale.offre,
            'Debit': valeur_commerciale.debit,
            'Delai Moyen Paiement': comportement_client.calculate_delai_moyen_paiement(),
            'Incident de Paiement': comportement_client.incident_de_paiement(),
            'Contentieux': comportement_client.contentieux(),
            'Delai Moyen Paiement Score': comportement_client.calculate_delai_moyen_paiement_score(),
            'Incident de Paiement Score': comportement_client.calculate_incident_de_paiement_score(),
            'Contentieux Score': comportement_client.calculate_contentieux_score(),
            'Nombre Reclamations': engagement_topnet.nombre_reclamations,
            'Delai Traitement': engagement_topnet.delai_traitement,
            'Total Score Comportement Client': total_score_comportement_client,
            'Total Score Engagement Client': total_score_engagement_client,  # Add this field
            'Total Score Engagement Topnet': engagement_topnet.calculate_total_score(),  # Add the total score here
            'Total Score Valeur Commerciale': valeur_commerciale.calculate_total_score(),  # Add the total score for valeur commerciale
            # Add more fields as needed
        })

    df = pd.DataFrame(data)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="client_data.xlsx"'

    # Write the DataFrame to the response as an Excel file
    df.to_excel(response, index=False)

    return response


# --------------------------------View All Scores --------------------------------

def process_client_scores(axes):
    clients_with_scores = []

    for axis in axes:
        valeur_commerciale_score = axis.valeur_commerciale.calculate_total_score()
        engagement_topnet_score = axis.engagement_topnet.calculate_total_score()
        engagement_client_score = axis.engagement_client.calculate_total_score()
        comportement_client_score = axis.comportement_client.calculate_total_score()

        total_score = (
            valeur_commerciale_score
            + engagement_topnet_score
            + engagement_client_score
            + comportement_client_score
        )
        score_level = get_score_level(total_score)
        decision = get_decision(total_score)

        client_with_score = {
            'client': axis.client,
            'total_score': total_score,
            'score_level': score_level,
            'decision': decision,
        }

        clients_with_scores.append(client_with_score)

    return clients_with_scores

def view_all_score(request):
    search_query = request.GET.get('search')
    filter_option = request.GET.get('filter', 'all')

    axes_with_clients = Axes.objects.select_related('client').filter(client__valeur_commerciale__isnull=False).exclude(client__is_superuser=True)

    if search_query:
        axes_with_clients = axes_with_clients.filter(client__username__icontains=search_query)

    if filter_option == 'today':
        axes_with_clients = axes_with_clients.filter(client__date_joined__date=timezone.now().date())
    elif filter_option == 'past7days':
        past_week = timezone.now() - timezone.timedelta(days=7)
        axes_with_clients = axes_with_clients.filter(client__date_joined__gte=past_week)
    elif filter_option == 'thismonth':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year, client__date_joined__month=timezone.now().month)
    elif filter_option == 'thisyear':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year)

    paginator = Paginator(axes_with_clients, 100)  # Change the number of items per page as needed

    page_number = request.GET.get('page')
    axes = paginator.get_page(page_number)

    clients_with_scores = process_client_scores(axes)

    return render(
        request,
        'client/view_all_score.html',
        {'clients_with_scores': clients_with_scores,
         'search_query': search_query,
         'filter_option': filter_option,}
    )

def download_excel(request):
    search_query = request.GET.get('search')
    filter_option = request.GET.get('filter', 'all')

    axes_with_clients = Axes.objects.select_related('client').filter(client__valeur_commerciale__isnull=False).exclude(client__is_superuser=True)

    if search_query:
        axes_with_clients = axes_with_clients.filter(client__username__icontains=search_query)

    if filter_option == 'today':
        axes_with_clients = axes_with_clients.filter(client__date_joined__date=timezone.now().date())
    elif filter_option == 'past7days':
        past_week = timezone.now() - timezone.timedelta(days=7)
        axes_with_clients = axes_with_clients.filter(client__date_joined__gte=past_week)
    elif filter_option == 'thismonth':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year, client__date_joined__month=timezone.now().month)
    elif filter_option == 'thisyear':
        axes_with_clients = axes_with_clients.filter(client__date_joined__year=timezone.now().year)

    clients_with_scores = process_client_scores(axes_with_clients)

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Client Scores"

    headers = ['Client', 'Total Score', 'Score Level', 'Decision']
    worksheet.append(headers)

    for client_score in clients_with_scores:
        row = [
            client_score['client'].username,
            client_score['total_score'],
            client_score['score_level'],
            client_score['decision']
        ]
        worksheet.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=client_scores.xlsx'

    workbook.save(response)

    return response


def get_score_level(total_score):
    if total_score <= 20:
        return "Niveau 4: Signaux clairs de failles."
    elif total_score <= 40:
        return "Niveau 3: Quelques alertes ont été remontées."
    elif total_score <= 70:
        return "Niveau 2: Bonne santé dans l'ensemble."
    else:
        return "Niveau 1: Excellente santé financière."

def get_decision(total_score):
    if total_score <= 20:
        return "Risque avéré."
    elif total_score <= 40:
        return "Risque probable."
    elif total_score <= 70:
        return "Risque limité."
    else:
        return "Risque très peu probable."









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

def import_data_from_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file)

        # Import Valeur Commerciale
        for index, row in df['ValeurCommerciale'].iterrows():
            valeur_commerciale = ValeurCommerciale.objects.create(
                categorie_client=row['categorie_client'],
                engagement_contractuel=row['engagement_contractuel'],
                offre=row['offre'],
                debit=row['debit']
            )

        # Import Engagement Client
        for index, row in df['EngagementClient'].iterrows():
            engagement_client = EngagementClient.objects.create(
                client=Client.objects.get(id=row['client_id']),
                anciennete=row['anciennete'],
                nombre_suspension=row['nombre_suspension'],
                montant_en_cours=row['montant_en_cours']
            )

        # Import Engagement TOPNET
        for index, row in df['EngagementTopnet'].iterrows():
            engagement_topnet = EngagementTopnet.objects.create(
                client=Client.objects.get(id=row['client_id']),
                nombre_reclamations=row['nombre_reclamations'],
                delai_traitement=row['delai_traitement']
            )

        # Import Comportement Client
        for index, row in df['ComportementClient'].iterrows():
            comportement_client = ComportementClient.objects.create(
                facture=Facture.objects.get(id=row['facture_id']),
                client=Client.objects.get(id=row['client_id'])
            )

        # Import AxesWeight
        axes_weight = AxesWeight.objects.create(
            valeur_commerciale_weight=df['AxesWeight']['valeur_commerciale_weight'][0],
            engagement_topnet_weight=df['AxesWeight']['engagement_topnet_weight'][0],
            engagement_client_weight=df['AxesWeight']['engagement_client_weight'][0],
            comportement_client_weight=df['AxesWeight']['comportement_client_weight'][0]
        )

        # Import CriteriaWeight
        criteria_weight = CriteriaWeight.objects.create(
            poids_offre=df['CriteriaWeight']['poids_offre'][0],
            poids_debit=df['CriteriaWeight']['poids_debit'][0],
            poids_categorie_client=df['CriteriaWeight']['poids_categorie_client'][0],
            poids_engagement_contractuel=df['CriteriaWeight']['poids_engagement_contractuel'][0],
            poids_anciennete=df['CriteriaWeight']['poids_anciennete'][0],
            poids_nombre_suspension=df['CriteriaWeight']['poids_nombre_suspension'][0],
            poids_montant_en_cours=df['CriteriaWeight']['poids_montant_en_cours'][0],
            poids_delai_moyen_paiement=df['CriteriaWeight']['poids_delai_moyen_paiement'][0],
            poids_incident_de_paiement=df['CriteriaWeight']['poids_incident_de_paiement'][0],
            poids_contentieux=df['CriteriaWeight']['poids_contentieux'][0],
            poids_nombre_reclamations=df['CriteriaWeight']['poids_nombre_reclamations'][0],
            poids_delai_traitement=df['CriteriaWeight']['poids_delai_traitement'][0],
        )

        # Import Axes
        for index, row in df['Axes'].iterrows():
            axes = Axes.objects.create(
                client=Client.objects.get(id=row['client_id']),
                valeur_commerciale=ValeurCommerciale.objects.get(id=row['valeur_commerciale_id']),
                engagement_topnet=EngagementTopnet.objects.get(id=row['engagement_topnet_id']),
                engagement_client=EngagementClient.objects.get(id=row['engagement_client_id']),
                comportement_client=ComportementClient.objects.get(id=row['comportement_client_id'])
            )

    return render(request, 'client/import_success.html')


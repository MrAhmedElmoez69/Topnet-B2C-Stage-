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



def view_axes(request):
    # Retrieve Axes objects with their related Client instances
    axes_with_clients = Axes.objects.select_related('client')

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

    axes_with_clients = Axes.objects.select_related('client').filter(client_id=client_id).exclude(client__is_superuser=True)

    

   
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
    from openpyxl import Workbook
    from django.http import HttpResponse
    from django.utils import timezone
    from .models import EngagementClient, ValeurCommerciale, ComportementClient, EngagementTopnet

    axes_with_clients = Axes.objects.select_related('client').exclude(client__is_superuser=True)
    Clients_with_Scores = process_client_scores(axes_with_clients)


    last_axes_weight = AxesWeight.objects.last()  

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Client Scores"

    headers = ['Client Name', 'Anciennete', 'Nombre Suspension', 'Montant en Cours', 'Categorie Client', 'Engagement Contractuel', 'Offre', 'Debit', 'Delai Moyen Paiement', 'Incident de Paiement', 'Contentieux', 'Delai Moyen Paiement Score', 'Incident de Paiement Score', 'Contentieux Score', 'Nombre Reclamations', 'Delai Traitement', 'Valeur Commerciale Score', 'Engagement Topnet Score', 'Engagement Client Score', 'Comportement Client Score', 'Score Total', 'Score Level', 'Decision' , 'AxeWeight ID']
    worksheet.append(headers)

    for client_score in Clients_with_Scores:
        client = client_score['client']

        engagement_clients = EngagementClient.objects.filter(client=client)
        valeur_commerciales = ValeurCommerciale.objects.filter(client=client)
        comportement_clients = ComportementClient.objects.filter(client=client)
        engagement_topnets = EngagementTopnet.objects.filter(client=client)

        if engagement_clients.exists() and valeur_commerciales.exists() and comportement_clients.exists() and engagement_topnets.exists():
            engagement_client = engagement_clients.first()
            valeur_commerciale = valeur_commerciales.first()
            comportement_client = comportement_clients.first()
            engagement_topnet = engagement_topnets.first()

            row = [
                client_score['client'].username,
                engagement_client.calculate_anciennete(),
                engagement_client.calculate_nombre_suspension(),
                engagement_client.calculate_montant_en_cours(),
                valeur_commerciale.categorie_client,
                valeur_commerciale.engagement_contractuel,
                valeur_commerciale.offre,
                valeur_commerciale.debit,
                comportement_client.calculate_delai_moyen_paiement(),
                comportement_client.incident_de_paiement(),
                comportement_client.contentieux(),
                comportement_client.calculate_delai_moyen_paiement_score(),
                comportement_client.calculate_incident_de_paiement_score(),
                comportement_client.calculate_contentieux_score(),
                engagement_topnet.nombre_reclamations,
                engagement_topnet.delai_traitement,
                client_score['valeur_commerciale_score'],
                client_score['engagement_topnet_score'],
                client_score['engagement_client_score'],
                client_score['comportement_client_score'],
                client_score['total_score'],
                client_score['score_level'],
                client_score['decision'] , 
                last_axes_weight.id if last_axes_weight else None

            ]
            worksheet.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Rapport_Clients.xlsx'

    workbook.save(response)

    return response

def process_client_Scoress(axes):
    Clients_with_Scores = {}

    for axis in axes:
        valeur_commerciale_score = axis.valeur_commerciale.calculate_total_score()
        engagement_topnet_score = axis.engagement_topnet.calculate_total_score()
        engagement_client_score = axis.engagement_client.calculate_total_score()
        comportement_client_score = axis.comportement_client.calculate_total_score()

        total_weight = (
            axis.valeur_commerciale_weight +
            axis.engagement_topnet_weight +
            axis.engagement_client_weight +
            axis.comportement_client_weight
        )

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
            'valeur_commerciale_score': valeur_commerciale_score,
            'axes_weight': axis.axes_weight,  # Include the entire AxesWeight object
            'engagement_topnet_score': engagement_topnet_score,
            'engagement_client_score': engagement_client_score,
            'comportement_client_score': comportement_client_score,
            'total_score': total_score,
            'score_level': score_level,
            'decision': decision,
        }

        Clients_with_Scores[axis.id] = client_with_score  # Store by axis ID

    return Clients_with_Scores
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
            'valeur_commerciale_score': valeur_commerciale_score,
            'engagement_topnet_score': engagement_topnet_score,
            'engagement_client_score': engagement_client_score,
            'comportement_client_score': comportement_client_score,
            'total_score': total_score,
            'score_level': score_level,
            'decision': decision,
        }

        clients_with_scores.append(client_with_score)

    return clients_with_scores

def view_all_score(request):
    search_query = request.GET.get('search')
    filter_option = request.GET.get('filter', 'all')

    axes_with_clients = Axes.objects.select_related('client').exclude(client__is_superuser=True)

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

    sort_param = request.GET.get('sort')
    if sort_param == 'total_score':
        clients_with_scores = sorted(clients_with_scores, key=lambda x: x['total_score'], reverse=True)
    elif sort_param == 'client':
        clients_with_scores = sorted(clients_with_scores, key=lambda x: x['client'].username)  # Use the appropriate attribute of the Client model for sorting
    
    score_ranges = {
        '0-20': (0, 20),
        '21-40': (21, 40),
        '41-71': (41, 71),
        '72-100': (72, 100),
    }

    filter_range = request.GET.get('filter_range')
    if filter_range in score_ranges:
        min_score, max_score = score_ranges[filter_range]
        clients_with_scores = [client for client in clients_with_scores if min_score <= client['total_score'] <= max_score]

    return render(
        request,
        'client/view_all_score.html',
        {'clients_with_scores': clients_with_scores,
         'search_query': search_query,
         'filter_option': filter_option,
         'sort_param': sort_param,
         'filter_range': filter_range,
         'score_ranges': score_ranges}
    )


def statistics(request):
    axes = Axes.objects.all()  # Retrieve all axes data

    clients_with_scores = process_client_scores(axes)

    # Sort clients_with_scores by total_score in descending order
    clients_with_scores = sorted(clients_with_scores, key=lambda x: x['total_score'], reverse=True)

    context = {
        'clients_with_scores': clients_with_scores,
    }

    return render(request, 'client/statistics.html', context)


def download_excel(request):
    axes_with_clients = Axes.objects.select_related('client').exclude(client__is_superuser=True)
    clients_with_scores = process_client_scores(axes_with_clients)
    
    last_axes_weight = AxesWeight.objects.last()  

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Client Scores"

    headers = ['Client', 'Total Score', 'Score Level', 'Decision', 'AxeWeight ID']
    worksheet.append(headers)

    for client_score in clients_with_scores:
        client = client_score['client']
        
        row = [
            client.username,
            client_score['total_score'],
            client_score['score_level'],
            client_score['decision'],
            last_axes_weight.id if last_axes_weight else None
        ]
        worksheet.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=client_scores.xlsx'

    workbook.save(response)

    return response




from django.shortcuts import get_object_or_404, redirect
def axes_weight_list(request):  
    axes_weights = AxesWeight.objects.all()

    if request.method == 'POST':
        weight_id_to_delete = request.POST.get('delete_weight_id')
        if weight_id_to_delete:
            weight_to_delete = get_object_or_404(AxesWeight, id=weight_id_to_delete)
            weight_to_delete.delete()
            return redirect('axes_weight_list')  # Redirect back to the list after deletion

    context = {
        'axes_weights': axes_weights,
    }

    return render(request, 'client/axes_weight_list.html', context)

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


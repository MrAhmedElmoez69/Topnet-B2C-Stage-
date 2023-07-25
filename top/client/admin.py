from django.contrib import admin
from .models import *
from .forms import *

class IsClient(admin.ModelAdmin):
    list_display = (
        'username',
        'CIN',
        'phone_number',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
        'total_score',  # Display the total score in the admin list view
        'niveau_classe',  # Display the niveau/classe in the admin list view
    )
    search_fields = [
        'phone_number',
    ]
    fieldsets = (
        (
            'Personal Info',
            {
                'fields': (
                    'phone_number',
                    'CIN',
                    'username',
                    'first_name',
                    'last_name',
                    'password',
                    'is_staff'
                ),
            }
        ),
    )
    list_filter = (
        'is_staff',
        'date_joined'
    )

    def total_score(self, obj):
        scores = obj.calculate_score()  # Calculate the scores using the calculate_score method of the Client model
        return scores['total_score']

    def niveau_classe(self, obj):
        total_score = self.total_score(obj)
        return obj.calculate_niveau_classe(total_score)

    total_score.short_description = 'Total Score'
    niveau_classe.short_description = 'Niveau/Classe'

class ClientAdmin(admin.ModelAdmin):
    list_display = ['username', 'CIN', 'phone_number', 'first_name', 'last_name', 'is_staff', 'date_joined']
    search_fields = ['username', 'CIN', 'phone_number']
    list_filter = ['is_staff', 'date_joined']
    actions = ['calculate_and_save_score']
    form = ClientCreationForm

    def calculate_and_save_score(self, request, queryset):
        for client in queryset:
            scores = client.calculate_score()
            client.total_score = scores['total_score']
            client.niveau_classe = scores['niveau_classe']
            client.save()

    calculate_and_save_score.short_description = 'Calculate and Save Score'

    def get_form(self, request, obj=None, **kwargs):
        # Get the default form and pass the 'criteres' value if available
        form = super().get_form(request, obj, **kwargs)
        criteres = request.POST.get('criteres') if request.POST else (obj.criteres if obj else None)

        if criteres:
            # Show relevant fields based on the selected value of 'criteres'
            form = form(request.POST, instance=obj) if obj else form(request.POST)
            form.show_fields_for_criteres(criteres)

        return form
    

#Data To a unique user 
class ScoreParametersInline(admin.TabularInline):
    model = ScoreParameters

class ScoreParametersAdmin(admin.ModelAdmin):
    list_display = ['criteres', 'client']  # Add 'client' to the list display for ScoreParameters
    list_filter = ['client']  # Add 'client' to the list filter for ScoreParameters

    def get_queryset(self, request):
        # Filter the ScoreParameters instances based on the currently logged-in client
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user)

class EngagementTopnetInline(admin.StackedInline):
    model = EngagementTopnet
    can_delete = False
    readonly_fields = ['nombre_reclamation', 'delai_traitement']

class EngagementClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours']
    readonly_fields = ['get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours']

    def get_anciennete(self, obj):
        today = datetime.date.today()
        if obj.client.contrats.exists():  # Access contrat_set using the reverse relationship
            last_contrat = obj.client.contrats.latest('date_debut')
            difference = today - last_contrat.date_debut
            if difference.days >= 730:
                return 3
            elif 365 <= difference.days < 730:
                return 2
            elif difference.days < 365:
                return 1
        return None
    get_anciennete.short_description = 'Anciennete'

    def get_nombre_suspension(self, obj):
        if obj.client.contrats.exists():  # Access contrat_set using the reverse relationship
            nombre_suspension = obj.client.contrats.aggregate(models.Max('nombre_suspension'))['nombre_suspension__max']
            if nombre_suspension < 2:
                return 1
            else:
                return 0
        return None
    get_nombre_suspension.short_description = 'Nombre Suspension'

    def get_montant_en_cours(self, obj):
        if obj.client.contrats.exists():  # Access contrat_set using the reverse relationship
            montant_en_cours = obj.client.contrats.aggregate(models.Max('montant_en_cours'))['montant_en_cours__max']
            if montant_en_cours < 2:
                return 1
            elif montant_en_cours == 0:
                return 0
            else:
                return 0.5
        return None
    get_montant_en_cours.short_description = 'Montant en Cours'
class EngagementTopnetAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_nombre_reclamations', 'get_delai_traitement']
    readonly_fields = ['get_nombre_reclamations', 'get_delai_traitement']

    def get_nombre_reclamations(self, obj):
        if obj.client.contrats.exists():
            reclamations = Reclamation.objects.filter(contrat__in=obj.client.contrats.all(), date_debut__year=datetime.date.today().year)
            nombre_reclamations_par_an = reclamations.count()

            if nombre_reclamations_par_an > 4:
                return 1
            elif 2 < nombre_reclamations_par_an < 4:
                return 0.5
            else:
                return 0
        return None
    get_nombre_reclamations.short_description = 'Nombre de Réclamations'

    def get_delai_traitement(self, obj):
        if obj.client.contrats.exists():
            reclamations = Reclamation.objects.filter(contrat__in=obj.client.contrats.all(), date_debut__year=datetime.date.today().year)
            delai_traitement_total = datetime.timedelta()

            for reclamation in reclamations:
                # Ensure date_fin is not before date_debut
                if reclamation.date_fin >= reclamation.date_debut:
                    delai_traitement_total += reclamation.date_fin - reclamation.date_debut

            delai_moyen_traitement = delai_traitement_total / reclamations.count()
            delai_theorique_traitement = datetime.timedelta(days=365)  # Replace this with the desired value for the theoretical processing time in days per year

            if delai_moyen_traitement > delai_theorique_traitement:
                return 1
            else:
                return 0
        return None
    get_delai_traitement.short_description = 'Délai de Traitement'



admin.site.register(EngagementTopnet, EngagementTopnetAdmin)
admin.site.register(EngagementClient, EngagementClientAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ScoreParameters)
admin.site.register(ValeurCommerciale)


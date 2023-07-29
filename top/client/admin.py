from django.contrib import admin
from .models import *
from .forms import *
from django.urls import reverse
from django.utils.html import format_html


class IsClient(admin.ModelAdmin):
    list_display = (
        'username',
        'CIN',
        'phone_number',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
        'total_score',  
        'niveau_classe',  
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
        scores = obj.calculate_score()  
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

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     criteres = request.POST.get('criteres') if request.POST else (obj.criteres if obj else None)

    #     if criteres:
    #         form = form(request.POST, instance=obj) if obj else form(request.POST)
    #         form.show_fields_for_criteres(criteres)

    #     return form
    

class ScoreParametersInline(admin.TabularInline):
    model = ScoreParameters

class ScoreParametersAdmin(admin.ModelAdmin):
    list_display = ['criteres', 'client']  
    list_filter = ['client']  

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user)

class EngagementTopnetInline(admin.StackedInline):
    model = EngagementTopnet
    can_delete = False
    readonly_fields = ['nombre_reclamation', 'delai_traitement']

class EngagementClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours', 'contrat_link', 'get_date_debut_contrat', 'get_date_fin_contrat']
    list_display_links = ['client', 'contrat_link']
    readonly_fields = ['get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours']

    def get_anciennete(self, obj):
        today = datetime.date.today()
        if obj.client.contrats.exists():  
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
        if obj.client.contrats.exists():  
            nombre_suspension = obj.client.contrats.aggregate(models.Max('nombre_suspension'))['nombre_suspension__max']
            if nombre_suspension < 2:
                return 1
            else:
                return 0
        return None
    get_nombre_suspension.short_description = 'Nombre Suspension'

    def get_montant_en_cours(self, obj):
        if obj.client.contrats.exists():  
            montant_en_cours = obj.client.contrats.aggregate(models.Sum('montant_en_cours'))['montant_en_cours__sum']
            return montant_en_cours
        return None
    get_montant_en_cours.short_description = 'Montant en cours'

    def get_contrat(self, obj):
        if obj.client.contrats.exists():  
            return obj.client.contrats.latest('date_debut')
        return None
    get_contrat.short_description = 'Contrat'

    
    
    def contrat_link(self, obj):
        contract = self.get_contrat(obj)
        if contract:
            pk_field_name = contract._meta.pk.name  # Get the name of the primary key field
            url = reverse('admin:%s_%s_change' % (contract._meta.app_label, contract._meta.model_name),  args=[getattr(contract, pk_field_name)])
            return format_html('<a href="{}">{}</a>', url, getattr(contract, pk_field_name))
        return None
    contrat_link.short_description = 'Contrat'
    contrat_link.admin_order_field = 'client__contrats__contract_id'  # If you want to make the column sortable

    def get_date_debut_contrat(self, obj):
        if obj.client.contrats.exists():  
            date_debut_contrat = obj.client.contrats.earliest('date_debut').date_debut
            return date_debut_contrat
        return None
    get_date_debut_contrat.short_description = 'Date Debut Contrat'

    def get_date_fin_contrat(self, obj):
        if obj.client.contrats.exists():  
            date_fin_contrat = obj.client.contrats.latest('date_fin').date_fin
            return date_fin_contrat
        return None
    get_date_fin_contrat.short_description = 'Date Fin Contrat'

class EngagementTopnetAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_nombre_reclamations','get_contrat_id', 'get_date_debut', 'get_date_fin', 'get_delai_traitement']
    list_display_links = ['client','get_contrat_id']
    readonly_fields = ['client','get_nombre_reclamations', 'get_delai_traitement']

    def get_contrat_id(self, obj):
        if obj.client.contrats.exists():
            return obj.client.contrats.latest('date_debut').id_contrat
        return 'No Contract'
    get_contrat_id.short_description = 'Contrat '

    def get_date_debut(self, obj):
        if obj.client.contrats.exists():
            return obj.client.contrats.latest('date_debut').date_debut
        return None
    get_date_debut.short_description = 'Date Debut Contrat'

    def get_date_fin(self, obj):
        if obj.client.contrats.exists():
            return obj.client.contrats.latest('date_debut').date_fin
        return None
    get_date_fin.short_description = 'Date Fin Contrat'
    def get_nombre_reclamations(self, obj):
        return obj.calculate_nombre_reclamations()
    get_nombre_reclamations.short_description = 'Taux Du nombre reclamation par an'

    def get_delai_traitement(self, obj):
        obj.calculate_delai_traitement()
        return obj.delai_traitement
    get_delai_traitement.short_description = 'delai traitement'



class ComportementClientAdmin(admin.ModelAdmin):
    list_display = ['client_name_link', 'contrat_link', 'get_date_debut', 'get_date_fin', 'get_delai_moyen_paiement', 'get_incident_de_paiement', 'get_contentieux']
    list_display_links = ['client_name_link', 'contrat_link']

    def client_name_link(self, obj):
        if obj.facture and obj.facture.client:
            client = obj.facture.client
            url = reverse('admin:%s_%s_change' % (client._meta.app_label, client._meta.model_name),  args=[client.pk])
            return format_html('<a href="{}">{}</a>', url, client.username)
        return 'No Client'
    client_name_link.short_description = 'Client Name'

    def contrat_link(self, obj):
        if obj.facture and obj.facture.contrat:
            contrat = obj.facture.contrat
            url = reverse('admin:%s_%s_change' % (contrat._meta.app_label, contrat._meta.model_name),  args=[contrat.pk])
            return format_html('<a href="{}">{}</a>', url, contrat.id_contrat)
        return 'No Contract'
    contrat_link.short_description = 'Contrat'

    def get_date_debut(self, obj):
        if obj.facture and obj.facture.contrat:
            return obj.facture.contrat.date_debut
        return None
    get_date_debut.short_description = 'Date Debut Contrat'

    def get_date_fin(self, obj):
        if obj.facture and obj.facture.contrat:
            return obj.facture.contrat.date_fin
        return None
    get_date_fin.short_description = 'Date Fin Contrat'

    def get_delai_moyen_paiement(self, obj):
        return obj.calculate_delai_moyen_paiement()
    get_delai_moyen_paiement.short_description = 'Delai moyen de paiement'

    def get_incident_de_paiement(self, obj):
        return obj.incident_de_paiement()
    get_incident_de_paiement.short_description = 'Incident de paiement'

    def get_contentieux(self, obj):
        return obj.contentieux()
    get_contentieux.short_description = 'Contentieux'


admin.site.register(EngagementTopnet, EngagementTopnetAdmin)
admin.site.register(EngagementClient, EngagementClientAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ScoreParameters)
admin.site.register(ValeurCommerciale)
admin.site.register(ComportementClient, ComportementClientAdmin)

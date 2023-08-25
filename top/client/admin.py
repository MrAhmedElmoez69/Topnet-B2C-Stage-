from django.contrib import admin, messages
from .models import *
from .forms import *
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django import forms



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


class ScoreParametersAdmin(admin.ModelAdmin):
    list_display = ('id', 'valeur_commerciale_weight', 'engagement_client_weight', 'engagement_topnet_weight', 'comportement_client_weight')
    list_filter = ()
    search_fields = ()
    ordering = ('id',)

class ValeurCommercialeAdmin(admin.ModelAdmin):
    list_display = ['client','categorie_client', 'calculate_score_categorie_client', 'engagement_contractuel', 'calculate_score_engagement_contractuel', 'offre','calculate_score_offre', 'debit','calculate_score_debit','calculate_total_score']

    def get_weight_from_axes(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            return axes.weight_valeur_commerciale
        return None

    get_weight_from_axes.short_description = 'Weight from Axes'

    def calculate_objectif_offre(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_valeur_commerciale = axes.weight_valeur_commerciale
            objectif_offre = (obj.poids_offre / 100) * (poids_valeur_commerciale / 100)
            return f'{objectif_offre:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_offre.short_description = 'Objectif Offre (%)'

    def calculate_objectif_debit(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_valeur_commerciale = axes.weight_valeur_commerciale
            objectif_debit = (obj.poids_debit / 100) * (poids_valeur_commerciale / 100)
            return f'{objectif_debit:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_debit.short_description = 'Objectif Debit (%)'

    def calculate_objectif_categorie(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_valeur_commerciale = axes.weight_valeur_commerciale
            objectif_categorie = (obj.poids_categorie_client / 100) * (poids_valeur_commerciale / 100)
            return f'{objectif_categorie:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_categorie.short_description = 'Objectif Categorie Client (%)'

    def calculate_objectif_engagement(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_valeur_commerciale = axes.weight_valeur_commerciale
            objectif_engagement = (obj.poids_engagement_contractuel / 100) * (poids_valeur_commerciale / 100)
            return f'{objectif_engagement:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_engagement.short_description = 'Objectif Engagement Contractuel (%)'

    def calculate_score_valeur_commerciale(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_valeur_commerciale = axes.weight_valeur_commerciale

            objectif_offre = (obj.poids_offre / 100) * (poids_valeur_commerciale / 100)
            objectif_debit = (obj.poids_debit / 100) * (poids_valeur_commerciale / 100)
            objectif_categorie = (obj.poids_categorie_client / 100) * (poids_valeur_commerciale / 100)
            objectif_engagement = (obj.poids_engagement_contractuel / 100) * (poids_valeur_commerciale / 100)

            score_valeur_commerciale = (objectif_offre + objectif_debit + objectif_categorie + objectif_engagement) * poids_valeur_commerciale
            return f'{score_valeur_commerciale:.2f}'  # Display with two decimal places
        return None

    calculate_score_valeur_commerciale.short_description = 'Objectif Score Valeur Commerciale (%)'

class EngagementClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours', 'contrat_link', 'get_date_debut_contrat', 'get_date_fin_contrat','calculate_total_score']
    list_display_links = ['client', 'contrat_link']
    readonly_fields = ['get_anciennete', 'get_nombre_suspension', 'get_montant_en_cours']

    def get_anciennete(self, obj):
        today = datetime.date.today()
        if obj.client.contrats.exists():  
            last_contrat = obj.client.contrats.latest('date_debut')
            difference = today - last_contrat.date_debut
            if difference.days >= 730:  # 2 years or more
                return "2 ans et plus"
        elif 365 <= difference.days < 730:  # between 1 year and 2 years (exclusive)
            return "1 an < a < 2 ans"
        return "< 1 an"  # less than 1 year or no contract
    get_anciennete.short_description = 'Anciennete'

    def get_nombre_suspension(self, obj):
        return obj.calculate_nombre_suspension()

    get_nombre_suspension.short_description = 'Nombre Suspension'

    def get_montant_en_cours(self, obj):
        if obj.client.contrats.exists():  
            nombre_facture_impayee = obj.client.contrats.aggregate(models.Sum('nombre_facture_impayee'))['nombre_facture_impayee__sum']
            if nombre_facture_impayee is not None:
                if nombre_facture_impayee > 2:
                    return Decimal('1')
                elif nombre_facture_impayee == 0:
                    return Decimal('0')
                else:
                    return Decimal('0.5')
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
    def get_weight_from_axes(self, obj):
        axes_queryset = Axes.objects.filter(engagement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            return axes.weight_engagement_client
        return None

    get_weight_from_axes.short_description = 'Weight from Axes'

    def calculate_objectif1(self, obj):
        axes_queryset = Axes.objects.filter(engagement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_client = axes.weight_engagement_client
            objectif1 = (obj.poids_anciennete / 100) * (poids_engagement_client / 100)
            return f'{objectif1:.2f}'
        return None

    calculate_objectif1.short_description = 'Objectif Ancienneté (%)'

    def calculate_objectif2(self, obj):
        axes_queryset = Axes.objects.filter(engagement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_client = axes.weight_engagement_client
            objectif2 = (obj.poids_nombre_suspension / 100) * (poids_engagement_client / 100)
            return f'{objectif2:.2f}'
        return None

    calculate_objectif2.short_description = 'Objectif Nombre Suspension (%)'

    def calculate_objectif3(self, obj):
        axes_queryset = Axes.objects.filter(engagement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_client = axes.weight_engagement_client
            objectif3 = (obj.poids_montant_en_cours / 100) * (poids_engagement_client / 100)
            return f'{objectif3:.2f}'
        return None

    calculate_objectif3.short_description = 'Objectif Montant En Cours (%)'
    
    def calculate_score_engagement_client(self, obj):
        axes_queryset = Axes.objects.filter(engagement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_client = axes.weight_engagement_client

            objectif_anciennete = (obj.poids_anciennete / 100) * (poids_engagement_client / 100)
            objectif_montant_en_cours = (obj.poids_montant_en_cours / 100) * (poids_engagement_client / 100)
            objectif_nombre_suspension = (obj.poids_nombre_suspension / 100) * (poids_engagement_client / 100)

            score_engagement_client = (objectif_anciennete + objectif_montant_en_cours + objectif_nombre_suspension) * poids_engagement_client
            return f'{score_engagement_client:.2f}'  # Display with two decimal places
        return None

    calculate_score_engagement_client.short_description = 'Objectif Score Engagement Client (%)'



class EngagementTopnetAdmin(admin.ModelAdmin):
    list_display = ['client', 'get_calculated_nombre_reclamations', 'get_delai_traitement','calculate_nombre_reclamations_score','calculate_delai_traitement_score','calculate_total_score']
    list_display_links = ['client']

    def get_calculated_nombre_reclamations(self, obj):
        return obj.nombre_reclamations
    get_calculated_nombre_reclamations.short_description = 'Calculated Nombre Reclamations'

    def get_delai_traitement(self, obj):
        return obj.delai_traitement
    get_delai_traitement.short_description = 'Délai de Traitement'
    def get_weight_from_axes(self, obj):
        axes_queryset = Axes.objects.filter(engagement_topnet=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            return axes.weight_engagement_topnet
        return None

    get_weight_from_axes.short_description = 'Weight from Axes'

    def calculate_objectif1(self, obj):
        axes_queryset = Axes.objects.filter(engagement_topnet=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_topnet = axes.weight_engagement_topnet
            objectif1 = (obj.poids_nombre_reclamations / 100) * (poids_engagement_topnet / 100)
            return f'{objectif1:.2f}'
        return None

    calculate_objectif1.short_description = 'Objectif Nombre de Reclamations (%)'

    def calculate_objectif2(self, obj):
        axes_queryset = Axes.objects.filter(engagement_topnet=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_topnet = axes.weight_engagement_topnet
            objectif2 = (obj.poids_delai_traitement / 100) * (poids_engagement_topnet / 100)
            return f'{objectif2:.2f}'
        return None

    calculate_objectif2.short_description = 'Objectif Delai de Traitement (%)'
    
    def calculate_score_engagement_topnet(self, obj):
        axes_queryset = Axes.objects.filter(engagement_topnet=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_engagement_topnet = axes.weight_engagement_topnet

            objectif_reclamations = (obj.poids_nombre_reclamations / 100) * (poids_engagement_topnet / 100)
            objectif_delai = (obj.poids_delai_traitement / 100) * (poids_engagement_topnet / 100)

            score_engagement_topnet = (objectif_reclamations + objectif_delai) * poids_engagement_topnet
            return f'{score_engagement_topnet:.2f}'  # Display with two decimal places
        return None

    calculate_score_engagement_topnet.short_description = 'Objectif Score Engagement Topnet (%)'

class ComportementClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'contrat_link',  'get_delai_moyen_paiement','calculate_delai_moyen_paiement_score', 'get_incident_de_paiement','calculate_incident_de_paiement_score', 'get_contentieux','calculate_contentieux_score','calculate_total_score']
    list_display_links = ['client', 'contrat_link']

   

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

    def get_weight_from_axes(self, obj):
        axes_queryset = Axes.objects.filter(comportement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            return axes.weight_comportement_client
        return None

    get_weight_from_axes.short_description = 'Weight from Axes'

    def calculate_objectif_delai_paiement(self, obj):
        axes_queryset = Axes.objects.filter(comportement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_comportement_client = axes.weight_comportement_client
            objectif_delai_paiement = (obj.poids_delai_moyen_paiement / 100) * (poids_comportement_client / 100)
            return f'{objectif_delai_paiement:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_delai_paiement.short_description = 'Objectif Delai Paiement (%)'

    def calculate_objectif_incident_paiement(self, obj):
        axes_queryset = Axes.objects.filter(comportement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_comportement_client = axes.weight_comportement_client
            objectif_incident_paiement = (obj.poids_incident_de_paiement / 100) * (poids_comportement_client / 100)
            return f'{objectif_incident_paiement:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_incident_paiement.short_description = 'Objectif Incident Paiement (%)'

    def calculate_objectif_contentieux(self, obj):
        axes_queryset = Axes.objects.filter(comportement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_comportement_client = axes.weight_comportement_client
            objectif_contentieux = (obj.poids_contentieux / 100) * (poids_comportement_client / 100)
            return f'{objectif_contentieux:.2f}'  # Display with two decimal places
        return None

    calculate_objectif_contentieux.short_description = 'Objectif Contentieux (%)'
    
    def calculate_score_comportement_client(self, obj):
        axes_queryset = Axes.objects.filter(comportement_client=obj)
        if axes_queryset.exists():
            axes = axes_queryset
            poids_comportement_client = axes.weight_comportement_client

            objectif_delai_paiement = (obj.poids_delai_moyen_paiement / 100) * (poids_comportement_client / 100)
            objectif_incident_paiement = (obj.poids_incident_de_paiement / 100) * (poids_comportement_client / 100)
            objectif_contentieux = (obj.poids_contentieux / 100) * (poids_comportement_client / 100)

            score_comportement_client = (objectif_delai_paiement + objectif_incident_paiement + objectif_contentieux) * poids_comportement_client
            return f'{score_comportement_client:.2f}'  # Display with two decimal places
        return None

    calculate_score_comportement_client.short_description = 'Objectif Score Comportement Client (%)'


class ValeurCommercialeFilter(admin.SimpleListFilter):
    title = 'Valeur Commerciale'
    parameter_name = 'valeur_commerciale'

    def lookups(self, request, model_admin):
        clients = Axes.objects.all().values_list('client__id', flat=True)
        return ValeurCommerciale.objects.filter(client__id__in=clients).values_list('id', 'id')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(valeur_commerciale__id=self.value())
        return queryset


class EngagementTopnetFilter(admin.SimpleListFilter):
    title = 'Engagement Topnet'
    parameter_name = 'engagement_topnet'

    def lookups(self, request, model_admin):
        clients = Axes.objects.all().values_list('client__id', flat=True)
        return EngagementTopnet.objects.filter(client__id__in=clients).values_list('id', 'id')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(engagement_topnet__id=self.value())
        return queryset


class EngagementClientFilter(admin.SimpleListFilter):
    title = 'Engagement Client'
    parameter_name = 'engagement_client'

    def lookups(self, request, model_admin):
        clients = Axes.objects.all().values_list('client__id', flat=True)
        return EngagementClient.objects.filter(client__id__in=clients).values_list('id', 'id')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(engagement_client__id=self.value())
        return queryset


class ComportementClientFilter(admin.SimpleListFilter):
    title = 'Comportement Client'
    parameter_name = 'comportement_client'

    def lookups(self, request, model_admin):
        clients = Axes.objects.all().values_list('client__id', flat=True)
        return ComportementClient.objects.filter(client__id__in=clients).values_list('id', 'id')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(comportement_client__id=self.value())
        return queryset
class ValeurCommercialeInline(admin.StackedInline):
    model = ValeurCommerciale

class EngagementTopnetInline(admin.StackedInline):
    model = EngagementTopnet

class EngagementClientInline(admin.StackedInline):
    model = EngagementClient

class ComportementClientInline(admin.StackedInline):
    model = ComportementClient


class ClientAdmin(admin.ModelAdmin):
    list_display = ['username', 'CIN', 'phone_number', 'first_name', 'last_name', 'is_staff', 'date_joined']
    search_fields = ['username', 'CIN', 'phone_number']
    list_filter = ['is_staff', 'date_joined']
    actions = ['calculate_and_save_score']
    # inlines = [
    #     EngagementClientInline,
    #     ComportementClientInline,
    #     EngagementTopnetInline,
    #     ValeurCommercialeInline,
    # ]
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
    

class AxesAdmin(admin.ModelAdmin):
    raw_id_fields = ['valeur_commerciale', 'engagement_topnet', 'engagement_client', 'comportement_client']
    exclude = ['categorie_client', 'engagement_contractuel', 'offre', 'debit']

    list_display = ['id','client', 'valeur_commerciale_display',
                    'engagement_topnet_display',
                    'engagement_client_display', 
                    'comportement_client_display','calculate_total_score','get_score_level','decision']

    def valeur_commerciale_display(self, obj):
        return str(obj.valeur_commerciale) if obj.valeur_commerciale else '-'

    def engagement_topnet_display(self, obj):
        return str(obj.engagement_topnet) if obj.engagement_topnet else '-'

    def engagement_client_display(self, obj):
        return str(obj.engagement_client) if obj.engagement_client else '-'

    def comportement_client_display(self, obj):
        return str(obj.comportement_client) if obj.comportement_client else '-'





    def calculate_total_score(self, obj):
        score_valeur_commerciale = obj.valeur_commerciale.calculate_total_score()
        score_engagement_topnet = obj.engagement_topnet.calculate_total_score()
        score_engagement_client = obj.engagement_client.calculate_total_score()
        score_comportement_client = obj.comportement_client.calculate_total_score()

        total_score = (score_valeur_commerciale + score_engagement_topnet + score_engagement_client + score_comportement_client)
        return total_score

    calculate_total_score.short_description = 'Total Score'
    def get_score_level(self, obj):
        try:
            total_score = self.calculate_total_score(obj)
            if isinstance(total_score, tuple):
                total_score = total_score[0]

            if total_score <= 20:
                return "Niveau 4: Signaux clairs de failles."
            elif total_score <= 40:
                return "Niveau 3: Quelques alertes ont été remontées."
            elif total_score <= 70:
                return "Niveau 2: Bonne santé dans l'ensemble."
            else:
                return "Niveau 1: Excellente santé financière."
        except Exception as e:
            return f"Error: {str(e)}"

    get_score_level.short_description = 'Score Level'

    def decision(self, obj):
        total_score_str = self.calculate_total_score(obj)

        try:
            total_score = float(total_score_str)
        except ValueError:
            return "N/A"  # If the score is not a valid number, return "N/A"

        if total_score <= 20:
            return "Risque avéré."
        elif total_score <= 40:
            return "Risque probable."
        elif total_score <= 70:
            return "Risque limité."
        else:
            return "Risque très peu probable."

    decision.short_description = 'Decision'


class AxesWeightAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # Add this line to display the ID
        'valeur_commerciale_weight',
        'engagement_topnet_weight',
        'engagement_client_weight',
        'comportement_client_weight',
        'calculate_total_weight',
        'is_active',
    )
    list_editable = ['is_active'] 
    def calculate_total_weight(self, obj):
        return obj.calculate_total_weight()
    calculate_total_weight.short_description = 'Total Weight'


class CriteriaWeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'active_axes_weight')
    list_editable = ['active_axes_weight'] 
    fieldsets = (
        ('Valeur Commercial', {
            'fields': ('poids_offre', 'poids_debit', 'poids_categorie_client', 'poids_engagement_contractuel'),
        }),
        ('EngagementTopnet', {
            'fields': ('poids_nombre_reclamations', 'poids_delai_traitement'),
        }),
        ('Engagement Client', {
            'fields': ('poids_anciennete', 'poids_nombre_suspension', 'poids_montant_en_cours'),
        }),
        ('Comportement Client', {
            'fields': ('poids_delai_moyen_paiement', 'poids_incident_de_paiement', 'poids_contentieux'),
        }),
        
    )


admin.site.register(Client, ClientAdmin)
admin.site.register(ValeurCommerciale,ValeurCommercialeAdmin)
admin.site.register(ComportementClient, ComportementClientAdmin)
admin.site.register(EngagementTopnet, EngagementTopnetAdmin)
admin.site.register(EngagementClient, EngagementClientAdmin)
admin.site.register(AxesWeight , AxesWeightAdmin)
admin.site.register(CriteriaWeight, CriteriaWeightAdmin)

admin.site.register(Axes,AxesAdmin)
# admin.site.register(ScoreParameters, ScoreParametersAdmin)
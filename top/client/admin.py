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


class ScoreParametersAdmin(admin.ModelAdmin):
    list_display = ('id', 'valeur_commerciale_weight', 'engagement_client_weight', 'engagement_topnet_weight', 'comportement_client_weight')
    list_filter = ()
    search_fields = ()
    ordering = ('id',)

admin.site.register(ScoreParameters, ScoreParametersAdmin)

# class EngagementTopnetInline(admin.StackedInline):
#     model = EngagementTopnet
#     can_delete = False
#     readonly_fields = ['nombre_reclamation', 'delai_traitement']

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
    list_display = ['client', 'get_calculated_nombre_reclamations', 'get_delai_traitement']
    list_display_links = ['client']

    def get_calculated_nombre_reclamations(self, obj):
        return obj.nombre_reclamations
    get_calculated_nombre_reclamations.short_description = 'Calculated Nombre Reclamations'

    def get_delai_traitement(self, obj):
        return obj.delai_traitement
    get_delai_traitement.short_description = 'Délai de Traitement'


class ComportementClientAdmin(admin.ModelAdmin):
    list_display = ['client', 'contrat_link', 'get_date_debut', 'get_date_fin', 'get_delai_moyen_paiement', 'get_incident_de_paiement', 'get_contentieux']
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

    list_display = ['client', 'valeur_commerciale_display', 'weight_valeur_commerciale', 
                    'engagement_topnet_display', 'weight_engagement_topnet', 
                    'engagement_client_display', 'weight_engagement_client', 
                    'comportement_client_display', 'weight_comportement_client']

    def valeur_commerciale_display(self, obj):
        return str(obj.valeur_commerciale) if obj.valeur_commerciale else '-'

    def engagement_topnet_display(self, obj):
        return str(obj.engagement_topnet) if obj.engagement_topnet else '-'

    def engagement_client_display(self, obj):
        return str(obj.engagement_client) if obj.engagement_client else '-'

    def comportement_client_display(self, obj):
        return str(obj.comportement_client) if obj.comportement_client else '-'

    def get_weight_in_axes(self, obj, related_obj_name):
        try:
            related_obj = getattr(obj, related_obj_name)
            if related_obj:
                return f"Weight: {getattr(obj, f'weight_{related_obj_name}'):.2f}"
        except Axes._meta.get_field(related_obj_name).related_model.DoesNotExist:
            pass
        return '-'

    def weight_valeur_commerciale(self, obj):
        return self.get_weight_in_axes(obj, 'valeur_commerciale')

    def weight_engagement_topnet(self, obj):
        return self.get_weight_in_axes(obj, 'engagement_topnet')

    def weight_engagement_client(self, obj):
        return self.get_weight_in_axes(obj, 'engagement_client')

    def weight_comportement_client(self, obj):
        return self.get_weight_in_axes(obj, 'comportement_client')

    valeur_commerciale_display.short_description = 'Valeur Commerciale'
    engagement_topnet_display.short_description = 'Engagement Topnet'
    engagement_client_display.short_description = 'Engagement Client'
    comportement_client_display.short_description = 'Comportement Client'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Update the related objects with their corresponding Axes object and weights
        related_objects = [
            ('valeur_commerciale', obj.valeur_commerciale, 'weight_valeur_commerciale'),
            ('engagement_topnet', obj.engagement_topnet, 'weight_engagement_topnet'),
            ('engagement_client', obj.engagement_client, 'weight_engagement_client'),
            ('comportement_client', obj.comportement_client, 'weight_comportement_client'),

        ]


        for related_obj_name, related_obj, weight_field_name in related_objects:
            if related_obj:
                # Remove the existing axes_relation from the related object if it exists
                if getattr(related_obj, 'axes_relation_id', None) and getattr(related_obj, 'axes_relation_id') != obj.id:
                    setattr(related_obj, 'axes_relation', None)

                # Assign the new axes_relation and weight to the related object
                setattr(related_obj, 'axes_relation', obj)
                setattr(related_obj, 'weight', getattr(obj, weight_field_name))
                related_obj.save()

        related_objects = [form.cleaned_data.get('valeur_commerciale'),
                           form.cleaned_data.get('engagement_topnet'),
                           form.cleaned_data.get('engagement_client'),
                           form.cleaned_data.get('comportement_client')]

        for related_object in related_objects:
            if related_object:
                related_object.client = obj.client
                related_object.save()
        

class ValeurCommercialeAdmin(admin.ModelAdmin):
    list_display = ['categorie_client', 'engagement_contractuel', 'offre', 'debit', 'client', 'get_weight_from_axes']

    def get_weight_from_axes(self, obj):
        axes_queryset = Axes.objects.filter(valeur_commerciale=obj)
        if axes_queryset.exists():
            axes = axes_queryset.last()
            return axes.weight_valeur_commerciale
        return None

    get_weight_from_axes.short_description = 'Weight from Axes'

admin.site.register(EngagementTopnet, EngagementTopnetAdmin)
admin.site.register(EngagementClient, EngagementClientAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ValeurCommerciale,ValeurCommercialeAdmin)
admin.site.register(ComportementClient, ComportementClientAdmin)
admin.site.register(Axes,AxesAdmin)

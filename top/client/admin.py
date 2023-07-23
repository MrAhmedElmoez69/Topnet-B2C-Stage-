from django.contrib import admin
from .models import ScoreParameters, Client
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
    form = ClientForm

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

admin.site.register(Client, ClientAdmin)


admin.site.register(ScoreParameters)

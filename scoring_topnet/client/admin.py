from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Client

class ClientAdmin(admin.ModelAdmin):
    list_display = ['ID_Client', 'Nom', 'Prenom', 'numero_ligne', 'CIN', 'score']
    list_filter = ['score']
    search_fields = ['Nom', 'Prenom', 'CIN']

admin.site.register(Client, ClientAdmin)

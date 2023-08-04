from django.db import models
from client.models import Client  

class Contrat(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contrats') 

    id_contrat = models.AutoField(primary_key=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    #montant_en_cours = models.DecimalField(max_digits=10, decimal_places=2)
    nombre_suspension = models.PositiveIntegerField()
    nombre_facture_impayee = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Contrat {self.id_contrat} - Client: {self.client.first_name} {self.client.last_name}"
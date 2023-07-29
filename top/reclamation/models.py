from django.db import models
from django.utils import timezone
from django.conf import settings



class Reclamation(models.Model):
    contrat = models.ForeignKey('contrat.Contrat', on_delete=models.CASCADE, related_name='reclamations')
    client = models.ForeignKey('client.Client', on_delete=models.CASCADE, related_name='reclamations', null=True, blank=True, default=None)

    Id_reclamation = models.AutoField(primary_key=True)
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(default=timezone.now)
    nombre_reclamation = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"Reclamation {self.Id_reclamation} - Contrat: {self.contrat.id_contrat}"


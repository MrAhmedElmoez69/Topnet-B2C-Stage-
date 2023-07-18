from django.contrib.auth.models import User
from django.db import models

class Client(models.Model):
    ID_Client = models.AutoField(primary_key=True)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)
    numero_ligne = models.CharField(max_length=20)
    CIN = models.CharField(max_length=20)
    score = models.IntegerField(default=0)
    mot_de_passe = models.CharField(max_length=128, default='')  # Champ de mot de passe

    def __str__(self):
        return f"{self.Nom} {self.Prenom}"

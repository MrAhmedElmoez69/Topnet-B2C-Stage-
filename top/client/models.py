from django.contrib.auth.models import User
from django.db import models

class ScoreParameters(models.Model):
    criteres = models.CharField(max_length=100)
    poids = models.DecimalField(max_digits=5, decimal_places=2)
    objectif = models.DecimalField(max_digits=5, decimal_places=2)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    score_parameters = models.ManyToManyField(ScoreParameters)
    # Ajouter d'autres champs spécifiques au client ici, si nécessaire

def calculate_score(client):
    score_parameters = client.score_parameters.all()
    total_weight = sum(param.poids for param in score_parameters)
    score = sum((param.objectif / total_weight) * param.poids for param in score_parameters)
    return score
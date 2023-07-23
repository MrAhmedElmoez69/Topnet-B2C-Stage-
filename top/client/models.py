from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator,MaxLengthValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django import forms


class ScoreParameters(models.Model):
    CRITERES_CHOICES = [
        ('valeur_commerciale', 'Valeur Commerciale'),
        ('engagement_client', 'Engagement Client'),
        ('engagement_topnet', 'Engagement Topnet'),
        ('comportement_client', 'Comportement Client'),
    ]

    # Add a default choice to represent "unspecified" option
    CATEGORIE_CHOICES = [
        (None, 'Unspecified'),
        (0, 'Standard'),
        (1, 'VIP'),
    ]

    # Add a default choice to represent "unspecified" option
    ENGAGEMENT_CHOICES = [
        (None, 'Unspecified'),
        (0, 'Engagé'),
        (1, 'Non Engagé'),
    ]

    # Add a default choice to represent "unspecified" option
    OFFRE_CHOICES = [
        (None, 'Unspecified'),
        (0.5, 'XDSL'),
        (1, 'HD'),
    ]

    # Add a default choice to represent "unspecified" option
    DEBIT_CHOICES = [
        (None, 'Unspecified'),
        (100, 1),
        (50, 0.9),
        (30, 0.8),
        (20, 0.7),
        (12, 0.6),
        (10, 0.4),
        (8, 0.2),
        (4, 0),
    ]

    criteres = models.CharField(max_length=100, choices=CRITERES_CHOICES)
    poids = models.DecimalField(max_digits=5, decimal_places=2)
    objectif = models.DecimalField(max_digits=5, decimal_places=2)

    categorie_client = models.IntegerField(choices=CATEGORIE_CHOICES, default=None, null=True, blank=True)
    engagement_contractuel = models.IntegerField(choices=ENGAGEMENT_CHOICES, default=None, null=True, blank=True)
    offre = models.DecimalField(choices=OFFRE_CHOICES, max_digits=3, decimal_places=1, default=None, null=True, blank=True)
    debit = models.PositiveIntegerField(choices=DEBIT_CHOICES, default=None, null=True, blank=True)



class Client(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+216 \d{2} \d{3} \d{3}$',
        message="Le numéro de téléphone doit être au format +216 00 000 000."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    CIN = models.CharField("CIN", max_length=250, validators=[RegexValidator(regex='^[0-9]{8}$', message="Numbers Only!")])

    score_parameters = models.ManyToManyField(ScoreParameters)

    def calculate_score(self):
        score_parameters = self.score_parameters.all()
        total_weight = sum(param.poids for param in score_parameters)
        score = sum((param.objectif / total_weight) * param.poids for param in score_parameters)
        return score

    def calculate_niveau_classe(self):
        # Define the mapping of total scores to niveau/classe
        niveau_classe_mapping = {
            (0, 20): 'classe 4. Signaux clairs de failles. Risque avéré.',
            (21, 40): 'niveau 3. Quelques alertes ont été remontées. Risque probable.',
            (41, 70): 'niveau 2. Bonne santé dans l’ensemble. Risque limité.',
            (71, 100): 'niveau 1. Excellente santé financière. Risque très peu probable.',
        }
        total_score = self.calculate_score()
        for (lower, upper), niveau_classe in niveau_classe_mapping.items():
            if lower <= total_score <= upper:
                return niveau_classe
        return 'Niveau indéterminé'
    

def calculate_score(client):
    score_parameters = client.score_parameters.all()
    total_weight = sum(param.poids for param in score_parameters)
    score = sum((param.objectif / total_weight) * param.poids for param in score_parameters)
    return score



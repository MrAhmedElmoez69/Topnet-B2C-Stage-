from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator,MaxLengthValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django import forms


class ScoreParameters(models.Model):
    criteres = models.CharField(max_length=100)
    poids = models.DecimalField(max_digits=5, decimal_places=2)
    objectif = models.DecimalField(max_digits=5, decimal_places=2)

class Client(AbstractUser):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')

        # Your fields for the Agent model go here
    phone_regex = RegexValidator(
        regex=r'^\+216 \d{2} \d{3} \d{3}$',
        message="Le numéro de téléphone doit être au format +216 00 000 000."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)  # Ajouter d'autres champs spécifiques au client ici, si nécessaire
    CIN =models.CharField("CIN",max_length=250,validators= [RegexValidator(regex='^[0-9]{8}$',message="Numbers Only !")])

    score_parameters = models.ManyToManyField(ScoreParameters)
  
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='agent_set'  # Change 'agent_set' to a unique related_name
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='agent_set'  # Change 'agent_set' to a unique related_name
    )
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

def calculate_score(client):
    score_parameters = client.score_parameters.all()
    total_weight = sum(param.poids for param in score_parameters)
    score = sum((param.objectif / total_weight) * param.poids for param in score_parameters)
    return score



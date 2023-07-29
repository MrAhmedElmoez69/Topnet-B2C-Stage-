from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator,MaxLengthValidator
from django.contrib.auth.models import AbstractUser
from django import forms
import datetime
from reclamation.models import *
from facture.models import *
from decimal import Decimal, ROUND_HALF_UP


class Client(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\d{8}$',
        message="Le numéro de téléphone doit être au format  71000000."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    CIN = models.CharField("CIN", max_length=250, validators=[RegexValidator(regex='^[0-9]{8}$', message="Numbers Only!")])

    #score_parameters = models.ManyToManyField(ScoreParameters)

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
    ANCIENNETE_CHOICES = [
        (1, '< 1 an'),
        (2, '1 an < ancienneté < 2 ans'),
        (3, '2 ans et plus'),
    ]

    anciennete = models.IntegerField(choices=ANCIENNETE_CHOICES, default=None, null=True, blank=True)
    criteres = models.CharField(max_length=100, choices=CRITERES_CHOICES)
    poids = models.DecimalField(max_digits=5, decimal_places=2)
    objectif = models.DecimalField(max_digits=5, decimal_places=2)

    categorie_client = models.IntegerField(choices=CATEGORIE_CHOICES, default=None, null=True, blank=True)
    engagement_contractuel = models.IntegerField(choices=ENGAGEMENT_CHOICES, default=None, null=True, blank=True)
    offre = models.DecimalField(choices=OFFRE_CHOICES, max_digits=3, decimal_places=1, default=None, null=True, blank=True)
    debit = models.PositiveIntegerField(choices=DEBIT_CHOICES, default=None, null=True, blank=True)
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='score_parameters', null=True, blank=True, default=None)





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


class ValeurCommerciale(models.Model):
    CATEGORIE_CHOICES = [
        (None, 'Unspecified'),
        (0, 'Standard'),
        (1, 'VIP'),
    ]

    ENGAGEMENT_CHOICES = [
        (None, 'Unspecified'),
        (0, 'Engagé'),
        (1, 'Non Engagé'),
    ]

    OFFRE_CHOICES = [
        (None, 'Unspecified'),
        (0.5, 'XDSL'),
        (1, 'HD'),
    ]

    DEBIT_CHOICES = [
        (None, 'Unspecified'),
        (Decimal('1'), '100'),
        (Decimal('0.9'), '50'),
        (Decimal('0.8'), '30'),
        (Decimal('0.7'), '20'),
        (Decimal('0.6'), '12'),
        (Decimal('0.4'), '10'),
        (Decimal('0.2'), '8'),
        (Decimal('0'), '4'),
    ]

    categorie_client = models.IntegerField(choices=CATEGORIE_CHOICES, default=None, null=True, blank=True)
    engagement_contractuel = models.IntegerField(choices=ENGAGEMENT_CHOICES, default=None, null=True, blank=True)
    offre = models.DecimalField(choices=OFFRE_CHOICES, max_digits=3, decimal_places=1, default=None, null=True, blank=True)
    debit = models.DecimalField(choices=DEBIT_CHOICES, max_digits=2, decimal_places=1, default=None, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ValeurCommerciale', null=True, blank=True, default=None)


class EngagementClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_client', null=True, blank=True, default=None)

    def calculate_anciennete(self):
        if self.client.contrats.exists():  
            today = datetime.date.today()
            last_contrat = self.client.contrats.latest('date_debut')
            difference = today - last_contrat.date_debut
            if difference.days >= 730:
                self.anciennete = 3
            elif 365 <= difference.days < 730:
                self.anciennete = 2
            elif difference.days < 365:
                self.anciennete = 1
            else:
                self.anciennete = None

    def calculate_nombre_suspension(self):
        if self.client.contrats.exists():  
            nombre_suspension = self.client.contrats.aggregate(models.Max('nombre_suspension'))['nombre_suspension__max']
            if nombre_suspension < 2:
                self.nombre_suspension = 1
            else:
                self.nombre_suspension = 0

    def calculate_montant_en_cours(self):
        if self.client.contrats.exists(): 
            montant_en_cours = self.client.contrats.aggregate(models.Max('montant_en_cours'))['montant_en_cours__max']
            if montant_en_cours < 2:
                self.montant_en_cours = 1
            elif montant_en_cours == 0:
                self.montant_en_cours = 0
            else:
                self.montant_en_cours = 0.5

    def save(self, *args, **kwargs):
        self.calculate_anciennete()
        self.calculate_nombre_suspension()
        self.calculate_montant_en_cours()
        super().save(*args, **kwargs)

class EngagementTopnet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_topnet', null=True, blank=True, default=None)

    def calculate_nombre_reclamation(self):
        nombre_reclamation = self.client.reclamations.filter(date_debut__year=timezone.now().year).count()
        if nombre_reclamation > 4:
            self.nombre_reclamation = 1
        elif 2 < nombre_reclamation < 4:
            self.nombre_reclamation = 0.5
        else:
            self.nombre_reclamation = 0

    def calculate_delai_traitement(self):
        last_reclamation = self.client.reclamations.order_by('-date_debut').first()
        if last_reclamation:
            delai_traitement = (timezone.now().date() - last_reclamation.date_debut).days
            if delai_traitement > 15:
                self.delai_traitement = 1
            else:
                self.delai_traitement = 0

    def save(self, *args, **kwargs):
        self.calculate_nombre_reclamation()
        self.calculate_delai_traitement()
        super().save(*args, **kwargs)



class ComportementClient(models.Model):
    facture = models.ForeignKey('facture.Facture', on_delete=models.CASCADE, related_name='ComportementClient', null=True, blank=True, default=None)

    def calculate_delai_moyen_paiement(self):
        if self.facture and self.facture.contrat.client.contrats.exists():  
            factures = Facture.objects.filter(contrat__in=self.facture.contrat.client.contrats.all(), date_a_payer_avant__year=datetime.date.today().year)
            delai_paiement_total = datetime.timedelta()

            for facture in factures:
                if facture.date_a_payer_avant >= facture.date_du_facture:
                    delai_paiement_total += facture.date_a_payer_avant - facture.date_du_facture

            delai_moyen_paiement = delai_paiement_total / factures.count()
            delai_theorique_paiement = datetime.timedelta(days=30)

            if delai_moyen_paiement <= delai_theorique_paiement:
                return 1
            else:
                return 0

    def incident_de_paiement(self):
        if self.facture:
            return self.facture.statut_paiement == Facture.REJET
        return False 

    def contentieux(self):
        return "True" if self.facture and self.facture.contentieux else "False"
    
    def __str__(self):
        if self.facture and self.facture.client:
            return f"Client: {self.facture.client.username} - Facture {self.facture.Id_facture}"
        return f"Facture {self.facture.Id_facture} - No Client"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
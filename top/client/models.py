from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator,MaxLengthValidator
from django.contrib.auth.models import AbstractUser
from django import forms
import datetime
from reclamation.models import *
from facture.models import *
from decimal import Decimal, ROUND_HALF_UP
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
class ScoreParameters(models.Model):
    valeur_commerciale_weight = models.PositiveIntegerField(
        default=25,
        validators=[
            MinValueValidator(0, message=_("Weight should be at least 0.")),
            MaxValueValidator(100, message=_("Weight cannot exceed 100.")),
        ],
        help_text=_("Weight for Valeur Commerciale in percentage."),
    )
    engagement_client_weight = models.PositiveIntegerField(
        default=25,
        validators=[
            MinValueValidator(0, message=_("Weight should be at least 0.")),
            MaxValueValidator(100, message=_("Weight cannot exceed 100.")),
        ],
        help_text=_("Weight for Engagement Client in percentage."),
    )
    engagement_topnet_weight = models.PositiveIntegerField(
        default=25,
        validators=[
            MinValueValidator(0, message=_("Weight should be at least 0.")),
            MaxValueValidator(100, message=_("Weight cannot exceed 100.")),
        ],
        help_text=_("Weight for Engagement Topnet in percentage."),
    )
    comportement_client_weight = models.PositiveIntegerField(
        default=25,
        validators=[
            MinValueValidator(0, message=_("Weight should be at least 0.")),
            MaxValueValidator(100, message=_("Weight cannot exceed 100.")),
        ],
        help_text=_("Weight for Comportement Client in percentage."),
    )

    def save(self, *args, **kwargs):
        if self.valeur_commerciale_weight + self.engagement_client_weight + self.engagement_topnet_weight + self.comportement_client_weight != 100:
            raise ValueError("The total of all weights must be equal to 100.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Score Axes Weights"

    class Meta:
        verbose_name_plural = "Calculate Score Axes"
class Client(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\d{8}$',
        message="Le numéro de téléphone doit être au format  71000000."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    CIN = models.CharField("CIN", max_length=250, validators=[RegexValidator(regex='^[0-9]{8}$', message="Numbers Only!")])
    score_parameters = models.ForeignKey(
        ScoreParameters,
        on_delete=models.CASCADE,
        related_name='client_score_parameters',
        null=True,
        blank=True
    )
    #score_parameters = models.ManyToManyField(ScoreParameters)
# Choices for the axes
class AxisChoices(models.TextChoices):
    VALEUR_COMMERCIALE = 'ValeurCommerciale', _('Valeur Commerciale')
    ENGAGEMENT_CLIENT = 'EngagementClient', _('Engagement client')
    ENGAGEMENT_TOPNET = 'EngagementTopnet', _('Engagement TOPNET')
    COMPORTEMENT_CLIENT = 'ComportementClient', _('Comportement client')




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


class EngagementTopnet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_topnet', null=True, blank=True, default=None)
    nombre_reclamations = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    delai_traitement = models.FloatField(default=0)

    def calculate_nombre_reclamations(self):
        if self.client and self.client.contrats.exists():
            current_year = timezone.now().year
            reclamations = Reclamation.objects.filter(contrat__in=self.client.contrats.all(), date_debut__year=current_year)
            nombre_reclamations_par_an = reclamations.aggregate(Sum('nombre_reclamation'))['nombre_reclamation__sum']

            if nombre_reclamations_par_an is not None:
                if nombre_reclamations_par_an > 4:
                    self.nombre_reclamations = 1
                elif 2 < nombre_reclamations_par_an <= 4:
                    self.nombre_reclamations = 0.5
                else:
                    self.nombre_reclamations = 0
            else:
                self.nombre_reclamations = 0

    def calculate_delai_traitement(self):
        if self.client and self.client.contrats.exists():
            reclamations = Reclamation.objects.filter(contrat__in=self.client.contrats.all())
            delai_traitement_total = datetime.timedelta()

            for reclamation in reclamations:
                if reclamation.date_fin >= reclamation.date_debut:
                    delai_traitement_total += reclamation.date_fin - reclamation.date_debut

            delai_moyen_traitement = delai_traitement_total / reclamations.count()
            delai_theorique_traitement = datetime.timedelta(days=15)

            if delai_moyen_traitement > delai_theorique_traitement:
                self.delai_traitement = 1
            else:
                self.delai_traitement = 0

    def save(self, *args, **kwargs):
        self.calculate_nombre_reclamations()
        self.calculate_delai_traitement()
        super().save(*args, **kwargs)
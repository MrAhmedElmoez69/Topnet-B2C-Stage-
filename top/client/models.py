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
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    def __str__(self):
            # Assuming you have a field named 'username' in the Client model
            return self.username if self.username else "N/A"
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
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='valeur_commerciale', null=True, blank=True, default=None)
    axes_relation = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='valeur_commerciale_relation', null=True, blank=True)

    poids_offre = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_debit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_categorie_client = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_engagement_contractuel = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def calculate_total_weight(self):
        total_weight = (
            self.poids_offre +
            self.poids_debit +
            self.poids_categorie_client +
            self.poids_engagement_contractuel
        )
        return total_weight
    
    def calculate_score_valeur_commerciale(self):
        axes_queryset = Axes.objects.filter(valeur_commerciale=self)
        if axes_queryset.exists():
            axes = axes_queryset.last()
            poids_valeur_commerciale = axes.weight_valeur_commerciale

            objectif_offre = (self.poids_offre / 100) * (poids_valeur_commerciale / 100)
            objectif_debit = (self.poids_debit / 100) * (poids_valeur_commerciale / 100)
            objectif_categorie = (self.poids_categorie_client / 100) * (poids_valeur_commerciale / 100)
            objectif_engagement = (self.poids_engagement_contractuel / 100) * (poids_valeur_commerciale / 100)

            score_valeur_commerciale = (objectif_offre + objectif_debit + objectif_categorie + objectif_engagement) * poids_valeur_commerciale
            return score_valeur_commerciale
        return 0

    def clean(self):
        total_weight = self.calculate_total_weight()
        if total_weight > 0 and total_weight != 100:
            raise ValidationError(
                'The total weight for this category must be equal to 100% if any weight is assigned.',
                code='invalid'
            )

    def save(self, *args, **kwargs):
        self.calculate_score_valeur_commerciale()
        self.clean()
        super().save(*args, **kwargs)

class EngagementClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_client', null=True, blank=True, default=None)
    axes_relation  = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='engagement_client_relation', null=True, blank=True)
    
    
    poids_anciennete = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_nombre_suspension = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_montant_en_cours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
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
    
    def calculate_total_weight(self):
        total_weight = (
            self.poids_nombre_suspension +
            self.poids_montant_en_cours + 
            self.poids_anciennete  
        )
        return total_weight

    def clean(self):
        total_weight = self.calculate_total_weight()
        if total_weight > 0 and total_weight != 100:
            raise ValidationError(
                'The total weight for this category must be equal to 100% if any weight is assigned.',
                code='invalid'
            )

    def save(self, *args, **kwargs):
        self.calculate_anciennete()
        self.calculate_nombre_suspension()
        self.calculate_montant_en_cours()
        self.clean()
        super().save(*args, **kwargs)

class ComportementClient(models.Model):
    facture = models.ForeignKey('facture.Facture', on_delete=models.CASCADE, related_name='ComportementClient', null=True, blank=True, default=None)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='comportement_client', null=True, blank=True, default=None)
    axes_relation = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='comportement_client_relation', null=True, blank=True)

    poids_delai_moyen_paiement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_incident_de_paiement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_contentieux = models.DecimalField(max_digits=5, decimal_places=2, default=0)    
    
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

    def calculate_total_weight(self):
        total_weight = (
            self.poids_delai_moyen_paiement +
            self.poids_incident_de_paiement + 
            self.poids_contentieux  
        )
        return total_weight

    def clean(self):
        total_weight = self.calculate_total_weight()
        if total_weight > 0 and total_weight != 100:
            raise ValidationError(
                'The total weight for this category must be equal to 100% if any weight is assigned.',
                code='invalid'
            )
        
    def save(self, *args, **kwargs):
        self.incident_de_paiement()
        self.calculate_delai_moyen_paiement()
        self.contentieux()
        self.clean()
        super().save(*args, **kwargs)

class EngagementTopnet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_topnet', null=True, blank=True, default=None)
    axes_relation = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='engagement_topnet_relation', null=True, blank=True)

    nombre_reclamations = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    delai_traitement = models.FloatField(default=0)
    poids_nombre_reclamations = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    poids_delai_traitement = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    

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

    def calculate_total_weight(self):
        total_weight = (
            self.poids_nombre_reclamations +
            self.poids_delai_traitement 
        )
        return total_weight
    
    def clean(self):
        total_weight = self.calculate_total_weight()
        if total_weight > 0 and total_weight != 100:
            raise ValidationError(
                'The total weight for this category must be equal to 100% if any weight is assigned.',
                code='invalid'
            )
        
    def save(self, *args, **kwargs):
        self.calculate_nombre_reclamations()
        self.calculate_delai_traitement()
        self.clean()
        super().save(*args, **kwargs)

class Axes(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='Axes')
    valeur_commerciale = models.ForeignKey(ValeurCommerciale, on_delete=models.CASCADE, null=True, blank=True)
    engagement_topnet = models.ForeignKey(EngagementTopnet, on_delete=models.CASCADE, null=True, blank=True)
    engagement_client = models.ForeignKey(EngagementClient, on_delete=models.CASCADE, null=True, blank=True)
    comportement_client = models.ForeignKey(ComportementClient, on_delete=models.CASCADE, null=True, blank=True)
    # Weight fields for each category
    weight_valeur_commerciale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weight_engagement_topnet = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weight_engagement_client = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weight_comportement_client = models.DecimalField(max_digits=5, decimal_places=2, default=0)


    def clean(self):
        total_weight = self.weight_valeur_commerciale + self.weight_engagement_topnet + self.weight_engagement_client + self.weight_comportement_client

        if total_weight != 100:
            raise ValidationError(
                _('The total weight must be equal to 100%.'),
                code='invalid'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)





@receiver(post_save, sender=ValeurCommerciale)
@receiver(post_save, sender=EngagementTopnet)
@receiver(post_save, sender=EngagementClient)
@receiver(post_save, sender=ComportementClient)
def update_axes_on_related_model_save(sender, instance, **kwargs):
    # Get the related Axes object for the client
    axes = Axes.objects.filter(client=instance.client).first()

    if axes:
        # Update the related field in Axes based on the instance's type
        if isinstance(instance, ValeurCommerciale):
            axes.valeur_commerciale = instance
        elif isinstance(instance, EngagementTopnet):
            axes.engagement_topnet = instance
        elif isinstance(instance, EngagementClient):
            axes.engagement_client = instance
        elif isinstance(instance, ComportementClient):
            axes.comportement_client = instance

        axes.save()
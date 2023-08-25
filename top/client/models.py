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
import random
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

    def calculate_score_categorie_client(self):
        poids_categorie_client = CriteriaWeight.objects.get(active_axes_weight=True).poids_categorie_client
        valeur_commerciale_weight = AxesWeight.objects.get(is_active=True).valeur_commerciale_weight

        # Convert categorie_client to a Decimal before performing multiplication
        categorie_client_decimal = Decimal(str(self.categorie_client))

        return categorie_client_decimal * (poids_categorie_client * valeur_commerciale_weight) / Decimal('100')

    def calculate_score_debit(self):
        poids_debit = CriteriaWeight.objects.get(active_axes_weight=True).poids_debit
        valeur_commerciale_weight = AxesWeight.objects.get(is_active=True).valeur_commerciale_weight
        debit_decimal = Decimal(str(self.categorie_client))

        return debit_decimal * (poids_debit * valeur_commerciale_weight) / Decimal('100')

    def calculate_score_offre(self):
        poids_offre = CriteriaWeight.objects.get(active_axes_weight=True).poids_offre
        valeur_commerciale_weight = AxesWeight.objects.get(is_active=True).valeur_commerciale_weight
        offre_decimal = Decimal(str(self.categorie_client))

        return offre_decimal * (poids_offre * valeur_commerciale_weight) / Decimal('100')

    def calculate_score_engagement_contractuel(self):
        poids_engagement_contractuel = CriteriaWeight.objects.get(active_axes_weight=True).poids_engagement_contractuel
        valeur_commerciale_weight = AxesWeight.objects.get(is_active=True).valeur_commerciale_weight
        engagement_contractuel_decimal = Decimal(str(self.categorie_client))
        
        return engagement_contractuel_decimal * (poids_engagement_contractuel * valeur_commerciale_weight) / Decimal('100')
    
    def calculate_total_score(self):
        poids_categorie_client = Decimal(str(CriteriaWeight.objects.get(active_axes_weight=True).poids_categorie_client))
        poids_debit = Decimal(str(CriteriaWeight.objects.get(active_axes_weight=True).poids_debit))
        poids_offre = Decimal(str(CriteriaWeight.objects.get(active_axes_weight=True).poids_offre))
        poids_engagement_contractuel = Decimal(str(CriteriaWeight.objects.get(active_axes_weight=True).poids_engagement_contractuel))
        valeur_commerciale_weight = Decimal(str(AxesWeight.objects.get(is_active=True).valeur_commerciale_weight))

        # Convert fields to Decimal before performing multiplication
        categorie_client_decimal = Decimal(str(self.categorie_client))
        debit_decimal = Decimal(str(self.debit))
        offre_decimal = Decimal(str(self.offre))
        engagement_contractuel_decimal = Decimal(str(self.engagement_contractuel))

        score_categorie_client = categorie_client_decimal * (poids_categorie_client * valeur_commerciale_weight) / Decimal('100')
        score_debit = debit_decimal * (poids_debit * valeur_commerciale_weight) / Decimal('100')
        score_offre = offre_decimal * (poids_offre * valeur_commerciale_weight) / Decimal('100')
        score_engagement_contractuel = engagement_contractuel_decimal * (poids_engagement_contractuel * valeur_commerciale_weight) / Decimal('100')

        total_score = score_categorie_client + score_debit + score_offre + score_engagement_contractuel
        return total_score


    def save(self, *args, **kwargs):
        self.calculate_score_categorie_client()
        self.calculate_score_debit()
        self.calculate_score_offre()
        self.calculate_score_engagement_contractuel()
        self.total_score = self.calculate_total_score()
        super().save(*args, **kwargs)

class EngagementClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_client', null=True, blank=True, default=None)
    axes_relation  = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='engagement_client_relation', null=True, blank=True)
    
    def calculate_anciennete(self):
        if self.client.contrats.exists():  
            today = datetime.date.today()
            last_contrat = self.client.contrats.latest('date_debut')
            difference = today - last_contrat.date_debut
            if difference.days >= 730:
                return Decimal('1')
            elif 365 <= difference.days < 730:
                return Decimal('0.5')
        return Decimal('0')


    def calculate_nombre_suspension(self):
        if self.client.contrats.exists():
            random_number = Decimal(str(random.randint(1, 1)))
            return random_number
        return None


    def calculate_montant_en_cours(self):
        if self.client.contrats.exists(): 
            nombre_facture_impayee = self.client.contrats.aggregate(models.Sum('nombre_facture_impayee'))['nombre_facture_impayee__sum']
            if nombre_facture_impayee is None:
                nombre_facture_impayee = 0

            if nombre_facture_impayee > 2:
                return Decimal('1')
            elif nombre_facture_impayee == 0:
                return Decimal('0')
            else:
                return Decimal('0.5')
        return None


    def calculate_anciennete_score(self):
        poids_anciennete = CriteriaWeight.objects.get(active_axes_weight=True).poids_anciennete
        engagement_client_weight = AxesWeight.objects.get(is_active=True).engagement_client_weight

        if self.anciennete is not None:
            anciennete_score = self.anciennete * (poids_anciennete * engagement_client_weight) / 100
        else:
            anciennete_score = 0

        return anciennete_score

    def calculate_nombre_suspension_score(self):
        poids_nombre_suspension = CriteriaWeight.objects.get(active_axes_weight=True).poids_nombre_suspension
        engagement_client_weight = AxesWeight.objects.get(is_active=True).engagement_client_weight

        if self.nombre_suspension is not None:
            nombre_suspension_score = self.nombre_suspension * (poids_nombre_suspension * engagement_client_weight) / 100
        else:
            nombre_suspension_score = 0

        return nombre_suspension_score

    def calculate_montant_en_cours_score(self):
        poids_montant_en_cours = CriteriaWeight.objects.get(active_axes_weight=True).poids_montant_en_cours
        engagement_client_weight = AxesWeight.objects.get(is_active=True).engagement_client_weight

        if self.montant_en_cours is not None:
            montant_en_cours_score = self.montant_en_cours * (poids_montant_en_cours * engagement_client_weight) / 100
        else:
            montant_en_cours_score = 0

        return montant_en_cours_score

    def calculate_total_score(self):
        poids_anciennete = CriteriaWeight.objects.get(active_axes_weight=True).poids_anciennete
        poids_nombre_suspension = CriteriaWeight.objects.get(active_axes_weight=True).poids_nombre_suspension
        poids_montant_en_cours = CriteriaWeight.objects.get(active_axes_weight=True).poids_montant_en_cours
        engagement_client_weight = AxesWeight.objects.get(is_active=True).engagement_topnet_weight  


        anciennete_score = self.calculate_anciennete() * (poids_anciennete * engagement_client_weight) / 100

        nombre_suspension_score = self.calculate_nombre_suspension() * (poids_nombre_suspension * engagement_client_weight) / 100

        montant_en_cours_score = self.calculate_montant_en_cours() * (poids_montant_en_cours * engagement_client_weight) / 100

        total_score = anciennete_score + nombre_suspension_score + montant_en_cours_score
        return total_score
        return total_score

    def save(self, *args, **kwargs):
        self.anciennete = self.calculate_anciennete()
        self.nombre_suspension = self.calculate_nombre_suspension()
        self.montant_en_cours = self.calculate_montant_en_cours()

        self.calculate_anciennete_score()
        self.calculate_nombre_suspension_score()
        self.calculate_montant_en_cours_score()

        self.total_score = self.calculate_total_score()
        super().save(*args, **kwargs)

class ComportementClient(models.Model):
    facture = models.ForeignKey('facture.Facture', on_delete=models.CASCADE, related_name='ComportementClient', null=True, blank=True, default=None)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='comportement_client', null=True, blank=True, default=None)
    axes_relation = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='comportement_client_relation', null=True, blank=True)

    
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
    def calculate_delai_moyen_paiement_score(self):
        poids_delai_moyen_paiement = CriteriaWeight.objects.get(active_axes_weight=True).poids_delai_moyen_paiement
        comportement_client_weight = AxesWeight.objects.get(is_active=True).comportement_client_weight

        if self.facture and self.facture.contrat.client.contrats.exists():
            factures = Facture.objects.filter(contrat__in=self.facture.contrat.client.contrats.all(), date_a_payer_avant__year=datetime.date.today().year)
            delai_paiement_total = datetime.timedelta()

            for facture in factures:
                if facture.date_a_payer_avant >= facture.date_du_facture:
                    delai_paiement_total += facture.date_a_payer_avant - facture.date_du_facture

            delai_moyen_paiement = delai_paiement_total / factures.count()
            delai_theorique_paiement = datetime.timedelta(days=30)

            if delai_moyen_paiement <= delai_theorique_paiement:
                delai_moyen_paiement_score = 1
            else:
                delai_moyen_paiement_score = 0
        else:
            delai_moyen_paiement_score = 0

        return delai_moyen_paiement_score * (poids_delai_moyen_paiement * comportement_client_weight) / 100

    def calculate_incident_de_paiement_score(self):
        poids_incident_de_paiement = CriteriaWeight.objects.get(active_axes_weight=True).poids_incident_de_paiement
        comportement_client_weight = AxesWeight.objects.get(is_active=True).comportement_client_weight

        if self.facture:
            incident_de_paiement_score = 1 if self.facture.statut_paiement == Facture.REJET else 0
        else:
            incident_de_paiement_score = 0

        return incident_de_paiement_score * (poids_incident_de_paiement * comportement_client_weight) / 100

    def calculate_contentieux_score(self):
        poids_contentieux = CriteriaWeight.objects.get(active_axes_weight=True).poids_contentieux
        comportement_client_weight = AxesWeight.objects.get(is_active=True).comportement_client_weight

        contentieux_score = 1 if self.facture and self.facture.contentieux else 0
        return contentieux_score * (poids_contentieux * comportement_client_weight) / 100

    def calculate_total_score(self):
        delai_moyen_paiement_score = self.calculate_delai_moyen_paiement_score()
        incident_de_paiement_score = self.calculate_incident_de_paiement_score()
        contentieux_score = self.calculate_contentieux_score()

        total_score = delai_moyen_paiement_score + incident_de_paiement_score + contentieux_score
        return total_score 




    def save(self, *args, **kwargs):
        self.incident_de_paiement()
        self.calculate_delai_moyen_paiement()
        self.contentieux()

        self.calculate_delai_moyen_paiement_score()
        self.calculate_incident_de_paiement_score()
        self.calculate_contentieux_score()
        self.total_score = self.calculate_total_score()
        super().save(*args, **kwargs)

class EngagementTopnet(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='engagement_topnet', null=True, blank=True, default=None)
    axes_relation = models.OneToOneField('client.Axes', on_delete=models.CASCADE, related_name='engagement_topnet_relation', null=True, blank=True)

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


    def calculate_nombre_reclamations_score(self):
        poids_nombre_reclamations = CriteriaWeight.objects.get(active_axes_weight=True).poids_nombre_suspension
        engagement_topnet_weight = AxesWeight.objects.get(is_active=True).engagement_topnet_weight

        if self.client and self.client.contrats.exists():
            current_year = timezone.now().year
            reclamations = Reclamation.objects.filter(contrat__in=self.client.contrats.all(), date_debut__year=current_year)
            nombre_reclamations_par_an = reclamations.aggregate(Sum('nombre_reclamation'))['nombre_reclamation__sum']

            if nombre_reclamations_par_an is not None:
                if nombre_reclamations_par_an > 4:
                    nombre_reclamations_score = Decimal('1')
                elif 2 < nombre_reclamations_par_an <= 4:
                    nombre_reclamations_score = Decimal('0.5')
                else:
                    nombre_reclamations_score = Decimal('0')
            else:
                nombre_reclamations_score = Decimal('0')
        else:
            nombre_reclamations_score = Decimal('0')

        return nombre_reclamations_score * (poids_nombre_reclamations * engagement_topnet_weight) / Decimal('100')

    def calculate_delai_traitement_score(self):
        poids_delai_traitement = CriteriaWeight.objects.get(active_axes_weight=True).poids_delai_traitement
        engagement_topnet_weight = AxesWeight.objects.get(is_active=True).engagement_topnet_weight

        if self.client and self.client.contrats.exists():
            reclamations = Reclamation.objects.filter(contrat__in=self.client.contrats.all())
            delai_traitement_total = datetime.timedelta()

            for reclamation in reclamations:
                if reclamation.date_fin >= reclamation.date_debut:
                    delai_traitement_total += reclamation.date_fin - reclamation.date_debut

            delai_moyen_traitement = delai_traitement_total / reclamations.count()
            delai_theorique_traitement = datetime.timedelta(days=15)

            if delai_moyen_traitement > delai_theorique_traitement:
                delai_traitement_score = Decimal('1')
            else:
                delai_traitement_score = Decimal('0')
        else:
            delai_traitement_score = Decimal('0')

        return delai_traitement_score * (poids_delai_traitement * engagement_topnet_weight) / Decimal('100')

    def calculate_total_score(self):
        nombre_reclamations_score = self.calculate_nombre_reclamations_score()
        delai_traitement_score = self.calculate_delai_traitement_score()

        total_score = nombre_reclamations_score + delai_traitement_score
        return total_score


    def save(self, *args, **kwargs):
        self.calculate_nombre_reclamations()
        self.calculate_delai_traitement()
    
        self.calculate_nombre_reclamations_score()
        self.calculate_delai_traitement_score()
        self.total_score = self.calculate_total_score()
        super().save(*args, **kwargs)


class Axes(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='Axes')
    valeur_commerciale = models.ForeignKey(ValeurCommerciale, on_delete=models.CASCADE, null=True, blank=True)
    engagement_topnet = models.ForeignKey(EngagementTopnet, on_delete=models.CASCADE, null=True, blank=True)
    engagement_client = models.ForeignKey(EngagementClient, on_delete=models.CASCADE, null=True, blank=True)
    comportement_client = models.ForeignKey(ComportementClient, on_delete=models.CASCADE, null=True, blank=True)


class AxesWeight(models.Model):
    valeur_commerciale_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    engagement_topnet_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    engagement_client_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    comportement_client_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=False)
    def calculate_total_weight(self):
        total_weight = (
            self.valeur_commerciale_weight +
            self.engagement_topnet_weight +
            self.engagement_client_weight +
            self.comportement_client_weight
        )
        return total_weight

    def clean(self):
        total_weight = self.calculate_total_weight()

        if total_weight != 100:
            raise ValidationError(
                'The total weight for axes must be equal to 100%.',
                code='invalid'
            )

    def save(self, *args, **kwargs):
        if self.is_active:
            AxesWeight.objects.exclude(pk=self.pk).update(is_active=False)
        self.calculate_total_weight()
        self.clean()
        super().save(*args, **kwargs)


class CriteriaWeight(models.Model):
    poids_offre = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_debit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_categorie_client = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_engagement_contractuel = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    poids_anciennete = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_nombre_suspension = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_montant_en_cours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    poids_delai_moyen_paiement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_incident_de_paiement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_contentieux = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    poids_nombre_reclamations = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    poids_delai_traitement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    active_axes_weight = models.BooleanField(default=False)

    def calculate_total_weight_valeur_commerciale(self):
        total_valeur_commerciale= (
            self.poids_offre + self.poids_debit +
            self.poids_categorie_client + self.poids_engagement_contractuel
        )
        return total_valeur_commerciale

    def calculate_total_weight_engagement_client(self):
        total_weight_engagement_client = (
            self.poids_anciennete + self.poids_nombre_suspension +
            self.poids_montant_en_cours
        )
        return total_weight_engagement_client

    def calculate_total_weight_comportement_client(self):
        total_weight_comportement_client = (
            self.poids_delai_moyen_paiement +
            self.poids_incident_de_paiement +
            self.poids_contentieux
        )
        return total_weight_comportement_client
    
    def calculate_total_weight_engagement_topnet(self):
        total_weight_engagement_topnet = (
            self.poids_nombre_reclamations +
            self.poids_delai_traitement 
        )
        return total_weight_engagement_topnet

    def clean(self):
        total_weight_vc = self.calculate_total_weight_valeur_commerciale()
        total_weight_ec = self.calculate_total_weight_engagement_client()
        total_weight_cc = self.calculate_total_weight_comportement_client()
        total_weight_et = self.calculate_total_weight_engagement_topnet()

        if total_weight_vc != 100:
            raise ValidationError(
                'The total weight for criteria must be equal to 100%.',
                code='invalid'
            )

        if total_weight_ec != 100:
            raise ValidationError(
                'The total weight for criteria must be equal to 100%.',
                code='invalid'
            )

        if total_weight_cc != 100:
            raise ValidationError(
                'The total weight for criteria must be equal to 100%.',
                code='invalid'
            )
        if total_weight_et != 100:
            raise ValidationError(
                'The total weight for criteria must be equal to 100%.',
                code='invalid'
            )


    def save(self, *args, **kwargs):
        if self.active_axes_weight:
            CriteriaWeight.objects.exclude(pk=self.pk).update(active_axes_weight=False) 
        self.clean()
        super().save(*args, **kwargs)




@receiver(post_save, sender=ValeurCommerciale)
@receiver(post_save, sender=EngagementTopnet)
@receiver(post_save, sender=EngagementClient)
@receiver(post_save, sender=ComportementClient)
def update_axes_on_related_model_save(sender, instance, **kwargs):
    axes = Axes.objects.filter(client=instance.client).first()

    if axes:
        if isinstance(instance, ValeurCommerciale):
            axes.valeur_commerciale = instance
        elif isinstance(instance, EngagementTopnet):
            axes.engagement_topnet = instance
        elif isinstance(instance, EngagementClient):
            axes.engagement_client = instance
        elif isinstance(instance, ComportementClient):
            axes.comportement_client = instance

        axes.save()
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_date_a_payer_avant(value):
    today = timezone.now().date()
    max_allowed_date = today + timezone.timedelta(days=10)
    if value > max_allowed_date:
        raise ValidationError("La date ne doit pas dépasser 10 jours à partir d'aujourd'hui.")

class Facture(models.Model):
    client = models.ForeignKey('client.Client', on_delete=models.CASCADE, related_name='factures', null=True, blank=True, default=None)
    contrat = models.ForeignKey('contrat.Contrat', on_delete=models.CASCADE, related_name='factures')
    Id_facture = models.AutoField(primary_key=True)
    montant_encours = models.DecimalField(max_digits=10, decimal_places=2, help_text="Montant en Dinar Tunisien")

    ESPECE = 'Espece'
    CREDIT_CARD = 'CreditCard'
    CHEQUE = 'Cheque'
    TYPE_PAIEMENT_CHOICES = [
        (ESPECE, 'Espece'),
        (CREDIT_CARD, 'Credit Card'),
        (CHEQUE, 'Cheque'),
    ]
    type_paiement = models.CharField(max_length=100, choices=TYPE_PAIEMENT_CHOICES)
    
    date_du_facture = models.DateField(default=timezone.now)
    date_a_payer_avant = models.DateField(validators=[validate_date_a_payer_avant])

    REJET = 'rejet'
    NON = 'non'
    STATUT_PAIEMENT_CHOICES = [
        (REJET, 'Rejet'),
        (NON, 'Non'),
    ]
    statut_paiement = models.CharField(max_length=10, choices=STATUT_PAIEMENT_CHOICES, default=NON)


    CONTENTIEUX_CHOICES = [
        (False, 1), 
        (True, 0),    
    ]
    contentieux = models.BooleanField(default=False, choices=CONTENTIEUX_CHOICES)    

    def __str__(self):
        return f"Facture {self.Id_facture} - Contrat: {self.contrat.id_contrat} - Continu: {self.contentieux}"

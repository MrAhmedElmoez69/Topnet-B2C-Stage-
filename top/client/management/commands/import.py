import pandas as pd
from django.core.management.base import BaseCommand
from client.models import (
    ValeurCommerciale, EngagementClient, EngagementTopnet,
    ComportementClient, AxesWeight, CriteriaWeight, Axes
)

class Command(BaseCommand):
    help = 'Import data from Excel file and fill in models'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        data_frame = pd.read_excel(file_path)

        for index, row in data_frame.iterrows():
            valeur_commerciale = ValeurCommerciale.objects.create(
                client_id=row['client_id'],

                categorie_client=row['categorie_client'],
                engagement_contractuel=row['engagement_contractuel'],
                offre=row['offre'],
                debit=row['debit'],
            )   
            criteria_weight = CriteriaWeight.objects.create(
                poids_offre=row['poids_offre'],
                poids_debit=row['poids_debit'],
                poids_categorie_client=row['poids_categorie_client'],
                poids_engagement_contractuel=row['poids_engagement_contractuel'],

                poids_anciennete=row['poids_anciennete'],
                poids_nombre_suspension=row['poids_nombre_suspension'],
                poids_montant_en_cours=row['poids_montant_en_cours'],

                poids_delai_moyen_paiement=row['poids_delai_moyen_paiement'],
                poids_incident_de_paiement=row['poids_incident_de_paiement'],

                poids_contentieux=row['poids_contentieux'],
                poids_nombre_reclamations=row['poids_nombre_reclamations'],
                poids_delai_traitement=row['poids_delai_traitement'],
            )
            axes_weight = AxesWeight.objects.create(
                valeur_commerciale_weight=row['valeur_commerciale_weight'],
                engagement_topnet_weight=row['engagement_topnet_weight'],
                engagement_client_weight=row['engagement_client_weight'],
                comportement_client_weight=row['comportement_client_weight'],
            )
            engagement_topnet = EngagementTopnet.objects.create(
                client_id=row['client_id'],
                nombre_reclamations=row['nombre_reclamations'],
                delai_traitement=row['delai_traitement'],
            )
            engagement_client = EngagementClient.objects.create(
                client_id=row['client_id'],
            )
            comportement_client = ComportementClient.objects.create(
                facture_id=row['facture_id'],
                client_id=row['client_id'],
            )
      
            axes = Axes.objects.create(
                client_id=row['client_id'],
                
                engagement_topnet=engagement_topnet,
                engagement_client=engagement_client,
                comportement_client=comportement_client,
                valeur_commerciale=valeur_commerciale,
            )            




        self.stdout.write(self.style.SUCCESS('Data import completed successfully.'))
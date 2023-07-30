import pandas as pd
from django.core.management.base import BaseCommand
from client.models import ValeurCommerciale, Client

class Command(BaseCommand):
    help = 'Import data from Excel file and fill in ValeurCommerciale table'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        data_frame = pd.read_excel(file_path)

        for index, row in data_frame.iterrows():
            client_name = row['client_id']
            try:
                client, created = Client.objects.get_or_create(username=client_name)
                ValeurCommerciale.objects.create(
                    categorie_client=row['categorie_client'],
                    engagement_contractuel=row['engagement_contractuel'],
                    offre=row['offre'],
                    debit=row['debit'],
                    client=client,
                )
            except Client.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Client with name '{client_name}' does not exist. Skipping entry."))

        self.stdout.write(self.style.SUCCESS('Data import completed successfully.'))

import os
import pandas as pd
from django.core.management.base import BaseCommand
from client.models import Client  # Make sure to import your 'Client' model

class Command(BaseCommand):
    help = 'Import clients from Excel file'

    def handle(self, *args, **options):
        base_dir = 'C:\\Topnet-B2C-Stage-\\top\\client\\management'  # Update the base directory
        excel_file = os.path.join(base_dir, 'test.xlsx')  # Use 'test.xlsx' as the Excel file name

        try:
            df = pd.read_excel(excel_file)
            for index, row in df.iterrows():
                Client.objects.create(
                    username=row['username'],
                    CIN=row['CIN'],
                    phone_number=row['phone_number'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                )
            self.stdout.write(self.style.SUCCESS('Successfully imported clients'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing clients: {e}'))

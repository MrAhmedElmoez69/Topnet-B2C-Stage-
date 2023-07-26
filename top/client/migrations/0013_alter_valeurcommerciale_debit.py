# Generated by Django 4.2.3 on 2023-07-26 13:04

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0012_remove_comportementclient_client_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valeurcommerciale',
            name='debit',
            field=models.DecimalField(blank=True, choices=[(None, 'Unspecified'), (Decimal('1'), '100'), (Decimal('0.9'), '50'), (Decimal('0.8'), '30'), (Decimal('0.7'), '20'), (Decimal('0.6'), '12'), (Decimal('0.4'), '10'), (Decimal('0.2'), '8'), (Decimal('0'), '4')], decimal_places=1, default=None, max_digits=2, null=True),
        ),
    ]
